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
from solana_program.client.types import TransactionData
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SOLANA_RPC = os.getenv('SOLANA_RPC')
SOLANA_PAYER_PRIVATE_KEY = os.getenv('SOLANA_PAYER_PRIVATE_KEY')


class Notifier:
    def __init__(self):
        self.conn = AsyncClient(SOLANA_RPC)
        # self.payer = Keypair.from_secret_key(SOLANA_PAYER_PRIVATE_KEY)
        self.processor_acc_addr = Pubkey.find_program_address([bytes("processor", "utf-8")], PROGRAM_ID)[0]
        self.processor_acc = None

    async def push_to_program(self, user_address, tx_hash, amount, is_incoming, block):
        """Send transaction data to the Solana program."""
        pass
        # TODO
        # ix = add_transaction({
        #     'user_address': user_address,
        #     'tx_hash': tx_hash,
        #     'amount': int(amount * 100_000_000),
        #     'is_incoming': is_incoming,
        #     'block': block,
        # }, {
        #     "processor": self.processor,
        #     "oracle_authority": self.payer.public_key(),
        # })
        # tx = Transaction().add(ix)
        # provider = Provider.local()
        # await provider.send(tx, [self.payer, self.processor])
        # print(f"Sending transaction data to Solana: {transaction_data}")
        # print(f"Transaction signature: {transaction_signature}")

    async def get_latest_processed_block(self):
        """Retrieve the latest processed Bitcoin block height from the Solana program, for BTC and for BRC20."""

        await self.load_processor_acc()
        latest_block_btc = 0
        latest_block_brc20 = 0
        for tx in self.processor_acc.transaction_data:
            pass
            # TODO: add asset to TransactionData
        
        return latest_block_btc, latest_block_brc20
    
    async def load_processor_acc(self):
        """Load the BitcoinTransactionProcessor account."""

        self.processor_acc = await BitcoinTransactionProcessor.fetch(self.conn, self.processor_acc_addr)
        print(f"BitcoinTransactionProcessor:")
        print(f" - Account: {self.processor_acc_addr}")
        print(f" - Owner: {self.processor_acc.owner}")
        print(f" - Oracle Authority: {self.processor_acc.oracle_authority}")
        print(f"Latest pushed transactions:")
        for tx in self.processor_acc.transaction_data:
            print(f" - {tx}")
        return self.processor_acc

    async def run(self):
        """Get new transactions from DB and push to the Solana program."""

        print(f"Connecting to program: {PROGRAM_ID}")
        
        latest_block_btc, latest_block_brc20 = await self.get_latest_processed_block()
        print(f"Last processed block: #{latest_block_btc} for BTC, #{latest_block_brc20} for BRC20")

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
    notifier = Notifier()
    asyncio.run(notifier.run())
