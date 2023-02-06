import pytest

ENDPOINT_INTERNAL = '/internal/v1/signal-device-message-api/device/v1/message'

ENDPOINT_EXTERNAL = '/fleet/signal-device-message-api/v1/device/message'

USER_TICKET = (
    '3:user:CA4Q__________9_GhsKAggqECoaBH'
    'JlYWQaBXdyaXRlINKF2MwEKAM:FmLcx6glId9f'
    'VYjhFTD69vUVDyMcawZ0z7En9Q0g6fsioFNEq'
    'dMhvEyx4bl25SFWFjjVnGBs-pPOpPWsqC4JmHV'
    'STH8lFgoAqeOb5B3D5g1t20V0NwxuAU9EIzkQ'
    'eE8a6cMbi4r6-lvAkUZZmefXbMvQddk_r1pHBg'
    'S--V-qAU4'
)


@pytest.mark.parametrize('endpoint', [ENDPOINT_INTERNAL, ENDPOINT_EXTERNAL])
async def test_message(
        taxi_signal_device_message_api,
        testpoint,
        pgsql,
        redis_store,
        mockserver,
        endpoint,
):
    @testpoint('session_id')
    def set_session(session_id):
        return session_id

    # just to get session_id
    response = await taxi_signal_device_message_api.get(
        f'{endpoint}' '?serial_number=123&command_id=1',
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
    )
    session_id = (await set_session.wait_call())['session_id']

    redis_store.hmset(
        f'Mqtt:Device:Commands:{session_id}:123:1',
        {'waiting_for_response': 'True'},
    )
    redis_store.hmset(
        f'Mqtt:Device:Commands:{session_id}:123:2',
        {'waiting_for_response': 'True'},
    )

    put_response = await taxi_signal_device_message_api.put(
        '/signal-device/v1/signal-device-message-api/device/v1/message',
        json={
            'meta': {
                'serial_number': '123',
                'receiver_id': session_id,
                'timestamp': '2021-02-05T15:00:00+03:00',
            },
            'payload': {
                'command_id': 1,
                'command_type': 'config_get',
                'command_status': 'success',
                'command_version': 1,
                'device_config': {
                    'name': 'my_cfg_1.json',
                    'content': {
                        'some_val1': 1,
                        'some_val2': 'xxx',
                        'some_val3': {'some_val4': True},
                    },
                },
            },
        },
    )
    assert put_response.status_code == 200, put_response.text

    response = await taxi_signal_device_message_api.get(
        f'{endpoint}' '?serial_number=123&command_id=1',
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'response_status': 'received_response',
        'device_response': {
            'command_status': 'success',
            'timestamp': '2021-02-05T12:00:00+00:00',
            'command_version': 1,
            'device_config': {
                'name': 'my_cfg_1.json',
                'content': {
                    'some_val1': 1,
                    'some_val2': 'xxx',
                    'some_val3': {'some_val4': True},
                },
            },
        },
    }

    # no response from device
    response = await taxi_signal_device_message_api.get(
        f'{endpoint}' '?serial_number=123&command_id=2',
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'response_status': 'waiting_for_response'}

    # no command
    response = await taxi_signal_device_message_api.get(
        '/internal/v1/signal-device-message-api/device/v1/message'
        '?serial_number=123&command_id=289',
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'response_status': 'command_unknown_or_expired'}
