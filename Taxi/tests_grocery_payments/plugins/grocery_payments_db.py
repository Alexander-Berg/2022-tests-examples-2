import json

import pytest

from .. import models

_UPSERT_TRANSACTIONS_CALLBACK_SQL = """
INSERT INTO payments.transactions_callbacks
    (invoice_id, operation_id, notification_type, operation_status)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

_HAS_TRANSACTIONS_CALLBACK_SQL = """
SELECT 1
FROM payments.transactions_callbacks
WHERE invoice_id = %s
  AND operation_id = %s
  AND notification_type = %s
"""

_UPSERT_DEFERRED_OPERATION_SQL = """
INSERT INTO payments.deferred_tasks
    (invoice_id, task_id, status, payload)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

_LOAD_DEFERRED_OPERATION_SQL = """
SELECT invoice_id, task_id, status, payload
FROM payments.deferred_tasks
WHERE invoice_id = %s
  AND task_id = %s
"""

_UPSERT_INVOICE_OPERATION_SQL = """
INSERT INTO payments.invoice_operations
    (invoice_id, operation_id)
VALUES (%s, %s)
ON CONFLICT DO NOTHING
"""

_LOAD_INVOICE_OPERATION_SQL = """
SELECT invoice_id, operation_id
FROM payments.invoice_operations
WHERE invoice_id = %s
  AND operation_id = %s
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_payments'].cursor()

    def upsert_callback(self, value: models.TransactionsCallback):
        self.cursor().execute(
            _UPSERT_TRANSACTIONS_CALLBACK_SQL,
            [
                value.invoice_id,
                value.operation_id,
                value.notification_type,
                value.operation_status,
            ],
        )

    def has_callback(self, value: models.TransactionsCallback) -> bool:
        cursor = self.cursor()
        cursor.execute(
            _HAS_TRANSACTIONS_CALLBACK_SQL,
            [value.invoice_id, value.operation_id, value.notification_type],
        )
        result = cursor.fetchone()
        return result is not None

    def upsert_deferred(self, value: models.DeferredTask):
        self.cursor().execute(
            _UPSERT_DEFERRED_OPERATION_SQL,
            [
                value.invoice_id,
                value.task_id,
                value.status,
                json.dumps(value.payload),
            ],
        )

    def load_deferred(self, invoice_id: str, task_id: str):
        cursor = self.cursor()
        cursor.execute(_LOAD_DEFERRED_OPERATION_SQL, [invoice_id, task_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.DeferredTask(*result)

    def upsert_invoice_operation(self, value: models.InvoiceOperationPg):
        self.cursor().execute(
            _UPSERT_INVOICE_OPERATION_SQL,
            [value.invoice_id, value.operation_id],
        )

    def load_invoice_operation(self, invoice_id: str, operation_id: str):
        cursor = self.cursor()
        cursor.execute(_LOAD_INVOICE_OPERATION_SQL, [invoice_id, operation_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.InvoiceOperationPg(*result)

    def has_invoice_operation(self, invoice_id: str, operation_id: str):
        return (
            self.load_invoice_operation(invoice_id, operation_id) is not None
        )


@pytest.fixture(name='grocery_payments_db')
def grocery_payments_db(pgsql):
    return Database(pgsql)
