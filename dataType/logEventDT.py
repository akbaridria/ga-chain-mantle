import json

class logEventDT:
    def __init__(self, transaction: object, event: object):
        self.block_number = transaction['blockNumber']
        self.block_timestamp = int(transaction['l1Timestamp'], 16)
        self.from_address = transaction['from']
        self.to_address = transaction['to']
        self.contract_address = event['address']
        self.topics = json.dumps(event['topics'])
        self.data = event['data']