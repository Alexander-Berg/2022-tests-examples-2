import os.path

from easytap import Tap

import pytest

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')

DSN = os.getenv('PG_DSN', '').replace('postgres://', 'pq://')
SKIP_COND = DSN == ''
SKIP_TEXT = 'Please export PG_DSN to run the test list'

try:
    import psycopg2
except ModuleNotFoundError:
    SKIP_COND = True
    SKIP_TEXT = 'Please install python3-postgresql first'


@pytest.mark.skipif(SKIP_COND, reason=SKIP_TEXT)
def test_db():
    import urllib.parse

    url = urllib.parse.urlparse(DSN)

    tap = Tap(4)
    tap.import_ok('dbtpl', 'import dbtpl')

    import dbtpl

    agent = dbtpl.agent(SQL_DIR, placeholders='%s')
    tap.ok(agent, 'Agent created')

    db = psycopg2.connect(None,
                          host=url.hostname,
                          port=url.port,
                          user=url.username,
                          database=url.path.replace('/', ''),
                          password=url.password)
    tap.ok(db, 'Connection established')

    sql, binds = agent('make_table.sql', {'count': 42})
    cursor = db.cursor()
    cursor.execute(sql, binds)
    res = cursor.fetchall()
    tap.eq_ok(res, list(map(lambda x: (x, str(x * 10)), range(42))),
              'результаты подготовленного запроса')

    assert tap.done_testing()
