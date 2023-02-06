import json
import typing

import pytest

from .. import models

_UPSERT_DEBT_SQL = """
INSERT INTO user_debts.debts
    (debt_id, status, priority, payload, order_id, invoice_id, created)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (debt_id) DO UPDATE SET
    status = EXCLUDED.status,
    priority = EXCLUDED.priority,
    payload = EXCLUDED.payload,
    order_id = EXCLUDED.order_id,
    invoice_id = EXCLUDED.invoice_id
"""

_GET_DEBT_SQL = """
SELECT debt_id, status, priority, payload,
    order_id, invoice_id, created, updated
FROM user_debts.debts
WHERE debt_id = %s
"""

_INSERT_PREDICTION_SQL = """
INSERT INTO user_debts.debts_prediction AS original
    (order_id, debt_id, yandex_uid, expected, actual, payload)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (debt_id) DO NOTHING
"""

_GET_PREDICTION_SQL = """
SELECT order_id,
       debt_id,
       yandex_uid,
       expected,
       actual,
       payload,
       created,
       updated
FROM user_debts.debts_prediction
WHERE debt_id = %s
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_user_debts'].cursor()

    def upsert(self, *values):
        for value in values:
            if isinstance(value, models.Debt):
                self.upsert_debt(value)
            else:
                assert False, 'Unsupported type: ' + str(type(value))

    def upsert_debt(self, debt: models.Debt):
        self.cursor().execute(
            _UPSERT_DEBT_SQL,
            [
                debt.debt_id,
                debt.status,
                debt.priority,
                json.dumps(debt.payload),
                debt.order_id,
                debt.invoice_id,
                debt.created,
            ],
        )

    def get_debt(self, debt_id: str) -> typing.Optional[models.Debt]:
        cursor = self.cursor()
        cursor.execute(_GET_DEBT_SQL, [debt_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.Debt(*result)

    def insert_prediction(self, prediction: models.Prediction):
        self.cursor().execute(
            _INSERT_PREDICTION_SQL,
            [
                prediction.order_id,
                prediction.debt_id,
                prediction.yandex_uid,
                prediction.expected,
                prediction.actual,
                json.dumps(prediction.payload),
            ],
        )

    def get_prediction(
            self, debt_id: str,
    ) -> typing.Optional[models.Prediction]:
        cursor = self.cursor()
        cursor.execute(_GET_PREDICTION_SQL, [debt_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.Prediction(*result)


@pytest.fixture(name='grocery_user_debts_db')
def grocery_user_debts_db(pgsql):
    return Database(pgsql)
