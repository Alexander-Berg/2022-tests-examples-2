import typing

import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/cars/create'

DEFAULT_BODY = {
    'brand': 'BMW',
    'model': 'X5',
    'color': 'Желтый',
    'year': 2019,
    'number': 'B777OP777',
    'callsign': 'B777OP777',
    'status': 'working',
}

DEFAULT_BODY_WITH_OPTIONAL_FIELDS = {
    'brand': 'BMW',
    'model': 'X5',
    'color': 'Желтый',
    'year': 2019,
    'number': 'B777OP777',
    'callsign': 'B777OP777',
    'status': 'working',
    'vin': 'COOLVIN228',
    'body_number': 'COOLBODYNUMBER228',
    'registration_cert': '12125564',
}

RESPONSE1: typing.Dict[str, typing.Any] = {
    **DEFAULT_BODY,
    'id': 'park_id0someCorrectToken',
    'park_id': 'park_id0',
}

RESPONSE2: typing.Dict[str, typing.Any] = {
    **DEFAULT_BODY_WITH_OPTIONAL_FIELDS,
    'id': 'park_id0someCorrectToken',
    'park_id': 'park_id0',
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_cars_create_without_user_ticket(
        taxi_signal_device_api_admin, parks, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('park_id0'),
                    'specifications': ['signalq'],
                },
            ],
        }

    headers = {
        **web_common.YA_TEAM_HEADERS_WITHOUT_USER_TICKET,
        'X-Park-Id': 'park_id0',
        'X-Idempotency-Token': 'someCorrectToken',
        'X-Real-Ip': '123.228.228.123',
    }
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=DEFAULT_BODY, headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'X-Ya-User-Ticket is not provided',
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'body, expected_response',
    [
        (DEFAULT_BODY, RESPONSE1),
        (DEFAULT_BODY_WITH_OPTIONAL_FIELDS, RESPONSE2),
    ],
)
async def test_cars_create(
        taxi_signal_device_api_admin,
        parks,
        body,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('park_id0'),
                    'specifications': ['signalq'],
                },
            ],
        }

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'park_id0',
        'X-Idempotency-Token': 'someCorrectToken',
        'X-Real-Ip': '123.228.228.123',
    }
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'expected_parks_code, expected_parks_msg',
    [
        ('invalid_vin', 'vehicle identification number must be correct'),
        (None, 'vehicle identification number must be correct'),
        ('invalid_year', None),
        (None, None),
    ],
)
async def test_cars_create_parks_400(
        taxi_signal_device_api_admin,
        parks,
        expected_parks_code,
        expected_parks_msg,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('park_id0'),
                    'specifications': ['signalq'],
                },
            ],
        }

    expected_response = {'code': '400', 'message': None}
    parks_response_error = {}
    if expected_parks_code is not None:
        expected_response['code'] = expected_parks_code
        parks_response_error['code'] = expected_parks_code
    if expected_parks_msg is not None:
        expected_response['message'] = expected_parks_msg
        parks_response_error['text'] = expected_parks_msg
    parks.set_cars_400_response({'error': parks_response_error})

    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': 'park_id0',
        'X-Idempotency-Token': 'someCorrectToken',
        'X-Real-Ip': '123.228.228.123',
    }
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=DEFAULT_BODY_WITH_OPTIONAL_FIELDS, headers=headers,
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == expected_response['code']

    # I don't want to hardcode userver default message answer in tests
    # So here if message is None => message can by any, I don't need to check
    if expected_response['message'] is not None:
        assert response_json['message'] == expected_response['message']
