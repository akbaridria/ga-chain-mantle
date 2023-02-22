from publishers.publisherManager import PublisherManager
import json

if __name__ == '__main__':
    config = json.load(open('config.json', 'r'))
    app = PublisherManager(config)
    app.run_workers('transactionPublisher', 3)