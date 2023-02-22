# ga-chain-mantle

Ga-chain is a protocol that index data from mantle chain both testnet or mainnet (future). 
we are serving data for developers to make it easier to query and visualize data using google bigquery and google data studio (looker studio).

<em>This code is to crawling the mantle-chain testnet data. and it is still running right now to backfill from the first block until it is sync with live data.</em>

## Dataset Bigquery Details

- Project : ambient-airlock-378415
- Dataset : ga_chain
- Tables : transactions, log_events

## How to use dataset

If you want to query the dataset follow this step below :
- First go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
- Select Bigquery menu and create query
- You dont have to search for the dataset, but you can query it for free using dataset details above. example ``SELECT * FROM `ambient-airlock-378415.ga_chain.transactions` LIMIT 1000``

if you want to visualize the dataset you can follow this step below :
- go to [https://lookerstudio.google.com/](https://lookerstudio.google.com/)
- create blank report and add data to report
- choose Bigquery and search for project ``ambient-airlock-378415`` and choose one of the tables to added to looker studio.

or you can find how to use this dataset on my video [here](https://youtu.be/UZiGg6qZeDo)

<em>if you want to use google bigquery client in nodejs/python for customize data visualization. you can dm me on twitter [@a_idria](https://twitter.com/a_idria) for asking the credentials to use the dataset.</em>

## Roadmap

We will add another table in the future such as <em>blocks, token_transfers etc.</em> after that we will try to build analytics dashboard like dune/flipside/footprint to make it easier for developer or community to query mantle-chain data.
