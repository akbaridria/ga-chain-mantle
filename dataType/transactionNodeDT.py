from dataType.logEventDT import logEventDT


class transactionNodeDT:
    def __init__(self, tx_hash: str, receipt: object, transaction: object):
        self.logEvents = []
        for event in receipt['logs']:
            print(event)
            logEvent = logEventDT(transaction, event)
            self.logEvents.append(logEvent)
        self.block_hash = transaction['blockHash']
        self.block_number = transaction['blockNumber']
        self.block_timestamp = int(transaction['l1Timestamp'], 16)
        self.from_address = transaction['from']
        self.to_address = transaction['to']
        self.value = transaction['value']
        self.data = transaction['input']
        self.nonce = transaction['nonce']
        self.gas = transaction['gas']
        self.gas_price = transaction['gasPrice']
        self.gas_used = receipt['gasUsed']
        self.status = receipt['status']
        self.tx_hash = tx_hash
