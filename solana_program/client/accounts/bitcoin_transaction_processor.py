import typing
from dataclasses import dataclass
from construct import Construct
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID
from .. import types


class BitcoinTransactionProcessorJSON(typing.TypedDict):
    owner: str
    oracle_authority: str
    transactions: list[str]
    transaction_data: list[types.transaction_data.TransactionDataJSON]


@dataclass
class BitcoinTransactionProcessor:
    discriminator: typing.ClassVar = b":\xd4\x95\xee\xd2\xe2\xa1\x83"
    layout: typing.ClassVar = borsh.CStruct(
        "owner" / BorshPubkey,
        "oracle_authority" / BorshPubkey,
        "transactions" / borsh.Vec(typing.cast(Construct, borsh.String)),
        "transaction_data"
        / borsh.Vec(
            typing.cast(Construct, types.transaction_data.TransactionData.layout)
        ),
    )
    owner: Pubkey
    oracle_authority: Pubkey
    transactions: list[str]
    transaction_data: list[types.transaction_data.TransactionData]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["BitcoinTransactionProcessor"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["BitcoinTransactionProcessor"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["BitcoinTransactionProcessor"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "BitcoinTransactionProcessor":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = BitcoinTransactionProcessor.layout.parse(
            data[ACCOUNT_DISCRIMINATOR_SIZE:]
        )
        return cls(
            owner=dec.owner,
            oracle_authority=dec.oracle_authority,
            transactions=dec.transactions,
            transaction_data=list(
                map(
                    lambda item: types.transaction_data.TransactionData.from_decoded(
                        item
                    ),
                    dec.transaction_data,
                )
            ),
        )

    def to_json(self) -> BitcoinTransactionProcessorJSON:
        return {
            "owner": str(self.owner),
            "oracle_authority": str(self.oracle_authority),
            "transactions": self.transactions,
            "transaction_data": list(
                map(lambda item: item.to_json(), self.transaction_data)
            ),
        }

    @classmethod
    def from_json(
        cls, obj: BitcoinTransactionProcessorJSON
    ) -> "BitcoinTransactionProcessor":
        return cls(
            owner=Pubkey.from_string(obj["owner"]),
            oracle_authority=Pubkey.from_string(obj["oracle_authority"]),
            transactions=obj["transactions"],
            transaction_data=list(
                map(
                    lambda item: types.transaction_data.TransactionData.from_json(item),
                    obj["transaction_data"],
                )
            ),
        )
