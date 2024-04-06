> **WORK IN PROGRESS**

## BTC Port

Please read the comprehensive [description](docs/Description.md) of the system design.

This code so far is a proof-of-concept implementation of a part of the system. It runs an Oracle that monitors transactions on a Bitcoin vault address and sends every transaction's details to a smart contract on Solana.

### Instructions

1. Deploy the smart contract: `contracts/lib.rs`

2. Create ".env" file from ".env.example":

    ```shell
    cp .env.example .env
    ```

3. Edit ".env" and set your values:

    ```shell
    nano .env
    ```

4. Install dependencies

    ```shell
    pip install -r requirements.txt
    ```

5. Run

    ```shell
    python oracle.py
    ```
