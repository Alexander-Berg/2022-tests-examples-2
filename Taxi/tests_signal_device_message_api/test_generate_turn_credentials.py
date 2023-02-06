import base64
from hashlib import sha1  # pylint: disable=C5521
import hmac

import pytest

TURN_SECRET = b'xxx'

USER_TICKET = (
    '3:user:CA4Q__________9_GhsKAggqECoaBH'
    'JlYWQaBXdyaXRlINKF2MwEKAM:FmLcx6glId9f'
    'VYjhFTD69vUVDyMcawZ0z7En9Q0g6fsioFNEq'
    'dMhvEyx4bl25SFWFjjVnGBs-pPOpPWsqC4JmHV'
    'STH8lFgoAqeOb5B3D5g1t20V0NwxuAU9EIzkQ'
    'eE8a6cMbi4r6-lvAkUZZmefXbMvQddk_r1pHBg'
    'S--V-qAU4'
)


@pytest.mark.pgsql('coturn', files=['coturn_db.sql'])
async def test_get_credentials(
        taxi_signal_device_message_api, pgsql, redis_store, mockserver,
):
    response = await taxi_signal_device_message_api.post(
        '/fleet/signal-device-message-api/v1/turn/generate-credentials',
        headers={
            'X-Ya-User-Ticket': USER_TICKET,
            'X-Yandex-UID': '4242',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
    )
    assert response.status_code == 200, response.text

    resp_json = response.json()
    user_name = resp_json['temporary_username']
    password = resp_json['temporary_password']

    name_splitted = user_name.split(':')
    assert len(name_splitted) == 2
    assert name_splitted[1] == '4242'

    name_hashed = hmac.new(TURN_SECRET, user_name.encode(), sha1).digest()
    assert password.encode() == base64.b64encode(name_hashed)

    assert set(resp_json['available_urls']) == {
        'turn:5.255.210.33:3478',
        'turn:[2a02:6b8:c10:2320:0:51d0:3949:0]:3478',
    }
