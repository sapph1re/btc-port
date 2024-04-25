from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class AddTransactionArgs(typing.TypedDict):
    user_address: str
    tx_hash: str
    amount: int
    is_incoming: bool


layout = borsh.CStruct(
    "user_address" / borsh.String,
    "tx_hash" / borsh.String,
    "amount" / borsh.U64,
    "is_incoming" / borsh.Bool,
)


class AddTransactionAccounts(typing.TypedDict):
    processor: Pubkey
    oracle_authority: Pubkey


def add_transaction(
    args: AddTransactionArgs,
    accounts: AddTransactionAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["processor"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["oracle_authority"], is_signer=True, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"0`\xaepQ\x1e\xefY"
    encoded_args = layout.build(
        {
            "user_address": args["user_address"],
            "tx_hash": args["tx_hash"],
            "amount": args["amount"],
            "is_incoming": args["is_incoming"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
