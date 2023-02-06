import pytest

GET_ALL_FAVORITES = """
    SELECT
        yandex_uid,
        id,
        product_id,
        is_favorite,
        updated
    FROM fav_goods.favorites
"""

GET_FAVORITES_BY_UID = """
    SELECT
        yandex_uid,
        id,
        product_id,
        is_favorite,
        updated
    FROM fav_goods.favorites
    WHERE yandex_uid = '{}'
"""

SET_IS_FAVORITE = """
    INSERT INTO fav_goods.favorites (
        yandex_uid,
        product_id,
        is_favorite
    )
    VALUES ('{}', '{}', '{}')
    ON CONFLICT (yandex_uid, product_id)
    DO UPDATE SET
        is_favorite = excluded.is_favorite,
        updated = CURRENT_TIMESTAMP
"""

INSERT_FAVORITES = """
    INSERT INTO fav_goods.favorites (
        yandex_uid,
        product_id,
        is_favorite
    )
    VALUES (
        '{}',
        UNNEST(array{}), UNNEST(array{})
    )
    ON CONFLICT (yandex_uid, product_id)
    DO UPDATE SET
        is_favorite = excluded.is_favorite,
        updated = CURRENT_TIMESTAMP
"""


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_fav_goods']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor


class FavoritesDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def get_all_favorites(self):
        cursor = _execute_sql_query(
            sql_query=GET_ALL_FAVORITES, pgsql=self._pgsql,
        )
        ret = []
        for row in list(cursor):
            assert row[3] is not None
            assert row[1] is not None
            ret.append(
                {
                    'yandex_uid': row[0],
                    'product_id': row[2],
                    'is_favorite': row[3],
                },
            )
        return ret

    def get_favorites(self, yandex_uid):
        cursor = _execute_sql_query(
            sql_query=GET_FAVORITES_BY_UID.format(yandex_uid),
            pgsql=self._pgsql,
        )
        ret = []
        for row in list(cursor):
            assert row[3] is not None
            assert row[1] is not None
            ret.append(
                {
                    'yandex_uid': row[0],
                    'product_id': row[2],
                    'is_favorite': row[3],
                },
            )
        return ret

    def set_is_favorite(self, yandex_uid, product_id, is_favorite):
        query = SET_IS_FAVORITE.format(yandex_uid, product_id, is_favorite)
        _execute_sql_query(query, pgsql=self._pgsql)

    def insert_favorites(self, yandex_uid, favorite_products):
        product_ids = []
        is_favorite_array = []
        for fav_product in favorite_products:
            product_ids.append(fav_product['product_id'])
            is_favorite_array.append(fav_product['is_favorite'])
        query = INSERT_FAVORITES.format(
            yandex_uid, str(product_ids), str(is_favorite_array),
        )
        _execute_sql_query(query, pgsql=self._pgsql)


@pytest.fixture(name='favorites_db')
def mock_recent_goods_db(pgsql):
    return FavoritesDbAgent(pgsql=pgsql)
