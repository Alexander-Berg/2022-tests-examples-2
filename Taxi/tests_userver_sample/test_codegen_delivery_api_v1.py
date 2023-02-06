import copy
from typing import Optional

import pytest


DEFAULT_HEADERS = {
    'X-Yandex-UID': '12345',
    'X-Ya-User-Ticket': 'test-user-ticket',
    'X-YaDelivery-Pass-Flags': 'registered',
    'X-YaDelivery-User': 'personal_phone_id=+11111_id',
    'X-Remote-IP': '1.2.3.4',
}


async def test_auth_ok(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/delivery/v1/userver-sample/v1/test/delivery-v1',
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'is-authorized': True,
        'is-registered': True,
        'phone-id': '+11111_id',
        'user-ip': '1.2.3.4',
        'user-ticket': 'test-user-ticket',
        'yandex-uid': '12345',
    }


async def test_user_phones(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/delivery/v1/userver-sample/v1/test/delivery-v1/phones',
        headers={
            **DEFAULT_HEADERS,
            'X-Ya-User-Phones': (
                'personal_phone_id=+111111_id;'
                'personal_phone_id=+222222_id,'
                'confirmed_at=2020-01-01T20:45:00+00:00'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'user-phones': [
            {'phone-id': '+111111_id'},
            {
                'phone-id': '+222222_id',
                'confirmed-at': '2020-01-01T20:45:00+00:00',
            },
        ],
    }


@pytest.mark.parametrize(
    'header_key, new_value',
    [
        ('X-Yandex-UID', None),
        ('X-YaDelivery-Pass-Flags', None),
        ('X-YaDelivery-Pass-Flags', 'not-registered'),
    ],
)
async def test_proxy_401(
        taxi_userver_sample, header_key: str, new_value: Optional[str],
):
    headers = copy.deepcopy(DEFAULT_HEADERS)
    if new_value is None:
        del headers[header_key]
    else:
        headers[header_key] = new_value

    response = await taxi_userver_sample.post(
        '/delivery/v1/userver-sample/v1/test/delivery-v1', headers=headers,
    )
    assert response.status_code == 200
    assert not response.json()['is-authorized']
