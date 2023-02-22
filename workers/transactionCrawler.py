import json
import MySQLdb
from dataType.transactionNodeDT import transactionNodeDT
from workers.Worker import Worker
from web3 import Web3

class TransactionCrawler(Worker):
    name = 'transaction_crawlers'
    
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

    def run(self, tx_hash):
        web3 = Web3(Web3.HTTPProvider(self.config['web3_http_url']))
        e = web3.eth.get_transaction_receipt(tx_hash)
        d = web3.eth.get_transaction(tx_hash)
        print(f'processing tx: {tx_hash}')
        receipt = json.loads(web3.toJSON(e))
        transaction = json.loads(web3.toJSON(d))
        transaction_instance = self.parse(tx_hash, receipt, transaction)

        self.insert_transaction(transaction_instance)
        print(f'done tx: {tx_hash}')
        self.update_task_state(tx_hash)
        return True

    def insert_transaction(self, data: transactionNodeDT):
        # insert transaction
        query = '''
            INSERT INTO transactions
                (
                    tx_hash, block_number, timestamp, from_address,
                    to_address, value, data, nonce, gas, gas_price,
                    gas_used, status
                )
            VALUES 
                (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s
                )
        '''
        params = (
            data.tx_hash, data.block_number, data.block_timestamp, data.from_address,
            data.to_address, data.value, data.data, data.nonce, data.gas, data.gas_price,
            data.gas_used, data.status
            )
        cursor = self.db.cursor()
        cursor.execute(query, params)

        # insert logEvent
        query = '''
            INSERT INTO log_events
                (
                    tx_hash, idx, block_number, timestamp, contract_address, from_address,
                    to_address, topics, data   
                )
            VALUES 
                (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
        '''
        params = []
        for idx, event in enumerate(data.logEvents):
            node = (
                data.tx_hash, idx, event.block_number, event.block_timestamp, event.contract_address, event.from_address,
                event.to_address, event.topics, event.data
            )
            params.append(node)
        cursor.executemany(query, params)
        self.db.commit()
        cursor.close()

    def parse(self, tx_hash, receipt, transaction):
        result = transactionNodeDT(tx_hash, receipt, transaction)
        return result

    def update_task_state(self, tx_hash):
        query = '''
            UPDATE transaction_tasks
            SET status = %s
            WHERE tx_hash = %s
        '''
        params = ('done', tx_hash)
        cursor = self.db.cursor()
        cursor.execute(query, params)
        self.db.commit()
        cursor.close()

