import time
from publishers.worker import Worker
from workers.transactionCrawler import TransactionCrawler



class transactionPublisher(Worker):
    last_checked = 0
    tasks_pointer = []
    threshold = 50

    def __init__(self, host_config, num=1):
        super().__init__(host_config)
        self.num = num

    def do_worker_action(self):
        while True:
            print('heartbeat transaction')
            self.update_task_progress(self.tasks_pointer)
            if len(self.tasks_pointer) > self.threshold:
                time.sleep(5)
                continue
            self.publish_transaction_task()
            time.sleep(5)

    def publish_transaction_task(self):
        jobs_to_pull = max(0, self.threshold - len(self.tasks_pointer))
        query = f'''
            SELECT * 
            FROM transaction_tasks
            WHERE status IN ('failed', 'waiting')
            AND retry_num < 5
            AND MOD(UNIX_TIMESTAMP(created_at), {self.num}) = 0
            ORDER BY created_at ASC
            LIMIT %s
        '''
        params = (jobs_to_pull, )
        self.mysql_execute(query, params = params, commit=False)
        tasks = self.db_cur.fetchall()
        # publish tasks to celery and store it inside tasks_pointer
        for task in tasks:
            print(task, '<<< task')
            query = '''
                UPDATE transaction_tasks
                SET status = %s
                WHERE tx_hash = %s
            '''
            param = ('running', task['tx_hash'] )
            self.mysql_execute(query, params=param)
            try:
                pointer = TransactionCrawler(self.db_conn).run(task['tx_hash'])
            except Exception as error:
                query = '''
                    UPDATE transaction_tasks
                    SET status = %s and retry_num = retry_num + 1
                    WHERE tx_hash = %s
                '''
                self.mysql_execute(query, params=('failed', task['tx_hash']))
                print(f'error while processing transaction: {error} {task}')
            # self.tasks_pointer.append(pointer)

    def run(self):
        self.logger.info("Worker started")
        try:
            self.do_worker_action()
        except KeyboardInterrupt:
            return