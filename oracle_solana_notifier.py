import redis
import time
import os
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl import Account, TransferParams, transfer, PublicKey
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Solana smart contract details
SOLANA_CONTRACT_ADDRESS = os.getenv('SOLANA_CONTRACT_ADDRESS')
SOLANA_PAYER_PRIVATE_KEY = os.getenv('SOLANA_PAYER_PRIVATE_KEY')

# Connect to the Solana network
SOLANA_RPC = os.getenv('SOLANA_RPC')
client = Client(SOLANA_RPC)
payer = Account(SOLANA_PAYER_PRIVATE_KEY)

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    db=os.getenv('REDIS_DB')
)


def notify_sc(user_address, tx_hash, amount, is_incoming, block):
    """Send transaction data to the Solana smart contract."""
    transaction = Transaction()
    transfer_params = TransferParams(
        from_pubkey=payer.public_key(),
        to_pubkey=PublicKey(SOLANA_CONTRACT_ADDRESS),
        lamports=0,  # No need to transfer SOL for this transaction
    )
    instruction = transfer(params=transfer_params)
    transaction.add(instruction)

    # Encode transaction data
    transaction_data = {
        'user_address': user_address,
        'tx_hash': tx_hash,
        'amount': int(amount * 100_000_000),
        'is_incoming': is_incoming,
        'block': block,
    }
    transaction.add_instruction(
        program_id=PublicKey(SOLANA_CONTRACT_ADDRESS),
        data=bytes(str(transaction_data), 'utf-8'),
        accounts=[],
    )

    transaction.sign(payer)
    transaction_signature = transaction.signature()
    print(f"Sending transaction data to Solana: {transaction_data}")
    print(f"Transaction signature: {transaction_signature}")

    # Send the transaction to the Solana network
    client.send_transaction(transaction)

def get_sc_latest_block():
    """Retrieve the latest processed Bitcoin block height from the Solana smart contract."""
    # TODO
    return 0

def run():
    """Get new transactions from Redis and notify the Solana smart contract"""

    from_block = get_sc_latest_block()
    while True:
        for tx in r.lrange('vault_txs', 0, -1):
            if tx['block'] <= from_block:
                continue
            print(f"New transaction: {tx}")
            notify_sc(
                user_address=tx['uaddr'],
                tx_hash=tx['txid'],
                amount=tx['amt'],
                is_incoming=tx['in'],
                block=tx['block'],
            )
        time.sleep(1)


if __name__ == "__main__":
    run()
