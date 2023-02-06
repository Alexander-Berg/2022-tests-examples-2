import pytest

from taxi_tests.plugins import pgsql

pytest_plugins = ['taxi_tests.plugins.pgsql.deprecated']


@pytest.mark.parametrize('dbname', ['foo', 'bar'])
def test_load_sqlconfig(dbname):
    connections_string = (
        'host=/tmp/testsuite-postgresql user=testsuite dbname=%s' % dbname
    )
    # pylint: disable=protected-access
    connection = pgsql._load_sqlconfig(connections_string)
    assert connection
    assert connection.tables


@pytest.mark.parametrize('database, tables_count', [
    ('foo', 1),
    ('bar', 2),
])
def test_sql_databases(sql_databases, database, tables_count):
    database = getattr(sql_databases, database)
    assert database
    assert database.conn
    assert tables_count == len(database.tables)


def _get_cursor_checked(db):
    assert db
    cursor = db.conn.cursor()
    assert cursor
    return cursor


def _check_field_selection(
        table_name, column_name, entity_id, name_expected, sql_db,
):
    cursor = _get_cursor_checked(sql_db)
    if not isinstance(entity_id, int):
        entity_id = '\'%s\'' % entity_id

    cursor.execute(
        'SELECT %s FROM %s WHERE id = %s;' % (
            column_name, table_name, entity_id,
        ),
    )

    rows = cursor.fetchall()
    if name_expected:
        assert rows
        assert len(rows) == 1
        assert rows[0][0] == name_expected
    else:
        assert not rows


@pytest.mark.sql(
    'foo', 'INSERT INTO users (id, name) VALUES '
           '(\'id0\', \'testsuite\'), '
           '(\'id1\', \'userver\'), '
           '(\'id2\', \'backend-cpp\');',
)
@pytest.mark.parametrize('user_id, name_expected', [
    ('id0', 'testsuite'),
    ('id1', 'userver'),
    ('id2', 'backend-cpp'),
    ('unknown', None),
])
def test_foo(user_id, name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, name_expected, sql_databases.foo,
    )


@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'id\', \'name\');',
    'INSERT INTO users (id, name) VALUES (\'id\', \'testsuite\') '
    'ON CONFLICT (id) DO UPDATE SET name = \'testsuite\';',
])
@pytest.mark.parametrize('user_id, name_expected', [
    ('id0', None),
    ('id1', None),
    ('id2', None),
    ('id', 'testsuite'),
])
def test_foo_cleared(user_id, name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, name_expected, sql_databases.foo,
    )


@pytest.mark.sql('bar', [
    'INSERT INTO state.services (id, name) VALUES (100, \'service_name\');',
    'INSERT INTO log.messages (id, service_id, timestamp, message) VALUES ('
    '1, 100, \'2018-04-04 20:00:00\', \'log message text\');',
])
@pytest.mark.parametrize('log_id, log_message', [
    (1, 'log message text'),
    (0, None),
])
def test_bar_with_foreigh_key(sql_databases, log_id, log_message):
    _check_field_selection(
        'state.services', 'name', 100, 'service_name', sql_databases.bar,
    )
    _check_field_selection(
        'log.messages', 'message', log_id, log_message, sql_databases.bar,
    )


def _foobar_parametrize():
    return pytest.mark.parametrize(
        'user_id, service_id, user_name_expected, service_name_expected',
        [
            ('user_id', 32167, 'user_name', 'service_name'),
            ('err', 366, None, None),
        ],
    )


@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'user_id\', \'user_name\');',
])
@pytest.mark.sql('bar', [
    'INSERT INTO state.services (id, name) VALUES (32167, \'service_name\');',
])
@_foobar_parametrize()
def test_foobar(user_id, service_id, user_name_expected, service_name_expected,
                sql_databases):
    _check_foobar(user_id, service_id, user_name_expected,
                  service_name_expected, sql_databases)


@pytest.mark.sql(foo='multi', bar='multi')
@_foobar_parametrize()
def test_foobar_from_files(user_id, service_id, user_name_expected,
                           service_name_expected, sql_databases):
    _check_foobar(user_id, service_id, user_name_expected,
                  service_name_expected, sql_databases)


@pytest.mark.sql(foo='multi')
@pytest.mark.sql(bar='multi')
@_foobar_parametrize()
def test_foobar_from_files_multi(user_id, service_id, user_name_expected,
                                 service_name_expected, sql_databases):
    _check_foobar(user_id, service_id, user_name_expected,
                  service_name_expected, sql_databases)


def _check_foobar(user_id, service_id, user_name_expected,
                  service_name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, user_name_expected, sql_databases.foo,
    )

    _check_field_selection(
        'state.services', 'name', service_id, service_name_expected,
        sql_databases.bar,
    )


@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'id0\', \'user_name0\');',
])
@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'id1\', \'user_name1\');',
], foo='default')
@pytest.mark.parametrize('user_id, user_name_expected', [
    ('id0', 'user_name0'),
    ('id1', 'user_name1'),
    ('id2', None),
    ('id3', 'user_name_default'),
])
def test_multiple_foo_usage(user_id, user_name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, user_name_expected, sql_databases.foo,
    )


@pytest.mark.sql(foo='test')
@pytest.mark.parametrize('user_id, user_name_expected', [
    ('id0', None),
    ('id1', None),
    ('id2', None),
    ('id3', 'user_name_custom'),
])
def test_foo_file_usage(user_id, user_name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, user_name_expected, sql_databases.foo,
    )


@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'id0\', \'user_name0\');',
])
@pytest.mark.sql(foo='test')
@pytest.mark.parametrize('user_id, user_name_expected', [
    ('id0', 'user_name0'),
    ('id1', None),
    ('id2', None),
    ('id3', 'user_name_custom'),
])
def test_multiple_combo_foo_usage(user_id, user_name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, user_name_expected, sql_databases.foo,
    )


@pytest.mark.sql('foo', [
    'INSERT INTO users (id, name) VALUES (\'id0\', \'user_name0\');',
], foo='test')
@pytest.mark.parametrize('user_id, user_name_expected', [
    ('id0', 'user_name0'),
    ('id1', None),
    ('id2', None),
    ('id3', 'user_name_custom'),
])
def test_combo_foo_usage(user_id, user_name_expected, sql_databases):
    _check_field_selection(
        'users', 'name', user_id, user_name_expected, sql_databases.foo,
    )


@pytest.mark.parametrize('arg,expected', [
    ('host=foo user=bar dbname=',
     'host=foo user=bar dbname='),
    ('host=foo user=bar dbname=bar',
     'host=foo user=bar dbname=bar'),
    ('host=foo dbname=bar user=bar',
     'host=foo user=bar dbname=bar'),
])
@pytest.mark.nofilldb()
def test_base_connstr(arg, expected):
    # pylint: disable=protected-access
    assert pgsql._build_base_connstr(arg) == expected
