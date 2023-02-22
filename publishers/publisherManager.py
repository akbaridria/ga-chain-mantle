import multiprocessing
import logging
import time
from publishers.BQdataSync import BQDataSync

from publishers.blockEnqueue import BlockEnqueue
from publishers.blockPublisher import BlockPublisher
from publishers.transactionPublisher import transactionPublisher


class PublisherManager:

    status_worker_sleep_seconds = 30
    AVAILABLE_WORKERS = {
        'blockPublisher': BlockPublisher,
        'transactionPublisher': transactionPublisher,
        'blockEnqueue': BlockEnqueue,
        'bqSync': BQDataSync,
    }


    def __init__(self, host_config):
        self.logger = logging.getLogger(__name__)
        self.host_config = host_config
        self.processes = []

    def run_workers(self, worker, num_worker=1):

        workers = [self.AVAILABLE_WORKERS[worker]]

        # save process -> worker_type association for restarting
        proc_types = {}
        for obj_class in workers:
            for num in range(1, num_worker+1):
                obj = obj_class(self.host_config, num)
                p = multiprocessing.Process(target=obj.run, args=())
                proc_types[p] = obj
                self.processes.append(p)
        for p in self.processes:
            p.start()

        while True:
            time.sleep(self.status_worker_sleep_seconds)
            for p in self.processes:
                if not p.is_alive():
                    obj = proc_types[p]
                    self.logger.error("Process %s of type %s died. Restarting." % (str(p), str(obj)))
                    try:
                        p.join()
                    except:
                        pass
                    self.processes.remove(p)
                    new_p = multiprocessing.Process(target=obj.run, args=())
                    proc_types[new_p] = obj
                    self.processes.append(new_p)
                    new_p.start()
