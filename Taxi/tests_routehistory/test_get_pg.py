import datetime

import pytest

from . import utils


def wipe_db(pgsql):
    cursor_ph = pgsql['routehistory_ph'].cursor()
    cursor_ph.execute('DELETE FROM routehistory_ph.phone_history2')


def create_pb_response(order_ids, load_json):
    all_orders = load_json('response_orders_pb.json')
    result = {
        'result': list(
            next(filter(lambda x, id=id: x['id'] == id, all_orders))
            for id in order_ids
        ),
    }
    if not result['result']:
        del result['result']
    return result


def create_json_response(order_ids, load_json):
    all_orders = load_json('response_orders.json')
    result = {
        'results': list(
            next(filter(lambda x, id=id: x['id'] == id, all_orders))
            for id in order_ids
        ),
    }
    return result


@pytest.mark.parametrize(
    'request_file', ['request_bad_1.json', 'request_bad_2.json'],
)
async def test_get_pg_bad(taxi_routehistory, request_file, load_json):
    request = load_json(request_file)
    headers = request['headers']
    body = request['body']
    response = await taxi_routehistory.post(
        'routehistory/get', body, headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='unsharded', marks=[]),
        pytest.param(
            id='sharded',
            marks=[
                pytest.mark.config(
                    ROUTEHISTORY_PARTITION={
                        'phone_history': [
                            {
                                'key_min': 0,
                                'key_max': 50,
                                'type': 'read_write',
                                'shard': 1,
                            },
                            {
                                'key_min': 50,
                                'key_max': 100,
                                'type': 'read_write',
                                'shard': 2,
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'cache',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                ROUTEHISTORY_CACHES={
                    'caches': {
                        '__default__': {
                            'bucket_count': 1000,
                            'part_count': 10,
                            'shift_period_ms': 100000,
                        },
                    },
                },
            ),
            id='cache',
        ),
        pytest.param(False, id='no_cache'),
    ],
)
@pytest.mark.parametrize(
    'want_proto',
    [pytest.param(True, id='proto'), pytest.param(False, id='json')],
)
@pytest.mark.parametrize(
    'request_file',
    [
        'request_1.json',
        'request_2.json',
        'request_3.json',
        'request_4.json',
        'request_5.json',
        'request_6.json',
        'request_7.json',
        'request_8.json',
        'request_9.json',
        'request_10.json',
    ],
)
async def test_get_pg(
        taxi_routehistory, request_file, want_proto, cache, load_json, pgsql,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    request = load_json(request_file)
    headers = request['headers']
    if want_proto:
        headers['Accept'] = 'application/x-protobuf'
    body = request['body']
    response = await taxi_routehistory.post(
        'routehistory/get', body, headers=headers,
    )

    def _check_result(expected_ids):
        if want_proto:
            expected = create_pb_response(expected_ids, load_json)
            actual = utils.rh_get_response_proto_to_json(response.content)
            assert actual == expected
            assert response.headers['Content-Type'] == 'application/x-protobuf'
        else:
            expected = create_json_response(expected_ids, load_json)
            assert response.json() == expected
            assert response.headers['Content-Type'] == 'application/json'

    assert response.status_code == 200
    assert response.headers['X-Data-Source'] == 'db'
    _check_result(request['expected'])

    # Wipe db and make another request
    wipe_db(pgsql)
    response = await taxi_routehistory.post(
        'routehistory/get', body, headers=headers,
    )
    assert response.status_code == 200
    if cache:
        assert response.headers['X-Data-Source'] == 'cache'
        _check_result(request['expected'])
    else:
        assert response.headers['X-Data-Source'] == 'db'
        _check_result([])


@pytest.mark.config(ROUTEHISTORY_HIDDEN_IMPORT_SOURCE=['vezet'])
async def test_get_pg_hidden_import_source(
        taxi_routehistory, load_json, pgsql,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    request = load_json('request_1.json')
    headers = request['headers']
    body = request['body']
    response = await taxi_routehistory.post(
        'routehistory/get', body, headers=headers,
    )

    expected = create_json_response(
        [
            '11111111000000000000000000000003',
            '11111111000000000000000000000002',
            '11111111000000000000000000000001',
            '11111111000000000000000000000004',
        ],
        load_json,
    )
    assert response.status_code == 200
    assert response.json() == expected
    assert response.headers['Content-Type'] == 'application/json'


@pytest.mark.xfail(reason='Known to be flaky')
@pytest.mark.parametrize(
    'add_header, ping, expected_response, expect_announce, data_source, '
    'expected_data_source, reroute_result, expect_accept_proto',
    [
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            None,  # data_source
            'rerouted_db',  # expected_data_source
            'json',  # reroute_result
            False,  # expect_accept_proto
            id='rerouted_db_1',
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            False,  # expected_response
            True,  # expect_announce
            None,  # data_source
            'db_after_reroute_error',  # expected_data_source
            'error',  # reroute_result
            False,  # expect_accept_proto
            id='reroute_error',
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            'cache',  # data_source
            'rerouted_cache',  # expected_data_source
            'json',  # reroute_result
            False,  # expect_accept_proto
            id='rerouted_cache',
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            'cache',  # data_source
            'rerouted_cache',  # expected_data_source
            'json',  # reroute_result
            True,  # expect_accept_proto
            id='rerouted_cache_proto_json',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_PROTOBUF=True)],
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            'cache',  # data_source
            'rerouted_cache',  # expected_data_source
            'proto',  # reroute_result
            True,  # expect_accept_proto
            id='rerouted_cache_proto_proto',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_PROTOBUF=True)],
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            'cache',  # data_source
            'rerouted_cache',  # expected_data_source
            'proto',  # reroute_result
            False,  # expect_accept_proto
            id='rerouted_cache_json_proto',
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            True,  # expected_response
            True,  # expect_announce
            'db',  # data_source
            'rerouted_db',  # expected_data_source
            'json',  # reroute_result
            False,  # expect_accept_proto
            id='rerouted_db_2',
        ),
        pytest.param(
            None,  # add_header
            500,  # ping
            False,  # expected_response
            True,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            False,  # expect_accept_proto
            id='failed_ping',
        ),
        pytest.param(
            'X-Rerouted',  # add_header
            200,  # ping
            False,  # expected_response
            True,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            False,  # expect_accept_proto
            id='already_rerouted_1',
        ),
        pytest.param(
            'X-Rerouted',  # add_header
            500,  # ping
            False,  # expected_response
            True,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            None,  # expect_accept_proto
            id='already_rerouted_2',
        ),
        pytest.param(
            None,  # add_header
            200,  # ping
            False,  # expected_response
            False,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            None,  # expect_accept_proto
            id='rerouting_disabled_1',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_ENABLE=False)],
        ),
        pytest.param(
            None,  # add_header
            500,  # ping
            False,  # expected_response
            False,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            None,  # expect_accept_proto
            id='rerouting_disabled_2',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_ENABLE=False)],
        ),
        pytest.param(
            'X-Rerouted',  # add_header
            200,  # ping
            False,  # expected_response
            False,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            None,  # expect_accept_proto
            id='rerouting_disabled_3',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_ENABLE=False)],
        ),
        pytest.param(
            'X-Rerouted',  # add_header
            500,  # ping
            False,  # expected_response
            False,  # expect_announce
            None,  # data_source
            'db',  # expected_data_source
            None,  # reroute_result
            None,  # expect_accept_proto
            id='rerouting_disabled_4',
            marks=[pytest.mark.config(ROUTEHISTORY_REROUTING_ENABLE=False)],
        ),
    ],
)
@pytest.mark.now('2025-03-24T16:45:17+0000')
async def test_get_pg_rerouting(
        taxi_routehistory,
        load_json,
        pgsql,
        mockserver,
        add_header,
        expected_response,
        expect_announce,
        ping,
        data_source,
        expected_data_source,
        reroute_result,
        expect_accept_proto,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    request = load_json('request_1.json')
    response_orders = request['expected']

    # pylint: disable=unused-variable
    @mockserver.handler('/ping')
    def mock_ping(mock_request):
        return mockserver.make_response('', status=ping)

    @mockserver.handler('/routehistory/rerouted-get')
    def mock_rerouted_get(mock_request):
        assert mock_request.headers['X-Rerouted']
        assert mock_request.headers['Content-Type'] == 'application/json'

        # 'Accept: */*' is added by libcurl even when not explicitly set
        accept = 'application/x-protobuf' if expect_accept_proto else '*/*'
        assert mock_request.headers['Accept'] == accept

        if reroute_result == 'error':
            return mockserver.make_response('', 500)
        headers = {}
        if data_source:
            headers['X-Data-Source'] = data_source
        if reroute_result == 'json':
            return mockserver.make_response(
                json=create_json_response(response_orders, load_json),
                headers=headers,
            )
        if reroute_result == 'proto':
            js_dict = create_pb_response(response_orders, load_json)
            binary = utils.rh_get_response_json_to_proto(js_dict)
            return mockserver.make_response(
                response=binary,
                content_type='application/x-protobuf',
                headers=headers,
            )
        assert False
        return None

    await taxi_routehistory.run_periodic_task('rerouting_announce')
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)
    cursor.execute('SELECT c FROM routehistory.rerouting c ORDER BY host')
    rerouting_table = utils.convert_pg_result(cursor.fetchall())
    expected_rerouting_table = (
        [
            {
                'host': rerouting_table[0]['host'],
                'online': datetime.datetime(2025, 3, 24, 16, 45, 17),
                'version': 0,
            },
        ]
        if expect_announce
        else []
    )
    assert rerouting_table == expected_rerouting_table
    cursor.execute('DELETE FROM routehistory.rerouting')
    cursor.execute(
        'INSERT INTO routehistory.rerouting (host, online, version)'
        f'VALUES (\'{mockserver.host}:{mockserver.port}\', '
        '\'2030-01-01T10:00:00+0000\', 0),'
        '(\'expired_host\', \'2010-01-01T10:00:00+0000\', 0)',
    )
    await taxi_routehistory.run_periodic_task('rerouting_fetch')
    await taxi_routehistory.run_periodic_task('rerouting_ping')

    headers = request['headers']
    if add_header:
        headers[add_header] = '1'
    body = request['body']
    response = await taxi_routehistory.post(
        'routehistory/get', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == create_json_response(response_orders, load_json)
    assert response.headers.get('X-Data-Source') == expected_data_source
