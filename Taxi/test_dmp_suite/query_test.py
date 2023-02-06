from dmp_suite.query import QueryBuilder
from dmp_suite.clickhouse.console_client import ConsoleQuery
from dmp_suite.yql.operation import YqlQuery, YqlSelect
from mock import patch


def _test_from_string(cls):
    obj = cls.from_string('SELECT 1')
    assert isinstance(obj, cls)
    assert isinstance(obj._query, str)


def test_from_string():
    _test_from_string(YqlQuery)
    _test_from_string(YqlSelect)
    with patch('connection.clickhouse.get_connection_settings') as conn_mock:
        conn_mock.return_value = None
        _test_from_string(ConsoleQuery)


def test_query_params():
    query = QueryBuilder.from_string('test').add_params(a=1)
    assert query.params == dict(a=1)
    query.params['a'] = 2
    assert query.params == dict(a=1)
