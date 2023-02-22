from workers.transactionCrawler import TransactionCrawler
from workers.blockCrawler import BlockCrawler
from celery import Celery

app = Celery('ga-chain', broker='amqp://guest:guest@localhost:5672/', backend='redis://localhost')

app.register_task(TransactionCrawler())
app.register_task(BlockCrawler())

# one more worker to load data into bigQuery? (from mysql -> bigQuery)


if __name__ == '__main__':
    app.start()