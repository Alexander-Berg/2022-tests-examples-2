import decimal
from typing import Collection
from typing import Tuple
from typing import Union

from billing_functions.functions.core import support_info

OperationTuple = Union[
    Tuple[str, str, str, str], Tuple[str, str, str, str, dict],
]
OperationTuples = Collection[OperationTuple]


def make_var(
        value: str, operations: OperationTuples = tuple(),
) -> support_info.Var:
    mutations = [_make_operation(*operation) for operation in operations]
    return support_info.Var(decimal.Decimal(value), mutations)


def _make_operation(
        operation: str,
        arg_value: str,
        reason: str,
        value: str,
        details: dict = None,
) -> support_info.Operation:
    if details is None:
        details = {}
    return support_info.Operation(
        op=operation,
        args=[decimal.Decimal(arg_value)],
        reason=reason,
        value=decimal.Decimal(value),
        details=details,
    )
