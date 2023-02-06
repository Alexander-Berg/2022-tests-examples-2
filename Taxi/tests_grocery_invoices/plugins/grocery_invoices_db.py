import json

import pytest

from tests_grocery_invoices import models

_INSERT_RECEIPT = """
INSERT INTO invoices.receipts
    (order_id,
     receipt_id,
     receipt_data_type,
     items,
     total,
     receipt_type,
     link,
     receipt_source,
     payload,
     created)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

_LOAD_RECEIPTS = """
SELECT order_id,
       receipt_id,
       receipt_data_type,
       items,
       total,
       receipt_type,
       link,
       receipt_source,
       payload
FROM invoices.receipts
WHERE order_id = %s;
"""

_LOAD_ALL_TASKS = """
SELECT task_id,
       task_type,
       order_id,
       status,
       args,
       result_payload,
       params
FROM invoices.tasks;
"""

_LOAD_TASK = """
SELECT task_id,
       task_type,
       order_id,
       status,
       args,
       result_payload,
       params
FROM invoices.tasks
WHERE
    task_id = %s;
"""

_INSERT_TASK = """
INSERT INTO invoices.tasks
      (task_id,
       task_type,
       order_id,
       status,
       args,
       result_payload,
       params,
       created)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery-invoices'].cursor()

    def insert(self, *values):
        for value in values:
            if isinstance(value, models.Receipt):
                self.insert_receipt(value)
            elif isinstance(value, models.Task):
                self.insert_task(value)
            else:
                assert False, 'Unsupported type: ' + str(type(value))

    def load_receipts(self, order_id: str):
        cursor = self.cursor()
        cursor.execute(_LOAD_RECEIPTS, [order_id])
        result = cursor.fetchall()

        return [models.Receipt(*item) for item in result]

    def load_receipt(self, order_id: str, receipt_id: str):
        receipts = self.load_receipts(order_id)
        receipts = (it for it in receipts if it.receipt_id == receipt_id)
        return next(receipts, None)

    def insert_receipt(self, receipt: models.Receipt):
        self.cursor().execute(
            _INSERT_RECEIPT,
            [
                receipt.order_id,
                receipt.receipt_id,
                receipt.receipt_data_type,
                json.dumps(receipt.items),
                receipt.total,
                receipt.receipt_type,
                receipt.link,
                receipt.receipt_source,
                json.dumps(receipt.payload),
                receipt.created.isoformat(),
            ],
        )

    def load_all_tasks(self):
        cursor = self.cursor()
        cursor.execute(_LOAD_ALL_TASKS, [])
        result = cursor.fetchall()

        return [models.Task(*item) for item in result]

    def load_task(self, task_id):
        cursor = self.cursor()
        cursor.execute(_LOAD_TASK, [task_id])
        row = cursor.fetchone()
        return models.Task(*row) if row is not None else None

    def insert_task(self, task: models.Task):
        self.cursor().execute(
            _INSERT_TASK,
            [
                task.task_id,
                task.task_type,
                task.order_id,
                task.status,
                json.dumps(task.args),
                json.dumps(task.result_payload),
                json.dumps(task.params),
                task.created,
            ],
        )


@pytest.fixture(name='grocery_invoices_db')
def grocery_invoices_db(pgsql):
    return Database(pgsql)
