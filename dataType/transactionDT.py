class transactionDT:
    def __init__(self, data: object):
        self.block_hash = data['blockHash']
        self.block_number = data['blockNumber']
        self.timestamp = data['timestamp']
        self.from_address = data['from']
        self.to_address = data['to']
        self.value = data['value']
        self.data = data['input']
        self.nonce = data['nonce']
        self.l2_gas = data['gas']
        self.l2_gas_price = data['gasPrice']
        self.l2_gas_used = data['gas_used']
        self.tx_hash = data['hash']