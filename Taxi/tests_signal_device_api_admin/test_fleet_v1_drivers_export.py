import pytest

from tests_signal_device_api_admin import web_common

TEXT_CSV = 'text/csv'

ALL_DRIVERS = (
    'водитель,телефоны водителя,удостоверение'
    '\r\nIvanov Petr D`,+79265975310; 111111,7723306794'
    '\r\nVoditel Vtoroi,+79265975310; 2222222,7723306794'
)

EMPTY_RESPONSE = 'водитель,телефоны водителя,удостоверение'

DRIVER_PROFILE_1 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
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
        'phones': ['+79265975310', '111111'],
    },
}

DRIVER_PROFILE_2 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Vtoroi',
        'last_name': 'Voditel',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd100500',
        'phones': ['+79265975310', '2222222'],
    },
}

DRIVER_PROFILES_LIST_BOTH_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1, DRIVER_PROFILE_2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}

DRIVER_PROFILES_LIST_EMPTY_RESPONSE = {
    'driver_profiles': [],
    'offset': 0,
    'parks': [],
    'total': 0,
    'limit': 300,
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.parametrize(
    'drivers_list, accept, expected_response',
    [
        pytest.param(
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
            TEXT_CSV,
            ALL_DRIVERS,
            id='test_all',
        ),
        pytest.param(
            [DRIVER_PROFILES_LIST_EMPTY_RESPONSE],
            TEXT_CSV,
            EMPTY_RESPONSE,
            id='test_empty',
        ),
        pytest.param(
            [DRIVER_PROFILES_LIST_EMPTY_RESPONSE],
            'text/xlsx',
            None,
            id='test_xlsx',
        ),
    ],
)
async def test_v1_drivers_export_csv(
        taxi_signal_device_api_admin,
        parks,
        drivers_list,
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

    parks.set_driver_profiles_response(drivers_list)

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'p1',
        'Accept-Language': 'ru',
        'Accept': accept,
    }

    response = await taxi_signal_device_api_admin.post(
        '/fleet/signal-device-api-admin/v1/drivers/export', headers=headers,
    )

    assert response.status_code == 200, response.text
    if accept == TEXT_CSV:
        assert response.text == expected_response
        return

    assert response.content is not None
    assert 'Content-Disposition' in response.headers
