import pytest

ENDPOINT = '/signal-device/v1/signal-device-message-api/device/v1/message'


@pytest.mark.redis_store(
    ['hmset', 'Mqtt:Device:Commands:test_client:123:1', {'some_meta': 'True'}],
)
@pytest.mark.parametrize('command_id, expected_code', [(1, 200), (2, 408)])
async def test_message(
        taxi_signal_device_message_api,
        pgsql,
        redis_store,
        mockserver,
        command_id,
        expected_code,
):
    response = await taxi_signal_device_message_api.put(
        ENDPOINT,
        json={
            'meta': {
                'serial_number': '123',
                'receiver_id': 'test_client',
                'timestamp': '2021-02-05T15:00:00+03:00',
            },
            'payload': {
                'command_id': command_id,
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
    assert response.status_code == expected_code, response.text

    if expected_code == 200:
        assert (
            redis_store.hgetall('Mqtt:Device:Commands:test_client:123:1')
            == {
                b'response': (
                    b'{"command_status":"success","command_version":1,'
                    b'"device_config":{"na'
                    b'me":"my_cfg_1.json",'
                    b'"content":{"some_val1":1,"some_val2":"xx'
                    b'x","some_val3":{"some_val4":true}}},'
                    b'"timestamp":"2021-02-05T'
                    b'12:00:00+00:00"}'
                ),
                b'some_meta': b'True',
            }
        )


async def test_message_bad_format(
        taxi_signal_device_message_api, pgsql, redis_store, mockserver,
):
    response = await taxi_signal_device_message_api.put(
        ENDPOINT,
        json={
            'meta': {
                'serial_number': '123',
                'receiver_id': 'test_client',
                'timestamp': '2021-02-05T15:00:00+03:00',
            },
            'payload': {
                'command_id': 1,
                'command_type': 'config_get',
                'command_status': 'success',
                'command_version': 1,
            },
        },
    )
    assert response.status_code == 400, response.text
