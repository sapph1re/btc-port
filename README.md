> **WORK IN PROGRESS**

## BTC Port

This code is a proof-of-concept to run an Oracle that monitors transactions on a Bitcoin vault address and sends every transaction details to a smart contract on Solana.

### Instructions

1. Create ".env" file from ".env.example":

    ```shell
    cp .env.example .env
    ```

2. Edit ".env" and set your values:

    ```shell
    nano .env
    ```

3. Install dependencies

    ```shell
    pip install -r requirements.txt
    ```

4. Run

    ```shell
    python oracle.py
    ```
