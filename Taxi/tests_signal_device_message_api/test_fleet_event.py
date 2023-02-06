import base64
import json
import time
import typing

import jwt
import pytest

ENDPOINT = '/fleet/signal-device-message-api/v1/event?jwt_signature={jwt_signature}'  # noqa: E501 pylint: disable=line-too-long

PUB_KEY = (
    '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE'
    'oHvMXvcDm59Av39Rh5Qee/E3+Eby\n7tH7UmkZWbnwFiK+QnYyB0CdLM8uZOPd7M'
    'gbJPezP39hL+LOQKR4pAxhyg==\n-----END PUBLIC KEY-----\n'
)

USER_TICKET = (
    '3:user:CA4Q__________9_GhsKAggqECoaBH'
    'JlYWQaBXdyaXRlINKF2MwEKAM:FmLcx6glId9f'
    'VYjhFTD69vUVDyMcawZ0z7En9Q0g6fsioFNEq'
    'dMhvEyx4bl25SFWFjjVnGBs-pPOpPWsqC4JmHV'
    'STH8lFgoAqeOb5B3D5g1t20V0NwxuAU9EIzkQ'
    'eE8a6cMbi4r6-lvAkUZZmefXbMvQddk_r1pHBg'
    'S--V-qAU4'
)

JWT_HS_256_ENCRYPTION_KEY = 'RkFFRTRDQTNDMzBFRTE4MTQ4Q0UzQURBMzc0NjY0OTg3RDlERDdDQzg0QjA3MzEyNDhCNDI3MDBFNTIxOTkxRQ=='  # noqa: E501 pylint: disable=line-too-long
SERIAL_NUMBER = '123'


def _parse_jwt_validate_base(request):
    request_json = json.loads(request.get_data())

    data = base64.b64decode(request_json.pop('data'))
    decoded = jwt.decode(data, PUB_KEY, algorithms=['ES256'])
    iat = decoded.pop('iat')
    exp = decoded.pop('exp')
    assert iat + 30 == exp

    receiver_id = decoded['meta'].pop('receiver_id')
    assert receiver_id != ''

    assert request_json == {
        'registry_id': 'xxx',
        'topic': '$devices/xyz/commands',
    }
    assert request.headers['Authorization'] == 'Bearer xzxzxz123'

    return decoded


def get_jwt_signature(
        serial_number: typing.Optional[str],
        unix_timestamp: typing.Optional[int],
        event_type: typing.Optional[str],
        park_id: typing.Optional[str],
) -> str:
    jwt_hs_256_encryption_key = base64.b64decode(JWT_HS_256_ENCRYPTION_KEY)

    payload = {
        'serial_number': serial_number,
        'iat': unix_timestamp,
        'event_type': event_type,
        'park_id': park_id,
    }
    if not serial_number:
        payload.pop('serial_number')
    if not unix_timestamp:
        payload.pop('iat')
    if not event_type:
        payload.pop('event_type')
    if not park_id:
        payload.pop('park_id')
    token = jwt.encode(payload, jwt_hs_256_encryption_key, algorithm='HS256')
    return str(token)


@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
@pytest.mark.parametrize(
    'serial_number, unix_timestamp, park_id, jwt_signature, expected_code',
    [
        (SERIAL_NUMBER, int(time.time()), None, None, 200),
        (
            SERIAL_NUMBER,
            int(time.time() - 100500),
            None,
            None,
            403,
        ),  # ttl expired
        (
            SERIAL_NUMBER,
            int(time.time() - 100500),
            'park_id_with_eternal_ttl',
            None,
            200,
        ),
        (
            SERIAL_NUMBER,
            int(time.time()),
            None,
            'some_unparseable_signature',
            400,
        ),  # bad jwt
        (
            None,
            int(time.time()),
            None,
            None,
            400,
        ),  # no serial_number in payload
        (SERIAL_NUMBER, None, None, None, 400),  # no iat in payload
        (
            SERIAL_NUMBER,
            int(time.time()),
            None,
            get_jwt_signature(SERIAL_NUMBER, int(time.time()), None, None)
            + 'some_shit',
            403,
        ),  # bad signature
    ],
)
@pytest.mark.config(
    SIGNAL_DEVICE_MESSAGE_API_EVENT_RAISE_URL_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'max_url_uses_number': 1,
            'ttl_seconds': 3600,
        },
        'park_id_with_eternal_ttl': {
            'enabled': True,
            'max_url_uses_number': 1,
            'ttl_seconds': 2100000000,
        },
    },
    SIGNAL_DEVICE_MESSAGE_API_EVENT_RAISE_EVENTS_WHITELIST=['support_tired'],
)
async def test_event_raise(
        taxi_signal_device_message_api,
        mockserver,
        serial_number,
        unix_timestamp,
        park_id,
        jwt_signature,
        expected_code,
):
    @mockserver.json_handler(
        '/iot-data-api-cloud/iot-devices/v1/registries/xxx/publish',
    )
    def _accept_message(request):
        decoded = _parse_jwt_validate_base(request)
        assert decoded == {
            'meta': {'seconds_to_expire': 30, 'serial_number': SERIAL_NUMBER},
            'payload': {
                'command_type': 'event_raise',
                'command_id': 1,
                'command_version': 1,
                'command_payload': {'name': 'support_tired', 'meta': '{}'},
            },
            'iss': 'signal_device_message_api',
        }
        return {}

    if not jwt_signature:
        jwt_signature = get_jwt_signature(
            serial_number, unix_timestamp, None, park_id,
        )

    response = await taxi_signal_device_message_api.get(
        ENDPOINT.format(jwt_signature=jwt_signature),
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Idempotency-Token': '123',
        },
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        return
    assert response.json() == {'command_id': 1}

    response = await taxi_signal_device_message_api.get(
        ENDPOINT.format(jwt_signature=jwt_signature),
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Idempotency-Token': '123',
        },
    )
    assert (
        response.status_code == 403
    ), response.text  # number of url's uses expired


@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_MESSAGE_API_EVENT_RAISE_URL_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'max_url_uses_number': 1,
            'ttl_seconds': 3600,
        },
    },
    SIGNAL_DEVICE_MESSAGE_API_EVENT_RAISE_EVENTS_WHITELIST=[
        'support_tired',
        'seatbelt',
    ],
)
async def test_default_event_raise(taxi_signal_device_message_api, mockserver):
    @mockserver.json_handler(
        '/iot-data-api-cloud/iot-devices/v1/registries/xxx/publish',
    )
    def _accept_message(request):
        decoded = _parse_jwt_validate_base(request)
        assert decoded == {
            'meta': {'seconds_to_expire': 30, 'serial_number': SERIAL_NUMBER},
            'payload': {
                'command_type': 'event_raise',
                'command_id': 1,
                'command_version': 1,
                'command_payload': {'name': 'seatbelt', 'meta': '{}'},
            },
            'iss': 'signal_device_message_api',
        }
        return {}

    jwt_signature = get_jwt_signature(
        SERIAL_NUMBER, int(time.time()), 'seatbelt', None,
    )

    response = await taxi_signal_device_message_api.get(
        ENDPOINT.format(jwt_signature=jwt_signature),
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Idempotency-Token': '123',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'command_id': 1}
