import time
from publishers.worker import Worker



class BlockEnqueue(Worker):
    last_checked = 0
    block_range = 100
    threshold = 2

    def __init__(self, host_config, num=1):
        super().__init__(host_config)

    def do_worker_action(self):
        while True:
            number_of_pending_tasks = self.count_pending_tasks()
            if number_of_pending_tasks > self.threshold:
                time.sleep(5)
                continue
            block_range = self.next_block_range()
            self.insert_task(block_range)
            time.sleep(5)
    
    def count_pending_tasks(self):
        query = '''
            SELECT COUNT(*) as count_pending_tasks
            FROM block_range_tasks
            WHERE status IN ('running', 'waiting')
        '''
        self.mysql_execute(query, commit=False)
        res = self.db_cur.fetchone()
        return res['count_pending_tasks']
    
    def next_block_range(self):
        fetch_latest_block_query = '''
            SELECT *
            FROM block_range_tasks
            ORDER BY start_block DESC
            LIMIT 1
        '''
        self.mysql_execute(fetch_latest_block_query, commit=False)
        latest_block_range = self.db_cur.fetchone()
        if latest_block_range is None:
            start_block = 500 * 1000
        else: start_block = latest_block_range['start_block'] + self.block_range + 1
        end_block = self.get_latest_block(start_block)
        return start_block, end_block
    
    def get_latest_block(self, start_block):
        return start_block + self.block_range

    def insert_task(self, block_range):
        print(f'creating block range {block_range}')
        query = '''
            INSERT INTO block_range_tasks
            (start_block, end_block)
            VALUES (%s, %s)
        '''
        params = (block_range[0], block_range[1])
        self.mysql_execute(query, params, commit = True)


    def run(self):
        self.logger.info("Worker started")
        try:
            self.do_worker_action()
        except KeyboardInterrupt:
            return