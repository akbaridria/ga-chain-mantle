import time
from bigQueryClient.bigQueryClient import BigQueryClient
from publishers.worker import Worker



class BQDataSync(Worker):
    max_block_size = 20

    def __init__(self, host_config, num=1):
        super().__init__(host_config)

    def do_worker_action(self):
        while True:
            transactions = self.fetch_transactions()
            log_events = self.fetch_log_events()
            bq_client = BigQueryClient()
            bq_client.connect()
            if len(transactions):
                print('syncing transaction')
                bq_client.insertIntoTransaction(transactions)
                print('transaction synced')
                self.update_tx_sent([node['tx_hash'] for node in transactions])
            if len(log_events):
                print('syncin log events')
                bq_client.insertIntoLogEvent(log_events)
                self.update_log_events_sent([(node['tx_hash'], node['idx']) for node in log_events])
            print('sync routine done')
            time.sleep(20)
    
    def fetch_transactions(self):
        query = f'''
            SELECT * 
            FROM transactions
            WHERE sent = 0
            ORDER BY timestamp 
            LIMIT {self.max_block_size}
        '''
        self.mysql_execute(query, commit=False)
        res = self.db_cur.fetchall()
        return res
    
    def fetch_log_events(self):
        query = f'''
            SELECT * 
            FROM log_events
            WHERE sent = 0
            ORDER BY created_at 
            LIMIT {self.max_block_size}
        '''
        self.mysql_execute(query, commit=False)
        res = self.db_cur.fetchall()
        return res
    
    def update_tx_sent(self, tx_hash_list):
        query = '''
            UPDATE transactions
            SET sent = 1
            WHERE tx_hash IN ({params})
        '''.format(params=', '.join(['%s'] * len(tx_hash_list)))
        self.mysql_execute(query, params=tx_hash_list, commit=True)
    
    def update_log_events_sent(self, log_event_list):
        query = f'''
        UPDATE log_events 
        SET sent = 1
        '''
        if len(log_event_list) < 1:
            return
        params = tuple()
        query += ' WHERE '
        pair = f' (tx_hash = %s AND idx = %s) '
        query_ext = []
        for node in log_event_list:
            query_ext.append(pair)
            params += node
        query_condition = ' OR '.join(query_ext)
        query += query_condition
        self.mysql_execute(query, params=params, commit=True)


    def run(self):
        self.logger.info("Worker started")
        try:
            self.do_worker_action()
        except KeyboardInterrupt:
            return