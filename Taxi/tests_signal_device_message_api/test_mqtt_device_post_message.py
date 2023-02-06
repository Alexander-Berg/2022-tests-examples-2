import base64
import json

import jwt
import pytest

ENDPOINT_INTERNAL = '/internal/v1/signal-device-message-api/device/v1/message'

ENDPOINT_EXTERNAL = '/fleet/signal-device-message-api/v1/device/message'

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


def _parse_jwt_validate_base(request):
    request_json = json.loads(request.get_data())

    data = base64.b64decode(request_json.pop('data'))
    decoded = jwt.decode(data, PUB_KEY, algorithms=['ES256'])
    iat = decoded.pop('iat')
    exp = decoded.pop('exp')
    assert iat + 69 == exp

    receiver_id = decoded['meta'].pop('receiver_id')
    assert receiver_id != ''

    assert request_json == {
        'registry_id': 'xxx',
        'topic': '$devices/xyz/commands',
    }
    assert request.headers['Authorization'] == 'Bearer xzxzxz123'

    return decoded


@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
async def test_config_get(
        taxi_signal_device_message_api, testpoint, redis_store, mockserver,
):
    @testpoint('session_id')
    def set_session(session_id):
        return session_id

    expected_cmd_id = 1

    @mockserver.json_handler(
        '/iot-data-api-cloud/iot-devices/v1/registries/xxx/publish',
    )
    def _accept_message(request):
        decoded = _parse_jwt_validate_base(request)

        assert decoded == {
            'meta': {'seconds_to_expire': 69, 'serial_number': '123'},
            'payload': {
                'command_type': 'config_get',
                'command_id': expected_cmd_id,
                'command_version': 1,
                'requested_config': 'xxx',
            },
            'iss': 'signal_device_message_api',
        }
        return {}

    json_request = {
        'meta': {'serial_number': '123', 'seconds_to_expire': 69},
        'payload': {
            'command_type': 'config_get',
            'command_version': 1,
            'requested_config': 'xxx',
        },
    }

    response = await taxi_signal_device_message_api.post(
        ENDPOINT_INTERNAL,
        json=json_request,
        headers={'X-Idempotency-Token': '123'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'command_id': 1}

    session_id = (await set_session.wait_call())['session_id']

    assert redis_store.get(f'Mqtt:Sessions:{session_id}:MaxCmdId') == b'1'
    assert redis_store.get(f'Mqtt:Sessions:{session_id}:MaxCmdId') == b'1'
    assert (
        redis_store.get(f'Mqtt:Sessions:{session_id}:TokensCmdIds:123') == b'1'
    )
    assert redis_store.hgetall(f'Mqtt:Device:Commands:{session_id}:123:1') == {
        b'waiting_for_response': b'true',
    }

    # retry
    response = await taxi_signal_device_message_api.post(
        ENDPOINT_INTERNAL,
        json=json_request,
        headers={'X-Idempotency-Token': '123'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'command_id': 1}
    assert redis_store.get(f'Mqtt:Sessions:{session_id}:MaxCmdId') == b'1'

    assert (
        redis_store.get(f'Mqtt:Sessions:{session_id}:TokensCmdIds:123') == b'1'
    )

    # another token
    expected_cmd_id = 2
    response = await taxi_signal_device_message_api.post(
        ENDPOINT_INTERNAL,
        json=json_request,
        headers={'X-Idempotency-Token': '456'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'command_id': 2}
    assert redis_store.get(f'Mqtt:Sessions:{session_id}:MaxCmdId') == b'2'
    assert (
        redis_store.get(f'Mqtt:Sessions:{session_id}:TokensCmdIds:456') == b'2'
    )


@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
async def test_start_streaming(taxi_signal_device_message_api, mockserver):
    @mockserver.json_handler(
        '/iot-data-api-cloud/iot-devices/v1/registries/xxx/publish',
    )
    def _accept_message(request):
        decoded = _parse_jwt_validate_base(request)

        assert decoded == {
            'meta': {'seconds_to_expire': 69, 'serial_number': '123'},
            'payload': {
                'command_type': 'start_streaming',
                'command_id': 1,
                'command_version': 1,
                'streaming_details': {'xxx': 'blablabla'},
            },
            'iss': 'signal_device_message_api',
        }
        return {}

    json_request = {
        'meta': {'serial_number': '123', 'seconds_to_expire': 69},
        'payload': {
            'command_type': 'start_streaming',
            'command_version': 1,
            'streaming_details': {'xxx': 'blablabla'},
        },
    }

    response = await taxi_signal_device_message_api.post(
        ENDPOINT_EXTERNAL,
        json=json_request,
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Idempotency-Token': '123',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'command_id': 1}


@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
@pytest.mark.parametrize(
    'endpoint, event_type, expected_code',
    [
        (ENDPOINT_INTERNAL, 'alarm', 200),
        (ENDPOINT_EXTERNAL, 'alarm', 200),
        (ENDPOINT_INTERNAL, 'holy_shit', 400),
        (ENDPOINT_EXTERNAL, 'holy_shit', 400),
    ],
)
async def test_event_raise(
        taxi_signal_device_message_api,
        mockserver,
        endpoint,
        event_type,
        expected_code,
):
    @mockserver.json_handler(
        '/iot-data-api-cloud/iot-devices/v1/registries/xxx/publish',
    )
    def _accept_message(request):
        decoded = _parse_jwt_validate_base(request)

        assert decoded == {
            'meta': {'seconds_to_expire': 69, 'serial_number': '123'},
            'payload': {
                'command_type': 'event_raise',
                'command_id': 1,
                'command_version': 1,
                'command_payload': {'name': event_type},
            },
            'iss': 'signal_device_message_api',
        }
        return {}

    json_request = {
        'meta': {'serial_number': '123', 'seconds_to_expire': 69},
        'payload': {
            'command_type': 'event_raise',
            'command_version': 1,
            'command_payload': {'name': event_type},
        },
    }

    response = await taxi_signal_device_message_api.post(
        endpoint,
        json=json_request,
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Idempotency-Token': '123',
        },
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 200:
        assert response.json() == {'command_id': 1}
