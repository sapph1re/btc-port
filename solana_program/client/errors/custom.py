import typing
from anchorpy.error import ProgramError


class InvalidOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Invalid owner")

    code = 6000
    name = "InvalidOwner"
    msg = "Invalid owner"


class InvalidOracleAuthority(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Invalid oracle authority")

    code = 6001
    name = "InvalidOracleAuthority"
    msg = "Invalid oracle authority"


class TransactionAlreadyProcessed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Transaction already processed")

    code = 6002
    name = "TransactionAlreadyProcessed"
    msg = "Transaction already processed"


CustomError = typing.Union[
    InvalidOwner, InvalidOracleAuthority, TransactionAlreadyProcessed
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidOwner(),
    6001: InvalidOracleAuthority(),
    6002: TransactionAlreadyProcessed(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
