import json

import pytest

from tests_signal_device_api import common


ENDPOINT = 'signal-device/v1/signal-device-message-api/device/v1/message'


AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '6359938a-7861-4266-9e02-6edd1c2138d9'
CONFIG_REQUEST = {
    'meta': {
        'serial_number': '1234567890ABC',
        'receiver_id': 'test_client',
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
}


CONFIG_REQUEST_PARSED = {
    'meta': {
        **CONFIG_REQUEST['meta'],  # type: ignore
        'timestamp': '2021-02-05T12:00:00+00:00',  # type: ignore
    },  # таймстамп превращается в utc при перекладывании
    'payload': CONFIG_REQUEST['payload'],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize('expected_code', [200, 400, 408, 501])
async def test_200(taxi_signal_device_api, expected_code, mockserver):
    @mockserver.json_handler(f'/signal-device-message-api/{ENDPOINT}')
    def _put_message(request):
        if expected_code != 200:
            return mockserver.make_response(
                json={
                    'code': 'command_expired',
                },  # для тестов подойдет один код везде
                status=expected_code,
            )
        request_json = json.loads(request.get_data())
        assert request_json == CONFIG_REQUEST_PARSED
        return mockserver.make_response(json={}, status=200)

    response = await taxi_signal_device_api.put(
        ENDPOINT,
        json=CONFIG_REQUEST,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, CONFIG_REQUEST,
            ),
        },
    )
    assert response.status_code == expected_code, response.text
