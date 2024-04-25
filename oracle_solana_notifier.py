import os
import time
import asyncio
from solana.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from anchorpy import Program, Provider, Wallet
from solana_program.client.program_id import PROGRAM_ID
from solana_program.client.instructions import add_transaction
from solana_program.client.accounts import BitcoinTransactionProcessor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SOLANA_RPC = os.getenv('SOLANA_RPC')
SOLANA_PAYER_PRIVATE_KEY = os.getenv('SOLANA_PAYER_PRIVATE_KEY')

conn = AsyncClient(SOLANA_RPC)
# payer = Account(SOLANA_PAYER_PRIVATE_KEY)


def push_to_program(user_address, tx_hash, amount, is_incoming, block):
    """Send transaction data to the Solana program."""
    pass
    # TODO
    # ix = add_transaction({
        # 'user_address': user_address,
        # 'tx_hash': tx_hash,
        # 'amount': int(amount * 100_000_000),
        # 'is_incoming': is_incoming,
        # 'block': block,
    # }, {
    #   "processor": processor_account,
    #   "oracle_authority": payer.public_key(),
    # })
    # tx = Transaction().add(ix)
    # provider = Provider.local()
    # await provider.send(tx, [payer, acc])
    # print(f"Sending transaction data to Solana: {transaction_data}")
    # print(f"Transaction signature: {transaction_signature}")

def get_sc_latest_block():
    """Retrieve the latest processed Bitcoin block height from the Solana program."""
    # TODO
    return 0

async def main():
    """Get new transactions from DB and push to the Solana program."""

    print(f"Connecting to program: {PROGRAM_ID}")
    processor_acc_addr = Pubkey.find_program_address([bytes("processor", "utf-8")], PROGRAM_ID)[0]    
    processor_acc = await BitcoinTransactionProcessor.fetch(conn, processor_acc_addr)
    print(f"BitcoinTransactionProcessor:")
    print(f" - Account: {processor_acc_addr}")
    print(f" - Owner: {processor_acc.owner}")
    print(f" - Oracle Authority: {processor_acc.oracle_authority}")
    print(f"Latest pushed transactions:")
    for tx in processor_acc.transaction_data:
        print(f" - {tx}")

    # from_block = get_sc_latest_block()
    # while True:
    #     for tx in r.lrange('vault_txs', 0, -1):
    #         tx = pickle.loads(tx)
    #         if tx['block'] <= from_block:
    #             continue
    #         print(f"New transaction: {tx}")
    #         push_to_program(
    #             user_address=tx['uaddr'],
    #             tx_hash=tx['txid'],
    #             amount=tx['amt'],
    #             is_incoming=tx['in'],
    #             block=tx['block'],
    #         )
    #     time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
