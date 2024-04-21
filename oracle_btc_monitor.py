import requests
import pickle
import time
import os
from db import Transaction, IntegrityError
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Bitcoin address to monitor
VAULT = os.getenv('BITCOIN_VAULT_ADDRESS')
HIRO_API_URL = os.getenv('HIRO_API_URL')


def get_address_txs(address, from_block=0):
    """Retrieve the list of transactions for the given address."""
    url = f"https://bitcoinexplorer.org/api/address/{address}"
    response = requests.get(url)
    data = response.json()
    txs = []
    for txid in data.get('txHistory', {}).get('txids', []):
        block = data.get('txHistory', {}).get('blockHeightsByTxid', {}).get(txid, 0)
        if block < from_block:
            continue
        txs.append({
            'txid': txid,
            'block': block,
        })
    return txs

def get_tx(txid):
    """Retrieve the transaction details for the given transaction ID."""
    url = f"https://bitcoinexplorer.org/api/tx/{txid}"
    response = requests.get(url)
    data = response.json()
    return data

def get_tx_info(tx):
    """Retrieve: user address, transaction hash, amount, is_incoming"""
    txid = tx['txid']
    block = tx['block']
    tx = get_tx(txid)
    sender = tx['vin'][0]['scriptSig']['address']
    if sender == VAULT:
        is_incoming = False
        for vout in tx['vout']:
            if vout['scriptPubKey']['address'] != VAULT:
                user_address = vout['scriptPubKey']['address']
                amount = vout['value']
                break
    else:
        is_incoming = True
        user_address = sender
        for vout in tx['vout']:
            if vout['scriptPubKey']['address'] == VAULT:
                amount = vout['value']
                break
    return {
        'asset': 'BTC',
        'uaddr': user_address,
        'txid': txid,
        'amt': amount,
        'in': is_incoming,
        'block': block,
    }

def get_brc20_txs(address, from_block=0):
    """Retrieve the list of BRC20 transactions for the given address."""
    url = f"{HIRO_API_URL}activity?address={address}"
    response = requests.get(url)
    data = response.json()
    txs = []
    for tx in data['results']:
        if not tx['operation'] == 'transfer_send':
            continue
        block = tx['block_height']
        if block < from_block:
            continue
        if tx['transfer_send']['from_address'] == address:
            is_incoming = False
            user_address = tx['transfer_send']['to_address']
        else:
            is_incoming = True
            user_address = tx['transfer_send']['from_address']
        txs.append({
            'asset': tx['ticker'],
            'uaddr': user_address,
            'txid': tx['tx_id'],
            'amt': tx['transfer_send']['amount'],
            'in': is_incoming,
            'block': block,
        })

def latest_processed_block():
    """Get the latest processed transaction's block height from DB, separately for BTC and BRC20."""

    block_btc = 0
    block_brc20 = 0
    try:
        block_btc = Transaction.select().where(
            Transaction.asset == 'BTC'
        ).order_by(
            Transaction.block.desc()
        ).get().block
    except Transaction.DoesNotExist:
        pass
    try:
        block_brc20 = Transaction.select().where(
            Transaction.asset != 'BTC'
        ).order_by(
            Transaction.block.desc()
        ).get().block
    except Transaction.DoesNotExist:
        pass
    return block_btc, block_brc20

def run():
    """Monitor transactions on Bitcoin vault and push them to DB"""

    # get the latest processed transaction's block height
    last_block_btc, last_block_brc20 = latest_processed_block()
    print(f"Last processed block: {last_block_btc} for BTC, {last_block_brc20} for BRC20")

    while True:
        # get the latest BTC transactions
        for tx in get_address_txs(VAULT, last_block_btc + 1):
            tx_info = get_tx_info(tx)
            print(f"New transaction: {tx_info}")
            # push the transaction to DB for further processing
            try:
                Transaction.create(
                    asset=tx_info['asset'],
                    txid=tx_info['txid'],
                    user_address=tx_info['uaddr'],
                    amount=tx_info['amt'],
                    is_incoming=tx_info['in'],
                    block=tx_info['block'],
                )
            except IntegrityError:
                print(f"Transaction already processed: {tx_info['txid']}")
            # update the latest processed transaction's block height
            if tx_info['block'] > last_block_btc:
                last_block_btc = tx_info['block']
        time.sleep(60)


if __name__ == "__main__":
    run()
