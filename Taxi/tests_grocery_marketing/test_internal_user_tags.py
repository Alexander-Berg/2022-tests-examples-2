import copy

import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_marketing_user_tags': {
            'tag': 'total_orders_count',
            'payment_id_divisor': 3,
        },
    },
)
@pytest.mark.parametrize(
    'appmetrica_usage_count, payment_usage_count, phone_usage_count,'
    'yandex_uid_usage_count, is_new',
    (
        (0, 0, 0, 0, True),
        (0, 2, 0, 0, True),
        (0, 3, 0, 0, False),
        (1, 0, 0, 0, False),
    ),
)
async def test_basic(
        taxi_grocery_marketing,
        pgsql,
        appmetrica_usage_count,
        payment_usage_count,
        phone_usage_count,
        yandex_uid_usage_count,
        is_new,
):
    tag = 'total_orders_count'

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=tag,
        usage_count=yandex_uid_usage_count,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.APPMETRICA_DEVICE_ID,
        id_type='appmetrica_device_id',
        tag=tag,
        usage_count=appmetrica_usage_count,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.PAYMENT_ID,
        id_type='payment_id',
        tag=tag,
        usage_count=payment_usage_count,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.PERSONAL_PHONE_ID,
        id_type='personal_phone_id',
        tag=tag,
        usage_count=phone_usage_count,
    )

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/user-tags',
        json={
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'eats_user_id': common.EATS_USER_ID,
            'payment_id': common.PAYMENT_ID,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['is_new_user'] == is_new


@pytest.mark.parametrize('remove_yandex_uid', (True, False))
@pytest.mark.parametrize('remove_device_id', (True, False))
async def test_401(
        taxi_grocery_marketing, remove_yandex_uid, remove_device_id,
):
    headers = copy.deepcopy(common.DEFAULT_USER_HEADERS)
    if remove_yandex_uid:
        del headers['X-Yandex-UID']
    if remove_device_id:
        del headers['X-AppMetrica-DeviceId']

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/user-tags',
        json={
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'eats_user_id': common.EATS_USER_ID,
            'payment_id': common.PAYMENT_ID,
        },
        headers=headers,
    )

    if remove_yandex_uid or remove_device_id:
        assert response.status_code == 401
    else:
        assert response.status_code == 200
