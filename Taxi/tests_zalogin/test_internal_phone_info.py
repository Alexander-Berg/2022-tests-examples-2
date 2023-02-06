import pytest


async def test_invalid_phone_id(taxi_zalogin):
    response = await taxi_zalogin.get(
        'v1/internal/phone-info', params={'phone_id': 'invalid'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_phone_id, response_items',
    [
        ('594baaba0000070000040100', []),
        (
            '594baaba0000070000040002',
            [
                {
                    'yandex_uid': '1112',
                    'type': 'phonish',
                    'bound_portal_uid': '1000',
                },
            ],
        ),
        (
            '594baaba0000070000040006',
            [
                {'yandex_uid': '1115', 'type': 'portal'},
                {'yandex_uid': '1120', 'type': 'portal'},
                {
                    'yandex_uid': '1121',
                    'type': 'phonish',
                    'bound_portal_uid': '1115',
                },
                {'yandex_uid': '1122', 'type': 'phonish'},
            ],
        ),
    ],
)
async def test_phone_info(taxi_zalogin, request_phone_id, response_items):
    response = await taxi_zalogin.get(
        'v1/internal/phone-info', params={'phone_id': request_phone_id},
    )
    assert response.status_code == 200
    assert _sorted_items(response.json()) == response_items


def _sorted_items(response_json):
    return sorted(response_json['items'], key=lambda item: item['yandex_uid'])
