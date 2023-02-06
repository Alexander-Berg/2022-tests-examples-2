import pytest


def _transaction(sql_query):
    return f"""
BEGIN TRANSACTION;
{sql_query}
COMMIT TRANSACTION;
    """


def _flush_distlocks():
    return """
TRUNCATE TABLE grocery_uber_gw.distlocks;
TRUNCATE TABLE grocery_uber_gw.distlock_periodic_updates;
"""


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['grocery_uber_gw']
    cursor = db.cursor()
    cursor.execute(sql_query)


def _fetch_from_sql(sql_query, pgsql):
    db = pgsql['grocery_uber_gw']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()


class GroceryUberGwDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql
        self._in_transaction = False
        self._sql_query = ''

    def begin_transaction(self):
        assert not self._in_transaction
        self._in_transaction = True

    def commit_transaction(self):
        assert self._in_transaction

        sql_query = _transaction(self._sql_query)
        _execute_sql_query(sql_query, pgsql=self._pgsql)

        self._sql_query = ''
        self._in_transaction = False

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.commit_transaction()

    def apply_sql_query(self, sql_query, as_transaction=False):
        if self._in_transaction:
            self._sql_query += f'\n{sql_query}'
        else:
            if as_transaction:
                sql_query = _transaction(sql_query)
            _execute_sql_query(sql_query, pgsql=self._pgsql)

    def fetch_from_sql(self, sql_query):
        return _fetch_from_sql(sql_query, pgsql=self._pgsql)

    def flush_distlocks(self):
        _execute_sql_query(_flush_distlocks(), self._pgsql)


@pytest.fixture(name='grocery_uber_gw_db')
def mock_grocery_uber_gw_db(pgsql):
    return GroceryUberGwDbAgent(pgsql=pgsql)
