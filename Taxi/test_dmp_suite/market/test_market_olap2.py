from dmp_suite.market.market_olap2 import get_olap2_params


def test_olap2_params():
    assert get_olap2_params('hahn', '//test', '2022-07', '2022-07-01 00:00:00') == {
        'cluster': 'hahn',
        'destination': 'clickhouse',
        'partition': '2022-07',
        'path': '//test',
        'timestamp': '2022-07-01 00:00:00T00:00:00',
    }

    assert get_olap2_params('hahn', '//test', None, '2022-07-01 00:00:00') == {
        'cluster': 'hahn',
        'destination': 'clickhouse',
        'path': '//test',
        'timestamp': '2022-07-01 00:00:00T00:00:00',
    }
