import pytest

GET_ALL_ONBOARDINGS = """
    SELECT
        yandex_uid,
        type,
        viewed
    FROM grocery_user_data.onboardings
"""

ADD_ONBOARDINGS = """
    INSERT INTO grocery_user_data.onboardings (
        yandex_uid,
        type,
        viewed
    )
    SELECT
        '{}',
        '{}',
        {}
"""


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_user_data']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor


class OnboardingDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def get_all_onboardings(self):
        cursor = _execute_sql_query(
            sql_query=GET_ALL_ONBOARDINGS, pgsql=self._pgsql,
        )
        ret = []
        for row in list(cursor):
            ret.append(
                {'yandex_uid': row[0], 'type': row[1], 'viewed': row[2]},
            )
        return ret

    def add_onboarding(self, yandex_uid, onboarding_type, viewed=True):
        _execute_sql_query(
            sql_query=ADD_ONBOARDINGS.format(
                yandex_uid, onboarding_type, viewed,
            ),
            pgsql=self._pgsql,
        )


@pytest.fixture(name='onboardings_db')
def mock_recent_goods_db(pgsql):
    return OnboardingDbAgent(pgsql=pgsql)
