from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TransactionDataJSON(typing.TypedDict):
    asset: str
    user_address: str
    tx_hash: str
    amount: int
    is_incoming: bool
    block: int


@dataclass
class TransactionData:
    layout: typing.ClassVar = borsh.CStruct(
        "asset" / borsh.String,
        "user_address" / borsh.String,
        "tx_hash" / borsh.String,
        "amount" / borsh.U64,
        "is_incoming" / borsh.Bool,
        "block" / borsh.U32,
    )
    asset: str
    user_address: str
    tx_hash: str
    amount: int
    is_incoming: bool
    block: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "TransactionData":
        return cls(
            asset=obj.asset,
            user_address=obj.user_address,
            tx_hash=obj.tx_hash,
            amount=obj.amount,
            is_incoming=obj.is_incoming,
            block=obj.block,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "asset": self.asset,
            "user_address": self.user_address,
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "is_incoming": self.is_incoming,
            "block": self.block,
        }

    def to_json(self) -> TransactionDataJSON:
        return {
            "asset": self.asset,
            "user_address": self.user_address,
            "tx_hash": self.tx_hash,
            "amount": self.amount,
            "is_incoming": self.is_incoming,
            "block": self.block,
        }

    @classmethod
    def from_json(cls, obj: TransactionDataJSON) -> "TransactionData":
        return cls(
            asset=obj["asset"],
            user_address=obj["user_address"],
            tx_hash=obj["tx_hash"],
            amount=obj["amount"],
            is_incoming=obj["is_incoming"],
            block=obj["block"],
        )
