import pytest

from tests_signal_device_api import common


ENDPOINT = 'signal-device/v1/signal-device-configs/v1/configs/updates'

CONFIGS_RESPONSE = {
    'config_updates': [
        {
            'name': 'my_top2_config.json',
            'update': {
                'my_field2': 1,
                'my_field5': {'my_field6': 21, 'my_field7': 'hello'},
            },
        },
    ],
}

AES_KEY1 = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
AES_KEY2 = 'TABE4XLXC30EE18148CE3ADA374669999D9DD7CC84B0731248B42700E521991E'
AES_KEY3 = 'F22L98LXC30EE18148CE3ADA374669999D9DD7CC84B0731248B42700E521991E'
AES_KEY4 = 'X42X99LXC30EL48148CE3ADA374669999D9DD7CC84B0731248B42700E521991E'

DEFAULT_IF_MODIFIED_SINCE = 'Wed, 21 Oct 2015 07:28:00 GMT'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'serial_number, aes_key, if_modified_since, code, expected',
    [
        (
            '1234567890ABC',
            AES_KEY1,
            DEFAULT_IF_MODIFIED_SINCE,
            200,
            CONFIGS_RESPONSE,
        ),
        (
            '9999567812CBC',
            AES_KEY2,
            DEFAULT_IF_MODIFIED_SINCE,
            200,
            CONFIGS_RESPONSE,
        ),
        (
            '9000567812CBC',
            AES_KEY3,
            DEFAULT_IF_MODIFIED_SINCE,
            200,
            CONFIGS_RESPONSE,
        ),
        (
            '1204467800CBC',
            AES_KEY4,
            DEFAULT_IF_MODIFIED_SINCE,
            200,
            CONFIGS_RESPONSE,
        ),
        ('xxx', AES_KEY1, DEFAULT_IF_MODIFIED_SINCE, 400, None),
        ('1234567890ABC', AES_KEY1, '2020-12-12T00:00:00+03:00', 400, None),
        ('2234567890ABC', AES_KEY1, DEFAULT_IF_MODIFIED_SINCE, 500, None),
    ],
)
async def test_configs_update(
        taxi_signal_device_api,
        serial_number,
        aes_key,
        if_modified_since,
        code,
        expected,
        mockserver,
):
    @mockserver.json_handler(f'/signal-device-configs/{ENDPOINT}')
    def _get_updates(request):
        return CONFIGS_RESPONSE

    request_json = {
        'software_version': '1.0-2',
        'serial_number': serial_number,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        json=request_json,
        headers={
            'X-JWT-Signature': common.generate_jwt_aes(
                ENDPOINT, aes_key, {}, request_json,
            ),
            'If-Modified-Since': if_modified_since,
        },
    )
    assert response.status_code == code, response.text
    if code == 200:
        assert response.json() == expected
