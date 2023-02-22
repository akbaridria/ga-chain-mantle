from google.cloud import bigquery as bq
from google.oauth2 import service_account

class BigQueryClient:
    project_id = 'ambient-airlock-378415'
    queryInsertTx = """ INSERT INTO 
                    `ambient-airlock-378415.ga_chain.transactions` (block_number, timestamp, tx_hash, from_address, to_address, value, input, nonce, gas, gas_price, gas_used, status )
                    VALUES
                """
    queryInsertLog = """ INSERT INTO 
                    `ambient-airlock-378415.ga_chain.log_events` (block_number, timestamp, tx_hash, from_address, to_address, contract_address, topics, data , log_index)
                    VALUES
                """
    def __init__(self):
        self.key_path = './ambient-airlock-378415-20a6a1beb3bb.json'

    def connect(self):
        credentials = service_account.Credentials.from_service_account_file(self.key_path)
        self.client = bq.Client(credentials=credentials, project=self.project_id)
        self.client.insert_rows

    def insertIntoTransaction(self, data):
        query = self.queryInsertTx
        for count, i in enumerate(data): 
            query += "({},{},'{}','{}','{}',{},'{}',{},{},{},{},{})".format(i['block_number'], i['timestamp'], i['tx_hash'], i['from_address'], i['to_address'], i['value'], i['data'], i['nonce'], i['gas'], i['gas_price'], i['gas_used'], i['status'])   
            if(count == len(data) - 1) :
                query += ';'
            else :
                query += ','
        query_job = self.client.query(query)
        result = query_job.result()
        return result

    def insertIntoLogEvent(self, data) :
        query = self.queryInsertLog
        for count, i in enumerate(data): 
            query += "({},{},'{}','{}','{}','{}',{},'{}',{})".format(i['block_number'], i['timestamp'], i['tx_hash'], i['from_address'], i['to_address'], i['contract_address'], i['topics'], i['data'], i['idx'])   
            if(count == len(data) - 1) :
                query += ';'
            else :
                query += ','
        query_job = self.client.query(query)
        result = query_job.result()
        return result