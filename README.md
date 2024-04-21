> **WORK IN PROGRESS**

## BTC Port

Please read the comprehensive [description](docs/Description.md) of the system design.

This code so far is a proof-of-concept implementation of a part of the system. It runs an Oracle that monitors transactions on a Bitcoin vault address and sends every transaction's details to a smart contract on Solana.

### Instructions

1. Deploy the smart contract: `contracts/lib.rs`

1. Run Redis:

    ```shell
    docker run --name postgres -e POSTGRES_PASSWORD=your_db_password -p 5432:5432 -d postgres
    ```

1. Run a [Hiro Ordinals API](https://github.com/hirosystems/ordinals-api) node (optional)

1. Create ".env" file from ".env.example":

    ```shell
    cp .env.example .env
    ```

1. Edit ".env" and set your values, make sure to set DB_URL with your db password:

    ```shell
    nano .env
    ```

1. Install dependencies

    ```shell
    pip install -r requirements.txt
    ```

1. Run

    ```shell
    python oracle_btc_monitor.py
    ```
