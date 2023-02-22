import json
import MySQLdb
from workers.Worker import Worker
from uuid import uuid4
import requests
from dataType import transactionDT


class BlockCrawler(Worker):
    payload_template = {
        "jsonrpc": "2.0",
        "method":"eth_getBlockRange"
    }
    node_url = 'https://rpc.testnet.mantle.xyz/'
    name = 'block_crawlers'

    def __init__(self, db):
        self.config = json.load(open('config.json', 'r'))
        self.db = db
    
    # @property
    # def db(self):
    #     if self._db is None:
    #         self._db = MySQLdb.connect(host=self.config["db"]["hostname"],
    #                                user=self.config["db"]["username"],
    #                                passwd=self.config["db"]["password"],
    #                                port=self.config["db"].get("port") or 3306,
    #                                database = 'ga_chain')
    #     return self._db

    def run(self, block_range):
        print(f'processing block: {block_range}')
        start_block = hex(block_range['start_block'])
        end_block = hex(block_range['end_block'])
        print(start_block, end_block)
        data = self.process(start_block, end_block)
        data = self.parse(data['result'])
        print(f'found {len(data)} transaction on {block_range}')
        # data = self.to_json(data)
        # return data
        self.insert_to_db(data)
        self.update_task_state(block_range['start_block'], block_range['end_block'])
        return True

    def insert_to_db(self, data):
        query = '''
            INSERT INTO transaction_tasks
            (tx_hash)
            VALUES (%s) 
        '''
        tx_hash_list = []
        for node in data:
            tx_hash_list.append(node['tx_hash'])
        cursor = self.db.cursor()
        try:
            cursor.executemany(query, tx_hash_list)
            self.db.commit()
        except Exception as error:
            print(error)
            self.db.rollback()


    def process(self, start_block, end_block):
        id = 1 # uuid4().int % (2**16) if should be unique
        params = [start_block, end_block, True]
        payload = self.payload_template
        payload['params'] = params
        payload['id'] = id
        response = requests.post(self.node_url, json=payload)
        if response.status_code != 200:
            raise f'Error request for ${start_block} -> ${end_block}'
        return response.json()

    def parse(self, data):
        transactions = []
        for block in data:
            timestamp = block['timestamp']
            gas_used = block['gasUsed']
            for transaction in  block['transactions']:
                node_raw = {
                    'block_hash': transaction['blockHash'],
                    'block_number': transaction['blockNumber'],
                    'timestamp': timestamp,
                    'from': transaction['from'],
                    'to': transaction['to'],
                    'value': transaction['value'],
                    'data': transaction['input'],
                    'nonce': transaction['nonce'],
                    'l2_gas': transaction['gas'],
                    'l2_gas_price': transaction['gasPrice'],
                    'l2_gas_used': gas_used,
                    'tx_hash': transaction['hash'],
                }
                transactions.append(node_raw)
        return transactions


    def update_task_state(self, start_block, end_block):
        query = '''
            UPDATE block_range_tasks
            SET status = 'done'
            WHERE start_block = %s AND end_block=%s
        '''
        print(f'marking done {start_block}, {end_block}')
        params = (start_block, end_block)
        cursor = self.db.cursor()
        try:
            cursor.execute(query, params)
            self.db.commit()
        except Exception as error:
            print(error, 'tai')
            self.db.rollback()

    def to_json(data):
        result = []
        for node in data:
            result.append(vars(node))
        return result
            