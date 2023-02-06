import json


import pytest


ENDPOINT = '/driver/profile-view/v1/vehicles'
CAR_CREATE_ENDPOINT = '/parks/car-create'
HEADERS = {
    'X-Driver-Session': 'session1',
    'User-Agent': 'Taximeter 8.80 (562)',
    'Accept-Language': 'ru',
}


@pytest.mark.config(
    DRIVER_VEHICLES_CATEGORY=['econom'], DRIVER_VEHICLES_AMENITIES=['animals'],
)
@pytest.mark.experiments3(filename='experiments3_dvpbs_default.json')
@pytest.mark.parametrize(
    'db_id, parks_code, parks_response, expected_code, ' 'expected_response',
    [
        (
            'db_id41',
            200,
            {},
            403,
            {'code': 'WRONG_SOURCE', 'message': 'Wrong source'},
        ),
        pytest.param(
            'db_id42',
            200,
            {},
            403,
            {'code': 'WRONG_SOURCE', 'message': 'Wrong source'},
            marks=pytest.mark.driver_tags_match(
                dbid='db_id42', uuid='uuid1', tags=['selfemployed'],
            ),
        ),
        ('db_id42', 200, {'id': 'new_car'}, 200, {'vehicle_id': 'new_car'}),
        (
            'db_id42',
            400,
            {
                'error': {
                    'text': 'У вас уже добавлен автомобиль с номером НВ123124',
                },
            },
            400,
            {
                'code': 'BAD_REQUEST',
                'details': {
                    'text': 'У вас уже добавлен автомобиль с номером НВ123124',
                    'title': 'Ошибка',
                },
                'message': 'Wrong request parameters',
            },
        ),
    ],
)
async def test_driver_vehicles_post(
        taxi_driver_profile_view,
        mockserver,
        driver_authorizer,
        mock_fleet_parks_list,
        db_id,
        parks_code,
        parks_response,
        expected_code,
        expected_response,
):
    driver_authorizer.set_session(db_id, 'session1', 'uuid1')

    @mockserver.json_handler(CAR_CREATE_ENDPOINT)
    def _mock_car_create(request):
        assert request.headers['Accept-Language'] == 'ru'
        body = request.json
        assert 'callsign' in body
        body.pop('callsign')
        assert body == {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'park_id': db_id,
            'category': ['econom'],
            'amenities': ['animals'],
            'status': 'working',
            'booster_count': 0,
            'mileage': 0,
            'registration_cert': 'QX25',
            'vin': 'ABCDEFG0123456789',
        }
        return mockserver.make_response(json.dumps(parks_response), parks_code)

    response = await taxi_driver_profile_view.post(
        ENDPOINT,
        headers=HEADERS,
        params={'park_id': db_id},
        data=json.dumps(
            {
                'brand': 'Audi',
                'model': 'A1',
                'color': 'Белый',
                'year': 2015,
                'number': 'НВ123124',
                'registration_cert': 'QX25',
                'vin': 'ABCDEFG0123456789',
            },
        ),
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response
