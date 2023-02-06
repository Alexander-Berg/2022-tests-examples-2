import pytest

from tests_signal_device_api_admin import web_common

ALL_CARS = (
    'статус,позывной автомобиля,бренд,модель,год,'
    'номер автомобиля,цвет,стс,vin,пробег'
    '\r\nработает,n123iu987,,,,'
    ',,123,11111111,10'
    '\r\nна техосмотре,t123er987,BMW,BMW X6,2007,'
    'T123ER987,белый,982,2222222,7'
)

CARS_LIST_RESPONSE = {
    'cars': [
        {
            'id': 'car1',
            'vin': '11111111',
            'callsign': 'n123iu987',
            'mileage': 10,
            'status': 'working',
            'registration_cert': '123',
        },
        {
            'id': 'car2',
            'color': 'Белый',
            'number': 'T123ER987',
            'vin': '2222222',
            'model': 'BMW X6',
            'callsign': 't123er987',
            'mileage': 7,
            'brand': 'BMW',
            'year': 2007,
            'status': 'tech_inspection',
            'registration_cert': '982',
        },
    ],
}


@pytest.mark.parametrize(
    'accept, expected_response',
    [pytest.param('text/csv', ALL_CARS), pytest.param('text/xlsx', None)],
)
async def test_cars_export_ok(
        taxi_signal_device_api_admin,
        parks,
        accept,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks(request):
        return {
            'parks': [
                {
                    'city_id': 'CITY_ID',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': 'p1',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'LOGIN',
                    'name': 'NAME',
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {'statuses': []}

    parks.set_cars_list_response(CARS_LIST_RESPONSE)

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'p1',
        'Accept-Language': 'ru',
        'Accept': accept,
    }

    response = await taxi_signal_device_api_admin.post(
        '/fleet/signal-device-api-admin/v1/cars/export', headers=headers,
    )

    assert response.status_code == 200, response.text
    assert parks.cars_list.times_called == 1
    if accept == 'text/csv':
        assert response.text == expected_response
        return

    assert response.content is not None
    assert 'Content-Disposition' in response.headers
