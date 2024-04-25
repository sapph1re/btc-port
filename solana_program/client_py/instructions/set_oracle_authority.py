from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SetOracleAuthorityArgs(typing.TypedDict):
    oracle_authority: Pubkey


layout = borsh.CStruct("oracle_authority" / BorshPubkey)


class SetOracleAuthorityAccounts(typing.TypedDict):
    processor: Pubkey
    owner: Pubkey


def set_oracle_authority(
    args: SetOracleAuthorityArgs,
    accounts: SetOracleAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["processor"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"'\x9bBj\xd5\xe2r\xae"
    encoded_args = layout.build(
        {
            "oracle_authority": args["oracle_authority"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
