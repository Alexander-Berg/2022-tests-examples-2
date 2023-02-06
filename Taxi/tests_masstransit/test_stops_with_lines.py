import copy

import pytest

DEFAULT_REQUEST = {'bbox': [40.00005, 40.00005, 40.01, 40.01]}

DEFAULT_HEADERS = {'X-YaTaxi-UserId': '0'}

URI = '4.0/masstransit/v1/stops_with_lines'


@pytest.mark.mtinfo(v2_stop='mtinfo_stop.json')
@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
    },
)
async def test_basic(taxi_masstransit, mockserver, load_json, load_binary):
    request = copy.deepcopy(DEFAULT_REQUEST)
    response = await taxi_masstransit.post(
        URI, request, headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected_answer.json')


@pytest.mark.stops_file(filename='stops.json')
@pytest.mark.config(
    MASSTRANSIT_STOPS_IMAGE_TAGS={
        'tramway': 'tramway_tag',
        'stop': 'stop_tag',
        'metro': 'metro_tag',
    },
)
async def test_without_lines(
        taxi_masstransit, mockserver, load_json, load_binary,
):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['fetch_lines'] = False
    response = await taxi_masstransit.post(
        URI, request, headers=DEFAULT_HEADERS,
    )

    expected_answer = load_json('expected_answer.json')
    del expected_answer['lines']
    for stop in expected_answer['stops']:
        del stop['line_ids']

    assert response.status_code == 200
    assert response.json() == expected_answer
