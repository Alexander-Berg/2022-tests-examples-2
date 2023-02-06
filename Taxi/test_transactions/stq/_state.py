from __future__ import annotations

import dataclasses
from typing import List
from typing import Optional
from typing import Union

from transactions.internal import payment_handler


_MISSING = object()


@dataclasses.dataclass(frozen=False)
class _Refund:
    status: str
    refund_sum: Optional[payment_handler.Sum] = None


@dataclasses.dataclass(frozen=False)
class _Transaction:
    payment_type: str
    status: str
    refunds: List[_Refund]
    transaction_sum: Optional[payment_handler.Sum] = None

    def add_refund(self, **kwargs):
        self.refunds.append(_Refund(**kwargs))


@dataclasses.dataclass(frozen=False)
class _Compensation:
    status: str
    refunds: List[_Refund]
    terminal_id: Optional[int]
    owner_uid: Optional[str]

    def add_refund(self, **kwargs):
        self.refunds.append(_Refund(**kwargs))


@dataclasses.dataclass(frozen=False)
class _Operation:
    operation_id: str
    status: str


@dataclasses.dataclass(frozen=False)
class _ExpectedState:
    invoice_id: str
    transactions: List[_Transaction]
    compensations: List[_Compensation]
    operations: List[_Operation]
    compensation_operations: List[_Operation]
    is_handled: Union[Optional[bool], object]

    @staticmethod
    def empty(invoice_id: str) -> _ExpectedState:
        return _ExpectedState(
            invoice_id=invoice_id,
            transactions=[],
            compensations=[],
            operations=[],
            compensation_operations=[],
            is_handled=_MISSING,
        )

    def add_transaction(self, **kwargs):
        self.transactions.append(_Transaction(**kwargs))

    def add_compensation(self, **kwargs):
        self.compensations.append(_Compensation(**kwargs))

    def add_operation(self, **kwargs):
        self.operations.append(_Operation(**kwargs))

    def add_compensation_operation(self, **kwargs):
        self.compensation_operations.append(_Operation(**kwargs))

    def check(self, invoice):
        self._check_transactions(invoice)
        self._check_operations(invoice)
        self._check_compensation_operations(invoice)

    def check_db(self, db_invoice):
        self._check_compensations(db_invoice)

    def check_db_is_handled(self, db_invoice):
        if self.is_handled is not _MISSING:
            expected = self.is_handled
            assert db_invoice['invoice_request'].get('is_handled') is expected

    def _check_transactions(self, invoice):
        transactions = invoice['transactions']
        assert len(transactions) == len(self.transactions)
        compared_transactions = zip(transactions, self.transactions)
        for transaction, expected_transaction in compared_transactions:
            assert (
                transaction['payment_type']
                == expected_transaction.payment_type
            )
            assert transaction['status'] == expected_transaction.status
            if expected_transaction.transaction_sum is not None:
                actual_sum = _sum_from_api_transaction(transaction)
                assert actual_sum == expected_transaction.transaction_sum
            refunds = transaction['refunds']
            assert len(refunds) == len(expected_transaction.refunds)
            compared_refunds = zip(refunds, expected_transaction.refunds)
            for refund, expected_refund in compared_refunds:
                assert refund['status'] == expected_refund.status
                if expected_refund.refund_sum is not None:
                    actual_refund_sum = _sum_from_api_transaction(refund)
                    assert actual_refund_sum == expected_refund.refund_sum

    def _check_compensations(self, db_invoice):
        compensations = db_invoice['billing_tech'].get('compensations', [])
        assert len(compensations) == len(self.compensations)
        compared_compensations = zip(compensations, self.compensations)
        for compensation, expected_compensation in compared_compensations:
            assert compensation['status'] == expected_compensation.status
            assert (
                compensation.get('terminal_id')
                == expected_compensation.terminal_id
            )
            assert (
                compensation.get('owner_uid')
                == expected_compensation.owner_uid
            )
            refunds = compensation['refunds']
            assert len(refunds) == len(expected_compensation.refunds)
            compared_refunds = zip(refunds, expected_compensation.refunds)
            for refund, expected_refund in compared_refunds:
                assert refund['status'] == expected_refund.status

    def _check_operations(self, invoice):
        operations = invoice['operations']
        assert len(operations) == len(self.operations)
        compared_operations = zip(operations, self.operations)
        for operation, expected_operation in compared_operations:
            assert operation['id'] == expected_operation.operation_id
            assert operation['status'] == expected_operation.status

    def _check_compensation_operations(self, invoice):
        operations = invoice.get('compensation', {}).get('operations', [])
        assert len(operations) == len(self.compensation_operations)
        compared_operations = zip(operations, self.compensation_operations)
        for operation, expected_operation in compared_operations:
            assert operation['id'] == expected_operation.operation_id
            assert operation['status'] == expected_operation.status


def _sum_from_api_transaction(transaction: dict) -> payment_handler.Sum:
    return payment_handler.Sum(
        {item['item_id']: item['amount'] for item in transaction['sum']},
    )
