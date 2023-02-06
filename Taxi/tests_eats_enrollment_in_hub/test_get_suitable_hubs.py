import pytest
# import json

TEST_EATS_ENROLLMENT_IN_HUB_HUBS_DATA = {
    'Московский Хаб 1': {
        'address': 'г. Москва, 1-я улица Строителей',
        'location_coordinates': {'lat': 39.60258, 'lon': 52.569089},
        'name': 'Хаб 1',
        'timezone': 'Europe/Moscow',
        'work_schedule': {
            '__default__': [
                {'from': '09:00', 'to': '13:00'},
                {'from': '14:00', 'to': '19:00'},
            ],
            'exclusions': [
                {
                    'date': '2022-01-03',
                    'schedule': [{'from': '11:00', 'to': '16:00'}],
                },
            ],
            'fri': [{'from': '09:00', 'to': '11:00'}],
            'sat': [{'from': '09:00', 'to': '12:00'}],
            'sun': [{'from': '10:00', 'to': '13:00'}],
        },
    },
    'Московский Хаб 2': {
        'address': 'г. Москва, 2-я улица Строителей',
        'location_coordinates': {'lat': 39.60258, 'lon': 52.569089},
        'name': 'Хаб 2',
        'timezone': 'Europe/Moscow',
        'work_schedule': {
            '__default__': [
                {'from': '09:00', 'to': '13:00'},
                {'from': '14:00', 'to': '18:00'},
            ],
            'sat': [
                {'from': '10:00', 'to': '12:00'},
                {'from': '14:00', 'to': '16:00'},
            ],
        },
    },
}

HEADERS = {
    'Accept-Language': 'en',
    'Content-Type': 'application/json',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.60',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.config(
    EATS_ENROLLMENT_IN_HUB_HUBS_DATA=TEST_EATS_ENROLLMENT_IN_HUB_HUBS_DATA,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    ['courier_id', 'number_of_hubs', 'status_code', 'expected_result'],
    [
        pytest.param('000000', 0, 200, 'result1.json', id='No suitable hubs'),
        pytest.param('111111', 2, 200, 'result2.json', id='2 hubs'),
        pytest.param(
            '666666', 0, 400, 'result3.json', id='error in getting courier',
        ),
    ],
)
@pytest.mark.now('2022-01-01T10:00:00+03:00')
async def test_suitable_hubs_search(
        taxi_eats_enrollment_in_hub,
        mock_get_courier_profile,
        load_json,
        courier_id,
        number_of_hubs,
        status_code,
        expected_result,
):
    HEADERS['X-YaEda-CourierId'] = courier_id
    response = await taxi_eats_enrollment_in_hub.get(
        '/driver/v1/enrollment-in-hub/v1/suitable-hubs-search',
        headers=HEADERS,
        json={},
    )
    res = response.json()
    # print(json.dumps(res, indent=4, sort_keys=True))

    assert response.status_code == status_code
    if response.status_code != 400:
        expected_result = load_json(expected_result)
        assert len(res['suitable_hubs']) == number_of_hubs
        assert res == expected_result
