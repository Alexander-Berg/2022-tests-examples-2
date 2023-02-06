import pytest
import unittest.mock
import dmp_suite.yt.task.etl.query as etl_query
import connection.yt


@pytest.mark.parametrize(
    'query, pool, expected', [
        ('SELECT * FROM table', None, 'SELECT * FROM table'),
        ('SELECT * FROM table', 'test', "PRAGMA yt.Pool='test';\nSELECT * FROM table"),
    ]
)
def test_pragma_addition(query, pool, expected):
    actual = etl_query.add_pool_pragma_to_query(query, pool)
    assert actual == expected


@pytest.mark.parametrize(
    'pool', [None, 'test']
)
def test_pool_resolution_for_valid_non_pool_instances(pool):
    actual = etl_query.resolve_pool_value(pool)
    expected = pool
    assert actual == expected


def test_pool_resolution_for_unsupported_value():
    class Pool(object):
        pass

    pool = Pool()
    with pytest.raises(etl_query.YTPoolSubstitutionError):
        etl_query.resolve_pool_value(pool)


@pytest.mark.parametrize(
    'mocker, pool, expected', [
        (unittest.mock.MagicMock(return_value=None), connection.yt.Pool.RESEARCH, None),
        (unittest.mock.MagicMock(return_value='resolved'), connection.yt.Pool.RESEARCH, 'resolved'),
    ]
)
def test_pool_resolution_if_get_pool_value_returns_valid_value(mocker, pool, expected):
    with unittest.mock.patch('dmp_suite.yt.task.etl.query.get_pool_value', mocker):
        actual = etl_query.resolve_pool_value(pool)
    assert actual == expected


def test_pool_resolution_if_get_pool_value_returns_invalid_value():
    class Pool(object):
        pass
    mocker = unittest.mock.MagicMock(return_value=Pool())
    pool = connection.yt.Pool.RESEARCH
    with unittest.mock.patch('dmp_suite.yt.task.etl.query.get_pool_value', mocker):
        with pytest.raises(etl_query.YTPoolSubstitutionError):
            etl_query.resolve_pool_value(pool)


@pytest.mark.parametrize(
    'query, expected', [
        ('', False),
        ('SELECT * from test', False),
        ("pragma pool='test'; SELECT * from test", False),
        ("pragma yt.Pool='test'; SELECT * from test", True),
        ("PRAGMA yt.Pool='test'; SELECT * from test", True),
        ("PRAGMA yt.Pool = 'test';\nSELECT * from test", True),
    ],
)
def test_pragma_validation(query, expected):
    actual = etl_query.query_has_pool_provided(query)
    assert actual == expected
