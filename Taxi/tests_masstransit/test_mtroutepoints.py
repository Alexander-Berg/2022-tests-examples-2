import copy

import pytest


BASIC_HEADERS = {'X-YaTaxi-UserId': '1'}

BASIC_REQUEST = {
    'route': [[37.664351, 55.732052], [37.685396, 55.704837]],
    'lang': 'ru',
}


@pytest.mark.parametrize(
    'dist_a,dist_b,empty_resp',
    [
        (1000, 1000, False),
        (10, 1000, True),
        (1000, 10, True),
        (None, None, False),
    ],
)
@pytest.mark.stops_file(filename='stops_extended.json')
async def test_simple(
        taxi_masstransit,
        load_json,
        load_binary,
        mockserver,
        dist_a,
        dist_b,
        empty_resp,
):
    @mockserver.json_handler('/mtrouter/masstransit/v2/route')
    def _mock_mtrouter(request):
        assert 'lang' in request.args
        assert request.args['lang'] == 'ru'
        return mockserver.make_response(
            load_binary('mtrouter_response.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(BASIC_REQUEST)
    if dist_a:
        request['max_distance_to_point_a'] = dist_a
    if dist_b:
        request['max_distance_to_point_b'] = dist_b

    response = await taxi_masstransit.post(
        'masstransit/v1/routepoints', request, headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    if empty_resp:
        assert response.json() == {'options': []}
    else:
        expected = load_json('expected_response.json')
        assert response.json() == expected


@pytest.mark.parametrize('metro_first', [True, False])
async def test_metro_first(
        taxi_masstransit, load_json, load_binary, mockserver, metro_first,
):
    @mockserver.json_handler('/mtrouter/masstransit/v2/route')
    def _mock_mtrouter(request):
        return mockserver.make_response(
            load_binary('mtrouter_response_metro_last.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(BASIC_REQUEST)
    request['metro_first'] = metro_first
    response = await taxi_masstransit.post(
        'masstransit/v1/routepoints', request, headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    resp_data = response.json()
    if metro_first:
        expected = load_json('expected_response_metro_first.json')
        assert resp_data == expected
    else:
        expected = load_json('expected_response_metro_last.json')
        assert resp_data == expected


@pytest.mark.parametrize('metro_first', [True, False])
async def test_transfer_segments(
        taxi_masstransit, load_json, load_binary, mockserver, metro_first,
):
    @mockserver.json_handler('/mtrouter/masstransit/v2/route')
    def _mock_mtrouter(request):
        return mockserver.make_response(
            load_binary('mtrouter_response_with_transfer.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(BASIC_REQUEST)
    request['metro_first'] = metro_first
    response = await taxi_masstransit.post(
        'masstransit/v1/routepoints', request, headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    resp_data = response.json()
    if metro_first:
        expected = load_json(
            'expected_response_with_transfer_metro_first.json',
        )
        assert resp_data == expected
    else:
        expected = load_json('expected_response_with_transfer_metro_last.json')
        assert resp_data == expected
