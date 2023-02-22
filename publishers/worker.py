import logging
import time
import MySQLdb
from MySQLdb.cursors import DictCursor
from celery import Celery
from celery.result import AsyncResult


class Worker:
    db_conn = None
    db_cur = None
    def __init__(self, host_config):
        self.config= host_config
        self.app = Celery('ga-chain', broker='amqp://guest:guest@localhost:5672/', backend='redis://localhost')
        self.add_logger()

    def add_logger(self):
        self.logger = logging.getLogger(__name__)

    def connect_to_db(self, try_num=1):
        if try_num > 5:
            error = "Could not connect to MySQL, even after several retries"
            self.logger.error(error)
            raise ValueError(error)
        if self.db_conn or self.db_cur:
            try:
                self.db_cur.close()
            except:
                pass
            try:
                self.db_conn.close()
            except:
                pass
        try:
            conn = MySQLdb.connect(host=self.config["db"]["hostname"],
                                   user=self.config["db"]["username"],
                                   passwd=self.config["db"]["password"],
                                   port=self.config["db"].get("port") or 3306,
                                   connect_timeout=10)
        except MySQLdb.OperationalError:
            self.logger.warning("OperationalError while connecting to database. Retrying (%d).." % try_num)
            time.sleep(1)
            return self.connect_to_db(try_num+1)
        except Exception as e:
            self.logger.warning("Exception while connecting to database. Retrying (%d).." % try_num)
            self.logger.warning(str(e))
            time.sleep(1)
            return self.connect_to_db(try_num+1)
        # We're disabling autocommit, but the "commit" flag in the mysql_execute* functions are set to True by default. So by default, after every execute will be a commit, except specified otherwise.
        # conn.autocommit(True)
        cur = conn.cursor(DictCursor)
        # Set conn and cur to use by mysql_execute
        self.db_conn = conn
        self.db_cur = cur
        # And change to current DB
        self.mysql_execute('USE ga_chain')


    def mysql_execute(self, operation, params=None, multi=False, try_num=1, commit=True):
        if try_num == 1:
            self.start_time = time.time()
        if not (self.db_conn or self.db_cur) or try_num == 2 or try_num == 4:
            self.connect_to_db()
        if try_num > 5:
            error = "Could not do SQL query (%s, params: %s) after 5 tries. Giving up" % (operation[:200], str(params)[:200])
            self.logger.error(error)
            # Try to exit cleanly if possible
            try:
                self.db_cur.close()
            except:
                pass
            try:
                self.db_conn.close()
            except:
                pass
            raise ValueError(error)
        try:
            ret = self.db_cur.execute(operation, params)
            self.logger.debug("mysql_execute took %.3fs." % (time.time() - self.start_time))
            if commit:
                self.db_conn.commit()
            return ret # row_count
        except Exception as e:
            self.logger.exception("Error during cur.execute() for sql %s and sql param %s . Retrying (%d. try)" % (str(operation), str(params),try_num))
            self.logger.warning(str(e))
            time.sleep(0.2)
            return self.mysql_execute(operation, params, multi, try_num+1)
    
    def update_task_progress(self, tasks_pointer):
        done_tasks_idx = []
        # print(f'current running tasks: {len(tasks_pointer)}')
        for idx, task in enumerate(tasks_pointer):
            task_id = task.task_id
            status = self.app(task_id)
            is_done = status.ready()
            if is_done:
                done_tasks_idx.append(idx)
        # cleanup
        # print(f'finished_tasks: {len(done_tasks_idx)}')
        for idx in sorted(done_tasks_idx, reverse=True):
            del self.tasks_pointer[idx]
