import dataclasses

import pytest
import pytz


ADD_RECENT_GOOD = """
INSERT INTO fav_goods.recent_goods (
    yandex_uid, product_id, last_purchase
)
VALUES ('{}', '{}', '{}')
ON CONFLICT (yandex_uid, product_id)
DO UPDATE
SET last_purchase = excluded.last_purchase
"""

ADD_RECENT_GOODS = """
INSERT INTO fav_goods.recent_goods (
    yandex_uid, product_id, last_purchase
)
VALUES
{}
ON CONFLICT (yandex_uid, product_id)
DO UPDATE
SET last_purchase = excluded.last_purchase
"""

GET_ALL_RECENT_GOODS = 'SELECT * FROM fav_goods.recent_goods'

GET_RECENT_GOOD_LAST_PURCHASE = """
SELECT last_purchase FROM fav_goods.recent_goods
WHERE recent_goods.yandex_uid = '{}' AND recent_goods.product_id = '{}'
"""


@dataclasses.dataclass
class RecentGood:
    yandex_uid: str
    product_id: str
    last_purchase: str


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_fav_goods']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor


class RecentGoodsDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def add_recent_good(self, yandex_uid, product_id, last_purchase):
        sql_query = ADD_RECENT_GOOD.format(
            yandex_uid, product_id, last_purchase,
        )
        _execute_sql_query(sql_query=sql_query, pgsql=self._pgsql)

    def add_recent_goods(self, yandex_uid, product_ids, last_purchase):
        values = [
            f'(\'{yandex_uid}\', \'{product_id}\', \'{last_purchase}\')'
            for product_id in product_ids
        ]
        sql_query = ADD_RECENT_GOODS.format(', '.join(values))
        _execute_sql_query(sql_query=sql_query, pgsql=self._pgsql)

    def get_all_recent_goods(self):
        cursor = _execute_sql_query(
            sql_query=GET_ALL_RECENT_GOODS, pgsql=self._pgsql,
        )
        return [
            RecentGood(
                yandex_uid=recent_good[0],
                product_id=recent_good[1],
                last_purchase=recent_good[2].astimezone(pytz.utc).isoformat(),
            )
            for recent_good in list(cursor)
        ]

    def get_last_purchase(self, yandex_uid, product_id):
        sql_query = GET_RECENT_GOOD_LAST_PURCHASE.format(
            yandex_uid, product_id,
        )
        cursor = _execute_sql_query(sql_query=sql_query, pgsql=self._pgsql)
        return list(cursor)[0][0].astimezone(pytz.utc).isoformat()


@pytest.fixture(name='recent_goods_db')
def mock_recent_goods_db(pgsql):
    return RecentGoodsDbAgent(pgsql=pgsql)
