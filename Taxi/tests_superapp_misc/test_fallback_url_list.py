import datetime
import json
import os
import struct

from Crypto.Cipher import AES
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util import Padding
import pytest


AES_KEY = b'test-app-proxy-urls-aes-key'


def get_aes_key():
    return SHA.new(AES_KEY).digest()[: AES.block_size]


def decrypt(message):
    (signature_length,) = struct.unpack('<I', message[:4])
    assert signature_length == 256
    signature = message[4 : 4 + signature_length]
    encrypted = message[4 + signature_length :]

    path_to_key = os.path.join(
        os.path.dirname(__file__),
        'static',
        'test_fallback_url_list',
        'private_key.pem',
    )
    with open(path_to_key) as file:
        private_key = RSA.importKey(file.read())

    hash_data = SHA.new(encrypted)
    verifier = PKCS1_v1_5.new(private_key)

    # signer.verify is not callable
    # pylint: disable=not-callable
    if not verifier.verify(hash_data, signature):
        raise ValueError('Signature check failed')

    assert AES.block_size == 16
    i_vect, encrypted = (
        encrypted[: AES.block_size],
        encrypted[AES.block_size :],
    )
    chiper = AES.new(get_aes_key(), AES.MODE_CBC, i_vect)
    return json.loads(Padding.unpad(chiper.decrypt(encrypted), AES.block_size))


@pytest.mark.experiments3(filename='exp3_proxy_url_groups.json')
@pytest.mark.parametrize(
    'user_agent, expected_config, ttl',
    [
        pytest.param(
            'yandex-taxi/3.96.0.61338 Android/8.1.0 (Xiaomi; MI 8 Lite)',
            'taxi_decoded_config.json',
            3600,
            id='yataxi',
        ),
        pytest.param(
            'yango/3.93.0.54106 Android/6.0.1 (Xiaomi; Redmi Note 3)',
            'yango_decoded_config.json',
            7200,
            id='yango',
        ),
        pytest.param(
            'yandex-uber/3.84.0.67190 Android/8.0.0 (samsung; SM-A730F)',
            'uber_decoded_config.json',
            1800,
            id='yauber',
        ),
        pytest.param(
            'unknown app', 'taxi_decoded_config.json', 3600, id='unknown',
        ),
    ],
)
async def test_fallback_url_list(
        taxi_superapp_misc, user_agent, expected_config, ttl, load_json,
):
    headers = {'User-Agent': user_agent, 'X-Real-IP': '188.243.183.152'}
    response = await taxi_superapp_misc.get(
        '/superapp-misc/v1/fallback-url-list', headers=headers,
    )

    assert response.status_code == 200

    encoded_response = response.content
    decoded_response = decrypt(encoded_response)
    expired = decoded_response.pop('expired')

    expected_decoded_config = load_json(expected_config)
    assert expected_decoded_config == decoded_response
    assert datetime.datetime.strptime(
        expired, '%Y-%m-%dT%H:%M:%SZ',
    ) - datetime.datetime.utcnow() <= datetime.timedelta(seconds=ttl)


@pytest.mark.experiments3(filename='exp3_query_params.json')
async def test_query_params(taxi_superapp_misc):
    response = await taxi_superapp_misc.get(
        '/superapp-misc/v1/fallback-url-list?'
        'id=some_user_id&device_id=some_device_id&uuid=some_uuid',
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_bad.json')
async def test_bad_config_no_brand(taxi_superapp_misc):
    headers = {
        'User-Agent': (
            'yandex-taxi/3.96.0.61338 Android/8.1.0 (Xiaomi; MI 8 Lite)'
        ),
    }
    response = await taxi_superapp_misc.get(
        '/superapp-misc/v1/fallback-url-list', headers=headers,
    )

    assert response.status_code == 404
