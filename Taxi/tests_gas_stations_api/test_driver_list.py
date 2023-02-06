import base64
import json
import typing as tp

import aiohttp.web
import pytest

from tests_gas_stations_api import responses

ENDPOINT = '/v1/contractor-profiles/list'


def encode_cursor(cursor: tp.Dict):
    return base64.b64encode(json.dumps(cursor).encode('utf-8')).decode()


PARK = {
    'city_id': 'city1',
    'country_id': 'rus',
    'demo_mode': False,
    'id': 'park_with_offer',
    'is_active': True,
    'is_billing_enabled': True,
    'is_franchising_enabled': False,
    'locale': 'locale1',
    'login': 'login1',
    'name': 'super_park1',
    'provider_config': {'clid': 'clid1', 'type': 'production'},
    'tz_offset': 3,
    'geodata': {'lat': 12, 'lon': 23, 'zoom': 0},
}

CURSOR_JSON_DP = {
    'sort': {'field': 'created_at', 'direction': 'asc'},
    'park_id': 'park_test',
    'last_item': {
        'created_at': '2017-08-03T09:32:42.965+00:00',
        'driver_id': 'driver2',
    },
}

DRIVERS_DATA = [
    {
        'created_at': '1970-01-01T00:00:00+00:00',
        'contractor_profile_id': 'driver1',
        'person': {
            'full_name': {
                'first_name': 'Нурсултан',
                'middle_name': 'Васильевич',
                'last_name': 'Гамлет',
            },
        },
        'car_id': 'car1',
        'account': {'balance_limit': '1000.0000'},
        'profile': {'work_status': 'working'},
    },
    {
        'created_at': '2017-08-03T09:32:42.965Z',
        'contractor_profile_id': 'driver2',
        'person': {
            'full_name': {
                'first_name': 'Нур',
                'middle_name': 'Сул',
                'last_name': 'Тан',
            },
        },
        'profile': {'work_status': 'working'},
    },
]

DRIVER_PROFILES_RESPONSE = {
    'park_with_offer_100': {'driver_profiles': DRIVERS_DATA},
    'park_with_offer_1': {
        'driver_profiles': [DRIVERS_DATA[0]],
        'cursor': encode_cursor(CURSOR_JSON_DP),
    },
}


@pytest.fixture(name='mock_driver_profiles_list')
def _mock_driver_profiles_list(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver-profiles/list')
    def _driver_profiles_list(request):
        if request.method == 'GET':
            return {'driver_profiles': [DRIVERS_DATA[1]]}
        return DRIVER_PROFILES_RESPONSE[
            request.json['park_id'] + '_' + str(request.json['limit'])
        ]


@pytest.mark.parametrize(
    ('test_name', 'status_code', 'body'),
    [
        ('ok1', 200, {'linit': 3}),
        ('ok2', 200, {'limit': 1}),
        (
            'ok3',
            200,
            {
                'cursor': (
                    'eyJzb3J0IjogeyJmaWVsZCI6ICJjcmVhdGVkX2F0IiwgImRpcm'
                    'VjdGlvbiI6ICJhc2MifSwgInBhcmtfaWQiOiAicGFya190ZXN0'
                    'IiwgImxhc3RfaXRlbSI6IHsiY3JlYXRlZF9hdCI6ICIyMDE3LTA'
                    '4LTAzVDA5OjMyOjQyLjk2NSswMDowMCIsICJkcml2ZXJfaWQiOiA'
                    'iZHJpdmVyMiJ9fQ=='
                ),
                'limit': 12,
            },
        ),
    ],
)
async def test_contractor_profiles_list(
        taxi_gas_stations_api,
        test_name,
        status_code,
        load_json,
        gas_stations,
        mock_driver_profiles_list,
        mock_fleet_parks_list,
        body,
):
    params = {'park_id': 'park_with_offer'}
    expected_response = load_json(f'responses/{test_name}.json')
    response = await taxi_gas_stations_api.post(
        ENDPOINT, params=params, json=body,
    )
    assert response.status_code == status_code
    assert response.json() == expected_response


async def test_invalid_cursor(taxi_gas_stations_api, gas_stations, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver-profiles/list')
    def _driver_profiles_list(request):
        return aiohttp.web.json_response(
            responses.make_error('invalid_cursor', 'Invalid cursor'),
            status=400,
        )

    response = await taxi_gas_stations_api.post(
        ENDPOINT,
        params={'park_id': 'park_with_offer'},
        json={'limit': 10, 'cursor': 'strange'},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'invalid cursor'}


async def test_is_direct_partner_flag(
        taxi_gas_stations_api,
        load_json,
        gas_stations,
        mock_driver_profiles_list,
        mock_fleet_parks_list,
):
    params = {'park_id': 'park_with_offer'}
    expected_response = load_json('responses/test_is_direct_partner_flag.json')
    PARK['driver_partner_source'] = 'yandex'
    mock_fleet_parks_list.set_parks([PARK])
    response = await taxi_gas_stations_api.post(
        ENDPOINT, params=params, json={},
    )
    assert response.status_code == 200
    assert response.json() == expected_response
