import time
from publishers.worker import Worker
from workers.blockCrawler import BlockCrawler



class BlockPublisher(Worker):
    last_checked = 0
    tasks_pointer = []
    threshold = 10

    def __init__(self, host_config, num=1):
        super().__init__(host_config)
        self.num = num

    def do_worker_action(self):
        while True:
            print('heartbeat block')
            # self.update_task_progress(self.tasks_pointer)
            if len(self.tasks_pointer) > self.threshold:
                time.sleep(5)
                continue
            print('checking waiting blocks')
            self.publish_block_task()
            time.sleep(5)
    
    def publish_block_task(self):
        jobs_to_pull = max(0, self.threshold - len(self.tasks_pointer))
        query = '''
            SELECT * 
            FROM block_range_tasks
            WHERE status IN ('failed', 'waiting')
            AND retry_num < 5
            ORDER BY created_at ASC
            LIMIT %s
        '''
        params = (jobs_to_pull, )
        self.mysql_execute(query, params = params, commit=False)
        tasks = self.db_cur.fetchall()
        print('blocks fetched', tasks, jobs_to_pull)
        for task in tasks:
            print(f'processing task: {task}')
            query = '''
                UPDATE block_range_tasks
                SET status = 'running'
                WHERE start_block = %s AND end_block = %s
            '''
            param = (task['start_block'], task['end_block'])
            self.mysql_execute(query, params=param)
            try:
                BlockCrawler(self.db_conn).run(task)
            except Exception as error:
                print(f'error while processing block: {error}')
            # self.tasks_pointer.append(pointer)
        print('kontoooool')
        return tasks

    def run(self):
        print("Worker started")
        try:
            self.do_worker_action()
        except KeyboardInterrupt:
            return