import pytest

from . import utils


@pytest.mark.parametrize(
    'cache',
    [
        pytest.param(
            True,
            id='cache',
            marks=[
                pytest.mark.config(
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
            ],
        ),
        pytest.param(False, id='no_cache'),
    ],
)
@pytest.mark.parametrize(
    'want_proto',
    [pytest.param(True, id='proto'), pytest.param(False, id='json')],
)
@pytest.mark.parametrize(
    'request_file, expected_proto, expected_json',
    [
        ('request_1.json', 'response_1_pb.json', 'response_1.json'),
        ('request_2.json', 'response_2_pb.json', 'response_2.json'),
    ],
)
async def test_search_get(
        taxi_routehistory,
        load_json,
        pgsql,
        cache,
        want_proto,
        request_file,
        expected_proto,
        expected_json,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    request = load_json(request_file)
    if want_proto:
        request['headers']['Accept'] = 'application/x-protobuf'
    response = await taxi_routehistory.post(
        'routehistory/search-get', request['body'], headers=request['headers'],
    )

    def _check_result_full():
        if want_proto:
            js_dict = utils.rh_search_get_response_proto_to_json(
                response.content,
            )
            expected_js_dict = load_json(expected_proto)
            assert js_dict == expected_js_dict
            assert response.headers['Content-Type'] == 'application/x-protobuf'
        else:
            assert response.json() == load_json(expected_json)
            assert response.headers['Content-Type'] == 'application/json'

    def _check_result_empty():
        if want_proto:
            assert response.content == b''
            assert response.headers['Content-Type'] == 'application/x-protobuf'
        else:
            assert response.json() == {'results': []}
            assert response.headers['Content-Type'] == 'application/json'

    assert response.status_code == 200
    _check_result_full()
    # Wipe the db
    cursor = pgsql['routehistory'].cursor()
    cursor.execute('DELETE FROM routehistory.search_history')
    # come again
    response = await taxi_routehistory.post(
        'routehistory/search-get', request['body'], headers=request['headers'],
    )
    assert response.status_code == 200
    if cache:
        _check_result_full()
    else:
        _check_result_empty()
