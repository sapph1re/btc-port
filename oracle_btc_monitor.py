import requests
import pickle
import redis
import time
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Bitcoin address to monitor
VAULT = os.getenv('BITCOIN_VAULT_ADDRESS')

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    db=os.getenv('REDIS_DB')
)


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
    url = f"https://open-api.unisat.io/v1/indexer/address/{address}/brc20/history"
    response = requests.get(url)
    data = response.json()
    txs = []
    for tx in data['data']['detail']:
        if not tx['valid']:
            continue
        if not tx['type'] == 'transfer':
            continue
        block = tx['block']
        if block < from_block:
            continue
        if tx['from'] == address:
            is_incoming = False
            user_address = tx['to']
        else:
            is_incoming = True
            user_address = tx['from']
        txs.append({
            'asset': tx['ticker'],
            'uaddr': user_address,
            'txid': tx['txid'],
            'amt': tx['amount'],
            'in': is_incoming,
            'block': block,
        })

def latest_processed_block():
    """Get the latest processed transaction's block height from Redis"""

    tx = r.lindex('vault_txs', 0)
    if tx:
        return int(pickle.loads(tx)['block'])
    return 0

def run():
    """Monitor transactions on Bitcoin vault and push them to Redis"""

    # get the latest processed transaction's block height
    last_block = latest_processed_block()

    while True:
        # get the latest transactions
        for tx in get_address_txs(VAULT, last_block + 1):
            tx_info = get_tx_info(tx)
            print(f"New transaction: {tx_info}")
            # push the transaction to Redis for further processing
            r.lpush('vault_txs', pickle.dumps(tx_info))
            # update the latest processed transaction's block height
            if tx_info['block'] > last_block:
                last_block = tx_info['block']
        time.sleep(60)


if __name__ == "__main__":
    run()
