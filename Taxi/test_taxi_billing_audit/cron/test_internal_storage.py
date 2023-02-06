from taxi_billing_audit.internal import storage


async def test_get_yql_pragma():
    config = {
        '__default__': [{'name': 'yt.DefaultMaxJobFails', 'value': '3'}],
        'my_check': [
            {'name': 'yt.DataSizePerJob', 'value': '10G'},
            {'name': 'AnsiInForEmptyOrNullableItemsCollections'},
        ],
    }
    assert storage.get_yql_pragma(config, 'my_check') == (
        'PRAGMA yt.DataSizePerJob = "10G";\n'
        'PRAGMA AnsiInForEmptyOrNullableItemsCollections;'
    )
    assert (
        storage.get_yql_pragma(config, 'my_second_check')
        == 'PRAGMA yt.DefaultMaxJobFails = "3";'
    )
