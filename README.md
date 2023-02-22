# ga-chain-mantle

Ga-chain is a protocol that index data from mantle chain both testnet or mainnet (future). 
we are serving data for developers to make it easier to query and visualize data using google bigquery and google data studio (looker studio).

<em>This code is to crawling the mantle-chain testnet data. and it is still running right now to backfill from the first block until it is sync with live data.</em>

## Dataset Bigquery Details

- Project : ambient-airlock-378415
- Dataset : ga_chain
- Tables : transactions, log_events

## How to use dataset

If you want to query and visualize the dataset follow this step below :
- First go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
- Select Bigquery menu and create query
- You dont have to search for the dataset, but you can query it for free using dataset details above example ``SELECT * FROM `ambient-airlock-378415.ga_chain.transactions` LIMIT 1000``
