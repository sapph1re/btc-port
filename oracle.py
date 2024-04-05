import requests
import time
import os
from solana.rpc.api import Client
from solana.transaction import Transaction
from spl import Account, TransferParams, transfer, PublicKey
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bitcoin address to monitor
BITCOIN_VAULT_ADDRESS = os.getenv('BITCOIN_VAULT_ADDRESS')

# Solana smart contract details
SOLANA_CONTRACT_ADDRESS = os.getenv('SOLANA_CONTRACT_ADDRESS')
SOLANA_PAYER_PRIVATE_KEY = os.getenv('SOLANA_PAYER_PRIVATE_KEY')

# Connect to the Solana network
SOLANA_RPC = os.getenv('SOLANA_RPC')
client = Client(SOLANA_RPC)
payer = Account(SOLANA_PAYER_PRIVATE_KEY)

def get_address_txs(address):
    """Retrieve the list of transactions for the given address."""
    url = f"https://bitcoinexplorer.org/api/address/{address}"
    response = requests.get(url)
    data = response.json()
    transactions = data.get('txHistory', {}).get('txids', [])
    return transactions

def get_tx(txid):
    """Retrieve the transaction details for the given transaction ID."""
    url = f"https://bitcoinexplorer.org/api/tx/{txid}"
    response = requests.get(url)
    data = response.json()
    return data

def get_tx_info(txid):
    """Retrieve: user address, transaction hash, amount, is_incoming"""
    tx = get_tx(txid)
    sender = tx['vin'][0]['scriptSig']['address']
    if sender == BITCOIN_VAULT_ADDRESS:
        is_incoming = False
        for vout in tx['vout']:
            if vout['scriptPubKey']['addresses'][0] != BITCOIN_VAULT_ADDRESS:
                user_address = vout['scriptPubKey']['addresses'][0]
                amount = vout['value']
                break
    else:
        is_incoming = True
        user_address = sender
        for vout in tx['vout']:
            if vout['scriptPubKey']['addresses'][0] == BITCOIN_VAULT_ADDRESS:
                amount = vout['value']
                break
    return {
        'user_address': user_address,
        'txid': txid,
        'amount': amount,
        'is_incoming': is_incoming,
    }


def send_transaction_to_solana(user_address, tx_hash, amount, is_incoming):
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

def run():
    """Monitor transactions on Bitcoin vault and notify Solana smart contract"""
    txs_prev = get_address_txs(BITCOIN_VAULT_ADDRESS)

    while True:
        time.sleep(60)  # Check for new transactions every minute
        txs = get_address_txs(BITCOIN_VAULT_ADDRESS)

        for tx in txs:
            if tx in txs_prev:
                continue
            tx_info = get_tx_info(tx)
            print(f"New transaction: {tx_info}")
            send_transaction_to_solana(**tx_info)

        txs_prev = txs

if __name__ == "__main__":
    run()
