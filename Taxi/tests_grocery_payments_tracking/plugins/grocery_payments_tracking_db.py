import json

import pytest

from tests_grocery_payments_tracking import consts
from tests_grocery_payments_tracking import models


_SELECT_PAYMENT_SQL = """
SELECT
    order_id,
    status,
    payload
FROM payments.payments
WHERE order_id = %s;
"""

_INSERT_PAYMENT_SQL = """
INSERT INTO payments.payments (order_id, status, payload)
    VALUES (%s, %s, %s);
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_payments_tracking'].cursor()

    def get_payment(self, order_id=consts.ORDER_ID):
        cursor = self.cursor()
        cursor.execute(_SELECT_PAYMENT_SQL, [order_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.Payment(*result)

    def insert_payment(self, status, order_id=consts.ORDER_ID, payload=None):
        cursor = self.cursor()
        payload = json.dumps(payload) if payload is not None else None
        cursor.execute(_INSERT_PAYMENT_SQL, [order_id, status, payload])


@pytest.fixture(name='grocery_payments_tracking_db')
def grocery_payments_tracking_db(pgsql):
    return Database(pgsql)
