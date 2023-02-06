import json

import pytest

from .. import models

_INSERT_TRANSACTION = """
INSERT INTO cibus.transactions (invoice_id,
                                transaction_id,
                                transaction_type,
                                items,
                                status,
                                error_code,
                                error_desc,
                                created)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
;
"""

_LOAD_TRANSACTION = """
SELECT invoice_id,
       transaction_id,
       transaction_type,
       items,
       status,
       error_code,
       error_desc,
       created
FROM cibus.transactions
WHERE invoice_id = %s
  AND transaction_id = %s
;
"""

_INSERT_PAYMENT = """
INSERT INTO cibus.payments (order_id,
                            invoice_id,
                            token,
                            yandex_uid,
                            status,
                            deal_price,
                            redirect_url,
                            application_id,
                            deal_id,
                            error_code,
                            error_desc)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

_LOAD_PAYMENT = """
SELECT
    order_id,
    invoice_id,
    token,
    yandex_uid,
    status,
    deal_price,
    redirect_url,
    application_id,
    deal_id,
    error_code,
    error_desc
FROM cibus.payments
WHERE invoice_id = %s;
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_cibus'].cursor()

    def insert_transaction(self, transaction: models.Transaction):
        self.cursor().execute(
            _INSERT_TRANSACTION,
            [
                transaction.invoice_id,
                transaction.transaction_id,
                transaction.transaction_type.name,
                json.dumps(transaction.items),
                transaction.status.name,
                transaction.error_code,
                transaction.error_desc,
                transaction.created,
            ],
        )

    def load_transaction(self, invoice_id: str, transaction_id: str):
        cursor = self.cursor()
        cursor.execute(_LOAD_TRANSACTION, [invoice_id, transaction_id])

        for result in cursor:
            return models.Transaction(
                invoice_id=result[0],
                transaction_id=result[1],
                transaction_type=models.TransactionType[result[2]],
                items=result[3],
                status=models.TransactionStatus[result[4]],
                error_code=result[5],
                error_desc=result[6],
                created=result[7],
            )

        return None

    def insert_payment(self, payment: models.Payment):
        self.cursor().execute(
            _INSERT_PAYMENT,
            [
                payment.order_id,
                payment.invoice_id,
                payment.token,
                payment.yandex_uid,
                payment.status.name,
                payment.deal_price,
                payment.redirect_url,
                payment.application_id,
                payment.deal_id,
                payment.error_code,
                payment.error_desc,
            ],
        )

    def load_payment(self, invoice_id: str):
        cursor = self.cursor()
        cursor.execute(_LOAD_PAYMENT, [invoice_id])

        for result in cursor:
            return models.Payment(
                order_id=result[0],
                invoice_id=result[1],
                token=result[2],
                yandex_uid=result[3],
                status=models.PaymentStatus[result[4]],
                deal_price=result[5],
                redirect_url=result[6],
                application_id=result[7],
                deal_id=result[8],
                error_code=result[9],
                error_desc=result[10],
            )

        return None


@pytest.fixture(name='grocery_cibus_db')
def grocery_cibus_db(pgsql):
    return Database(pgsql)
