from typing import Optional

import pytest


@pytest.mark.parametrize(
    ('maas_sub_id', 'expected_status'),
    (
        ('not_found_id', None),
        ('reserved_id', 'RESERVED'),
        ('active_id', 'ACTIVATED'),
        ('expired_id', 'EXPIRED'),
        ('active_expired_id', 'EXPIRED'),
        ('canceled_id', 'CANCELED'),
    ),
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_simple(
        taxi_maas, maas_sub_id: str, expected_status: Optional[str],
):
    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post(
        '/vtb/v1/sub/status',
        headers=headers,
        json={'maas_sub_id': maas_sub_id},
    )

    body = response.json()

    if expected_status is None:
        assert response.status == 422
        assert body['errorCode'] == '40'
        assert body['errorCause'] == 'subscription_not_found'
        return

    assert response.status == 200
    assert body['maas_user_id'] == 'maas_user_id'
    assert body['status'] == expected_status
