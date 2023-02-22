
CREATE DATABASE ga_chain;
USE ga_chain;
-- block_range_tasks
CREATE TABLE block_range_tasks (
    start_block BIGINT UNSIGNED,
    end_block BIGINT UNSIGNED,
    status ENUM('waiting', 'running', 'done', 'failed') DEFAULT 'waiting',
    retry_num INT UNSIGNED DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (start_block, end_block),
    INDEX status_idx (status)
);

-- transaction_tasks
CREATE TABLE transaction_tasks (
    tx_hash VARCHAR(128),
    status ENUM('waiting', 'running', 'done', 'failed') DEFAULT 'waiting',
    retry_num INT UNSIGNED DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (tx_hash),
    INDEX status_idx (status)
);

-- transactions
CREATE TABLE transactions (
    tx_hash VARCHAR(128) PRIMARY KEY,
    block_number BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    from_address VARCHAR(128) NOT NULL,
    to_address VARCHAR(128),
    value BIGINT UNSIGNED DEFAULT 0,
    data TEXT,
    nonce BIGINT UNSIGNED,
    gas BIGINT UNSIGNED,
    gas_price BIGINT UNSIGNED,
    gas_used BIGINT UNSIGNED,
    status TINYINT,
    sent TINYINT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- log events
CREATE TABLE log_events (
    idx INT UNSIGNED NOT NULL,
    tx_hash VARCHAR(128),
    block_number BIGINT UNSIGNED NOT NULL,
    timestamp BIGINT UNSIGNED NOT NULL,
    contract_address VARCHAR(128) NOT NULL,
    from_address VARCHAR(128) NOT NULL,
    to_address VARCHAR(128),
    topics JSON,
    data TEXT,
    sent TINYINT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (tx_hash, idx)
);