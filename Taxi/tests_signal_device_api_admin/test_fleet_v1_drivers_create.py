import copy
import typing

import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/drivers/create'

IDEMPOTENCY_TOKEN = 'someidempotencylonglongtoken'
X_REAL_IP = '122.152.124.551'

EXPECTED_FLEET_PARKS_RESPONSE = {
    'parks': [
        {
            'city_id': 'CITY_ID1',
            'country_id': 'rus',
            'demo_mode': False,
            'id': 'p1',
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'locale': 'ru',
            'login': 'LOGIN1',
            'name': 'NAME1',
            'specifications': ['signalq'],
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
        {
            'city_id': 'CITY_ID2',
            'country_id': 'rus',
            'demo_mode': False,
            'id': 'p2',
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'locale': 'ru',
            'login': 'LOGIN2',
            'name': 'NAME2',
            'specifications': ['signalq', 'taxi'],
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
        {
            'city_id': 'CITY_ID3',
            'country_id': 'rus',
            'demo_mode': False,
            'id': 'p3',
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'locale': 'ru',
            'login': 'LOGIN3',
            'name': 'NAME3',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ],
}


def _get_parks_author(ya_team_headers) -> typing.Dict:
    ticket_provider = ya_team_headers['X-Ya-User-Ticket-Provider']
    if ticket_provider == 'yandex':
        return {
            'consumer': 'signal-device-api-admin',
            'identity': {
                'type': 'passport_user',
                'id': ya_team_headers['X-Yandex-UID'],
                'client_ip': X_REAL_IP,
            },
        }
    if ticket_provider == 'yandex_team':
        return {
            'consumer': 'signal-device-api-admin',
            'identity': {
                'type': 'passport_yandex_team',
                'client_ip': X_REAL_IP,
            },
        }
    raise RuntimeError('Unknown ticket provider')


def _get_expected_parks_request(*, sdaa_request_body, author) -> typing.Dict:
    result = {**copy.deepcopy(sdaa_request_body), 'author': author}
    result['driver_profile']['providers'] = []
    result['driver_profile']['profession_id'] = 'signalq-user'

    if result['driver_profile'].get('hire_date') is None:
        result['driver_profile']['hire_date'] = '2021-01-01'
    if result['driver_profile'].get('phones') is None:
        result['driver_profile']['phones'] = []
    if result.get('biometry') is not None:
        result.pop('biometry')
    return result


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'park_id, ya_team_headers, body, expected_parks_err_response, '
    'expected_code, expected_err_response',
    [
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {'driver_profile': {'first_name': '2pac', 'last_name': 'Shakur'}},
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {
                'driver_profile': {
                    'first_name': '2pac',
                    'last_name': 'Shakur',
                },
                'biometry': {'profile_id': 'p1'},
            },
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.PARTNER_HEADERS_1,
            {'driver_profile': {'first_name': '2pac', 'last_name': 'Shakur'}},
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {
                'driver_profile': {
                    'first_name': '2pac',
                    'last_name': 'Shakur',
                    'driver_license': {'number': 'SOME_LICENSE'},
                },
            },
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {
                'driver_profile': {
                    'first_name': '2pac',
                    'last_name': 'Shakur',
                    'driver_license': {
                        'number': 'SOME_LICENSE',
                        'birth_date': '1994-01-01',
                    },
                },
            },
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {
                'driver_profile': {
                    'first_name': '2pac',
                    'last_name': 'Shakur',
                    'middle_name': 'Amaru',
                    'driver_license': {'number': 'SOME_LICENSE'},
                    'phones': ['+78005553530'],
                    'hire_date': '2020-12-12',
                    'signalq_details': {
                        'employee_number': 'some_emp_num',
                        'unit': 'some_unit',
                    },
                },
            },
            None,
            200,
            None,
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {
                'driver_profile': {
                    'first_name': '2pac',
                    'last_name': 'Shakur',
                    'signalq_details': {},
                },
            },
            None,
            400,
            {
                'code': '400',
                'message': 'signalq_details can not be an empty object',
            },
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {'driver_profile': {'first_name': '2pac', 'last_name': 'Shakur'}},
            {
                'error': {
                    'code': 'invalid_phone',
                    'text': 'some invalid phone message',
                },
            },
            400,
            {'code': 'invalid_phone', 'message': 'some invalid phone message'},
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {'driver_profile': {'first_name': '2pac', 'last_name': 'Shakur'}},
            {
                'error': {
                    'code': 'duplicate_phone',
                    'text': 'some duplicate phone message',
                },
            },
            400,
            {
                'code': 'duplicate_phone',
                'message': 'some duplicate phone message',
            },
        ),
        (
            'p1',
            web_common.YA_TEAM_HEADERS,
            {'driver_profile': {'first_name': '2pac', 'last_name': 'Shakur'}},
            {
                'error': {
                    'code': 'too_long_identification',
                    'text': 'some too long identification message',
                },
            },
            400,
            {
                'code': 'too_long_identification',
                'message': 'some too long identification message',
            },
        ),
    ],
)
async def test_drivers_create(
        taxi_signal_device_api_admin,
        mockserver,
        parks,
        pgsql,
        stq,
        stq_runner,
        park_id,
        ya_team_headers,
        body,
        expected_parks_err_response,
        expected_code,
        expected_err_response,
):
    expected_driver_id = parks.make_driver_id(
        park_id=park_id, idempotency_token=IDEMPOTENCY_TOKEN,
    )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return EXPECTED_FLEET_PARKS_RESPONSE

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profile/assign',
    )
    def _assign(request):
        request_parsed = request.json
        assert request_parsed['provider'] == 'signalq'
        assert request_parsed['old_profile'] == {
            'type': 'anonymous',
            'id': 'p1',
        }
        assert request_parsed['new_profile'] == {
            'type': 'park_driver_profile',
            'id': f'{park_id}_{expected_driver_id}',
        }

        return mockserver.make_response(json={}, status=200)

    if expected_parks_err_response is not None:
        parks.set_drivers_create_400_response(expected_parks_err_response)
    else:
        author = _get_parks_author(ya_team_headers)
        parks.set_drivers_create_body(
            _get_expected_parks_request(sdaa_request_body=body, author=author),
        )

    headers = {
        **ya_team_headers,
        'X-Park-Id': park_id,
        'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
        'X-Real-IP': X_REAL_IP,
    }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {'id': expected_driver_id}
        if body.get('biometry') is not None:
            expected_response['is_biometry_profile_processing'] = True
        assert response.json() == expected_response
        return

    if expected_err_response is not None:
        assert response.json() == expected_err_response
