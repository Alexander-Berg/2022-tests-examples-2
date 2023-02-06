import pytest

from tests_signal_device_api_admin import web_common


ALL_EVENTS = (
    'номер автомобиля,номер устройства,imei,версии ПО устройства,'
    'телефоны водителя,удостоверение,водитель,статус'
    '\r\nО122КХ777,AB1,990000862471854,2.31-2,+79265975310; '
    '+1231234,7723306794,Ivanov Petr D`,Работает'
    '\r\nО122КХ178,AB12FE45DD,351756051523999,2.31.32-3'
    ',,,,Не работает с 2020-08-11T17:50:00+0300'
    '\r\n,FFEE33,,,,,,Не работает'
    '\r\n,FFFDEAD4,,,,,,Удалена'
)

FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'data': {'car_id': 'car1', 'number': 'О122КХ777'},
            'park_id_car_id': 'p1_car1',
            'revision': '0_1574328384_71',
        },
        {
            'data': {'car_id': 'car2', 'number': 'О122КХ178'},
            'park_id_car_id': 'p1_car2',
            'revision': '0_1574328384_71',
        },
    ],
}

DRIVER_PROFILE_1 = {
    'car': {'id': 'car1', 'number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd1',
        'phones': ['+79265975310', '+1231234'],
    },
}

DRIVER_PROFILES_LIST_SINGLE_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

EMPTY_CARS_LIST_RESPONSE = {'cars': [], 'offset': 0, 'limit': 100, 'total': 0}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize(
    'accept, expected_response',
    [pytest.param('text/csv', ALL_EVENTS), pytest.param('text/xlsx', None)],
)
async def test_v1_devices_export_csv(
        taxi_signal_device_api_admin,
        mockserver,
        fleet_vehicles,
        parks,
        accept,
        expected_response,
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
                    'specifications': ['signalq'],
                },
            ],
        }

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        return {'statuses': []}

    fleet_vehicles.set_fleet_vehicles_response(FLEET_VEHICLES_RESPONSE)
    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_SINGLE_RESPONSE)
    parks.set_cars_list_response(EMPTY_CARS_LIST_RESPONSE)

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'p1',
        'Accept-Language': 'ru',
        'Accept': accept,
    }

    response = await taxi_signal_device_api_admin.post(
        '/fleet/signal-device-api-admin/v1/devices/export', headers=headers,
    )

    assert response.status_code == 200, response.text
    if accept == 'text/csv':
        assert response.text == expected_response
        return

    assert response.content is not None
    assert 'Content-Disposition' in response.headers
