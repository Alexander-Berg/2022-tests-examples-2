import pytest

from tests_signal_device_api import common


ENDPOINT = (
    'signal-device/v1/signal-device-message-api/device/v1/mqtt-registration'
)


AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '6359938a-7861-4266-9e02-6edd1c2138d9'
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmYB6e5eBFtRajXxCsIDm6AXoL/xN
zLsG2LMul+PWC+fPMA5QnUMpBdk/BsUdqabRzkKkbxO2aXxxwY3xGoC2iw==
-----END PUBLIC KEY-----"""


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'serial_number, code, expected, public_key',
    [
        ('1234567890ABC', 200, {'client_id': 'xxx'}, PUBLIC_KEY),
        ('xxx', 400, {}, PUBLIC_KEY),
    ],
)
async def test_200(
        taxi_signal_device_api,
        serial_number,
        code,
        expected,
        mockserver,
        public_key,
):
    @mockserver.json_handler(f'/signal-device-message-api/{ENDPOINT}')
    def _get_updates(request):
        return {'client_id': 'xxx'}

    request_json = {'serial_number': serial_number, 'public_key': public_key}
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, AES_KEY, {}, request_json,
            ),
        },
    )
    assert response.status_code == code, response.text
    if code == 200:
        assert response.json() == expected
