import pytest

GET_ALL_ATTRIBUTES = 'SELECT * FROM fav_goods.attributes'

GET_ATTRIBUTES_BY_UID = """
    SELECT
        yandex_uid,
        id,
        important_ingredients,
        main_allergens,
        custom_tags,
        updated
    FROM fav_goods.attributes
    WHERE yandex_uid = '{}'
"""

SET_ATTRIBUTES = """
    INSERT INTO fav_goods.attributes (
        yandex_uid,
        important_ingredients,
        main_allergens,
        custom_tags
    )
    VALUES ('{}', '{}', '{}', '{}')
    ON CONFLICT (yandex_uid)
    DO UPDATE SET
        important_ingredients = excluded.important_ingredients,
        main_allergens = excluded.main_allergens,
        custom_tags = excluded.custom_tags
"""


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_fav_goods']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor


class AttributesDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def get_all_attributes(self):
        cursor = _execute_sql_query(
            sql_query=GET_ALL_ATTRIBUTES, pgsql=self._pgsql,
        )
        ret = []
        for row in list(cursor):
            assert row[5] is not None
            ret.append(
                {
                    'yandex_uid': row[0],
                    'important_ingredients': row[1],
                    'main_allergens': row[2],
                    'custom_tags': row[3],
                    'updated': str(row[4]),
                },
            )
        return ret

    def get_attributes(self, yandex_uid):
        cursor = _execute_sql_query(
            sql_query=GET_ATTRIBUTES_BY_UID.format(yandex_uid),
            pgsql=self._pgsql,
        )
        ret = []
        for row in list(cursor):
            assert row[1] is not None
            assert row[5] is not None
            ret.append(
                {
                    'yandex_uid': row[0],
                    'important_ingredients': row[1],
                    'main_allergens': row[2],
                    'custom_tags': row[3],
                    'updated': str(row[4]),
                },
            )
        return ret

    def set_attributes(
            self,
            yandex_uid,
            important_ingredients,
            main_allergens,
            custom_tags,
    ):
        query = (
            SET_ATTRIBUTES.format(
                yandex_uid,
                str(important_ingredients).replace('\'', '"'),
                str(main_allergens).replace('\'', '"'),
                str(custom_tags).replace('\'', '"'),
            )
            .replace('[', '{')
            .replace(']', '}')
        )
        _execute_sql_query(sql_query=query, pgsql=self._pgsql)


@pytest.fixture(name='attributes_db')
def mock_recent_goods_db(pgsql):
    return AttributesDbAgent(pgsql=pgsql)
