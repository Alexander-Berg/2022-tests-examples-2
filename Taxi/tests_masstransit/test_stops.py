import copy

import pytest

DEFAULT_REQUEST = {'position': [40, 40], 'lang': 'ru_Ru'}

DEFAULT_HEADERS = {'X-YaTaxi-UserId': '0'}


@pytest.mark.parametrize(
    'position, stops_count, types',
    [
        ([40, 40], 1, ['stop']),
        ([40, 40], 1, ['exit']),
        ([40, 40], 1, ['station']),
        ([40, 40], 3, ['stop', 'exit', 'station']),
        ([40.5, 40], 0, ['stop', 'exit', 'station']),
    ],
)
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
    },
)
async def test_stops(
        taxi_masstransit,
        mockserver,
        load_json,
        load_binary,
        position,
        stops_count,
        types,
):
    @mockserver.json_handler('/mtinfo/v2/stop')
    def _mock_mtinfo(request):
        return mockserver.make_response(
            load_binary('mtinfo_response.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['position'] = position
    request['types'] = types
    response = await taxi_masstransit.post(
        '/v1/stops', request, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['stops']) == stops_count
    if stops_count == 1:
        assert len(data['stops']) == 1
        assert response.json() == load_json(
            'stops_response_' + types[0] + '_type.json',
        )
    elif stops_count == 3:
        assert response.json() == load_json('stops_response.json')
    else:
        assert not data['stops']


async def test_stops_empty(taxi_masstransit):
    response = await taxi_masstransit.post(
        '/v1/stops', DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['stops']


@pytest.mark.experiments3(filename='add_shuttle_exp.json')
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
        'shuttle': 'shuttle_tag',
    },
)
async def test_stops_v2(taxi_masstransit, mockserver, load_json, load_binary):
    @mockserver.json_handler('/mtinfo/v2/stop')
    def _mock_mtinfo(request):
        return mockserver.make_response(
            load_binary('mtinfo_response.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['requested_stops_num'] = 3
    request['requested_data'] = ['stops', 'stops_transport_types']
    request['bbox'] = [40.0, 40.0, 40.01, 40.01]
    request['types'] = ['stop', 'exit', 'station']
    response = await taxi_masstransit.post(
        '/v2/stops', request, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected_resp = load_json('stops_response_extra_stop.json')
    expected_stops_types = copy.deepcopy(
        expected_resp['stops_transport_types'],
    )
    expected_resp.pop('stops_transport_types')
    resp_data = response.json()
    resp_stops_types = copy.deepcopy(resp_data['stops_transport_types'])
    resp_data.pop('stops_transport_types')
    resp_data['stops'] = sorted(
        resp_data['stops'], key=lambda stop: stop['info']['id'],
    )
    assert resp_data == expected_resp
    for stops_transport_type in resp_stops_types:
        assert stops_transport_type in expected_stops_types
        expected_stops_types.remove(stops_transport_type)
    assert not expected_stops_types


@pytest.mark.experiments3(filename='add_shuttle_exp.json')
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
        'shuttle': 'shuttle_tag',
    },
)
@pytest.mark.parametrize(
    'expected_stop_names',
    [
        pytest.param(
            [
                'Shuttle stop 1 tanker key',
                'Shuttle stop 2',
                'exit_name',
                'station_name',
            ],
            marks=pytest.mark.translations(
                client_messages={
                    'shuttle_control.stops.shuttle_stop_1': {
                        'ru': 'Shuttle stop 1 tanker key',
                    },
                },
            ),
        ),
        ['Shuttle stop', 'Shuttle stop 2', 'exit_name', 'station_name'],
    ],
)
async def test_stops_v2_name_translation(
        taxi_masstransit,
        mockserver,
        load_json,
        load_binary,
        expected_stop_names,
):
    @mockserver.json_handler('/mtinfo/v2/stop')
    def _mock_mtinfo(request):
        return mockserver.make_response(
            load_binary('mtinfo_response.bin'),
            content_type='application/x-protobuf',
        )

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['requested_stops_num'] = 3
    request['requested_data'] = ['stops', 'stops_transport_types']
    request['bbox'] = [40.0, 40.0, 40.01, 40.01]
    request['types'] = ['stop', 'exit', 'station']
    response = await taxi_masstransit.post(
        '/v2/stops', request, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    resp_data = response.json()

    stop_names = sorted([stop['info']['name'] for stop in resp_data['stops']])
    assert stop_names == expected_stop_names
