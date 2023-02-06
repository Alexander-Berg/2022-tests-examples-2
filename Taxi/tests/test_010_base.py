import os.path

from easytap import Tap

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')


class TstVar:
    def postgresql(self):
        return self.value + 1
    def __init__(self, value):
        self.value = value


def test_base():
    tap = Tap(9, 'Basic tests')
    tap.import_ok('dbtpl', 'импорт dbtpl')

    import dbtpl    # noqa

    agent = dbtpl.agent(SQL_DIR)
    tap.ok(agent, 'agent created')

    sql, binds = agent('select-novars.sql', {})
    tap.isa_ok(sql, str, 'sql created')
    tap.isa_ok(binds, list, 'binds created')

    @tap.subtest(2, 'immediately filter')
    def test_i(tap):    # pylint: disable=unused-variable
        sql, binds = agent('immediately.sql', {'table': 'users'})
        tap.eq_ok(binds, [], 'There is no variables to bind')
        tap.like(sql, r'(SELECT\s+"id"\s+FROM\s+"users")',
                 'Immediately filter')

    @tap.subtest(4, 'quoted insert')
    def test_q(tap):    # pylint: disable=unused-variable
        sql, binds = agent('quote.sql',
                           {'val': 123, 'name': 'Vasya', 'tablename': 'users'})
        tap.eq_ok(binds, [123, 'Vasya'], 'variables to bind')
        tap.like(sql,
                 r'SELECT\s+"id"\s+FROM\s+"users"\s+'
                 r'WHERE\s+"id"\s+=\s+\$1\s+AND\s+"name"\s+=\s+\$2',
                 'SQL text')

        sql, binds = agent('quote.sql',
                           {'val': 345, 'name': 'Petya', 'tablename': 'users'})
        tap.eq_ok(binds, [345, 'Petya'], 'variables to bind')
        tap.like(sql,
                 r'SELECT\s+"id"\s+FROM\s+"users"\s+'
                 r'WHERE\s+"id"\s+=\s+\$1\s+AND\s+"name"\s+=\s+\$2',
                 'SQL text')

    @tap.subtest(10, 'vlist')
    def test_vlist(tap):    # pylint: disable=unused-variable
        sql, binds = agent('vlist.sql', {'lst': [1, 2, 3]})
        tap.eq_ok(binds, [1, 2, 3], 'variables to bind')
        tap.eq_ok(sql, 'SELECT * FROM ($1,$2,$3)', 'sql text')

        sql, binds = agent('vlist.sql', {'lst': 1})
        tap.eq_ok(binds, [1], 'one variable[int] to bind')
        tap.eq_ok(sql, 'SELECT * FROM ($1)', 'sql text')

        sql, binds = agent('vlist.sql', {'lst': 1.0})
        tap.eq_ok(binds, [1], 'one variable[float] to bind')
        tap.eq_ok(sql, 'SELECT * FROM ($1)', 'sql text')

        sql, binds = agent('vlist.sql', {'lst': 'hello'})
        tap.eq_ok(binds, ['hello'], 'one variable[str] to bind')
        tap.eq_ok(sql, 'SELECT * FROM ($1)', 'sql text')

        sql, binds = agent('vlist.sql', {'lst': tuple()})
        tap.eq_ok(binds, [], 'empty vlist')
        tap.eq_ok(sql, 'SELECT * FROM ()', 'sql text')

    @tap.subtest(4, 'inline')
    def test_inline(tap):   # pylint: disable=unused-variable
        sql, binds = agent.inline(
            'select * FROM {{ t|i }} WHERE id = {{ id }}',
            {'t': 'user', 'id': 123})
        tap.isa_ok(sql, str, 'sql')
        tap.isa_ok(binds, list, 'binds')
        tap.eq_ok(sql, 'select * FROM user WHERE id = $1', 'sql text')
        tap.eq_ok(binds, [123], 'binds')


    @tap.subtest(4, 'postgresql method')
    def test_postgresql_method(tap):    # pylint: disable=unused-variable
        sql, binds = agent.inline('{{ o }}', {'o': TstVar(123)})
        tap.isa_ok(sql, str, 'sql')
        tap.isa_ok(binds, list, 'binds')
        tap.eq_ok(sql, '$1', 'sql text')
        tap.eq_ok(binds, [124], 'binds')

    assert tap.done_testing()
