import pytest


@pytest.fixture(name='erased_users')
def erased_users_db_fixture(pgsql):
    class Context:
        def __init__(self, pgsql):
            self._pgsql = pgsql

        def insert_user(self, yandex_uid):
            db = self._pgsql['grocery_takeout']
            cursor = db.cursor()

            cursor.execute(
                'INSERT INTO takeout.erased_users(yandex_uid)'
                f'VALUES (\'{yandex_uid}\')',
            )

    return Context(pgsql)
