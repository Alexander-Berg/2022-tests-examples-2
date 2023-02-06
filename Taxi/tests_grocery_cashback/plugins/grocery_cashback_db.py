import json

import pytest

from .. import consts
from .. import headers
from .. import models


_SELECT_COMPENSATION_SQL = """
SELECT
    compensation_id,
    order_id,
    data,
    status,
    created,
    updated,
    compensation_type
FROM grocery_cashback.compensations
WHERE compensation_id = %s;
"""

_SELECT_REWARDS = """
SELECT
    order_id,
    reward_id,
    yandex_uid,
    type,
    amount
FROM grocery_cashback.rewards
WHERE order_id = %s;
"""

_INSERT_COMPENSATION = """
INSERT INTO grocery_cashback.compensations (
    compensation_id,
    order_id,
    data,
    compensation_type
) VALUES (%s,
          %s,
          %s,
          %s);
"""

_INSERT_REWARD = """
INSERT INTO grocery_cashback.rewards (
    order_id,
    reward_id,
    yandex_uid,
    type,
    amount
) VALUES (%s,
          %s,
          %s,
          %s,
          %s);
"""


class Database:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def cursor(self):
        return self._pgsql['grocery_cashback'].cursor()

    def get_compensation(self, compensation_id):
        cursor = self.cursor()
        cursor.execute(_SELECT_COMPENSATION_SQL, [compensation_id])
        result = cursor.fetchone()
        if result is None:
            return None

        return models.Compensation(*result)

    def get_rewards(self, order_id):
        cursor = self.cursor()
        cursor.execute(_SELECT_REWARDS, [order_id])
        pg_result = cursor.fetchall()

        if pg_result is None:
            return []

        result = []
        for item in pg_result:
            result.append(models.Reward(*item))

        return result

    def insert_compensation(
            self,
            compensation_id,
            compensation_type,
            data,
            order_id=consts.ORDER_ID,
    ):
        cursor = self.cursor()
        cursor.execute(
            _INSERT_COMPENSATION,
            [compensation_id, order_id, json.dumps(data), compensation_type],
        )

    def insert_reward(
            self,
            order_id=consts.ORDER_ID,
            reward_id='reward-id',
            yandex_uid=headers.YANDEX_UID,
            reward_type='tracking_game',
            amount='15',
    ):
        cursor = self.cursor()
        cursor.execute(
            _INSERT_REWARD,
            [order_id, reward_id, yandex_uid, reward_type, amount],
        )


@pytest.fixture(name='grocery_cashback_db')
def grocery_cashback_db(pgsql):
    return Database(pgsql)
