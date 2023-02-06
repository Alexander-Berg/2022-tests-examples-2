import copy

import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models


LIMIT_LAST_ORDER_IDS = 3


async def upload_stats(taxi_grocery_marketing, body):
    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/upload-statistics',
        json=body,
        headers=common.DEFAULT_USER_HEADERS,
    )
    assert response.status_code == 200


def check_stats(pgsql, tag, stats, other_stats):
    for stat in stats:
        tag_stat = models.TagStatistic.fetch(
            pgsql=pgsql, yandex_uid=stat['yandex_uid'], tag=tag,
        )

        assert tag_stat.last_order_ids is None
        assert tag_stat.usage_count == stat['usage_count']

    for stat in other_stats:
        tag_other_stat = models.OtherTagStatistic.fetch(
            pgsql=pgsql,
            user_id=stat['device_id'],
            id_type='appmetrica_device_id',
            tag=tag,
        )

        assert tag_other_stat.last_order_ids is None
        assert tag_other_stat.usage_count == stat['usage_count']


@pytest.mark.config(
    GROCERY_MARKETING_LIMIT_LAST_ORDER_IDS=LIMIT_LAST_ORDER_IDS,
)
async def test_basic(taxi_grocery_marketing, pgsql):
    stats = [
        {'yandex_uid': 'yandex_uid_1', 'usage_count': 50},
        {'yandex_uid': 'yandex_uid_2', 'usage_count': 10},
    ]
    other_stats = [
        {'device_id': 'device_id_1', 'usage_count': 50},
        {'device_id': 'device_id_2', 'usage_count': 10},
    ]
    tag = 'tag_1'

    body = {'tag': tag, 'values': stats + other_stats, 'operation_id': '123'}

    await upload_stats(taxi_grocery_marketing, body)

    check_stats(pgsql, tag, stats, other_stats)


@pytest.mark.config(
    GROCERY_MARKETING_LIMIT_LAST_ORDER_IDS=LIMIT_LAST_ORDER_IDS,
)
async def test_existing_tag(taxi_grocery_marketing, pgsql):
    tag = 'tag_1'
    yandex_uid = 'yandex_uid_1'
    device_id = 'device_id_1'
    usage_count1 = 50

    body = {
        'operation_id': '123',
        'tag': tag,
        'values': [
            {
                'yandex_uid': yandex_uid,
                'device_id': device_id,
                'usage_count': usage_count1,
            },
        ],
    }

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/upload-statistics',
        json=body,
        headers=common.DEFAULT_USER_HEADERS,
    )
    assert response.status_code == 200

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
    )
    other_tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
    )

    assert tag_stat.usage_count == usage_count1
    assert other_tag_stat.usage_count == usage_count1

    usage_count2 = 33

    body = {
        'operation_id': '456',
        'tag': tag,
        'values': [
            {
                'yandex_uid': yandex_uid,
                'device_id': device_id,
                'usage_count': usage_count2,
            },
        ],
    }

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/upload-statistics',
        json=body,
        headers=common.DEFAULT_USER_HEADERS,
    )
    assert response.status_code == 200

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
    )
    other_tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
    )

    assert tag_stat.usage_count == usage_count1 + usage_count2
    assert other_tag_stat.usage_count == usage_count1 + usage_count2


@pytest.mark.config(
    GROCERY_MARKETING_LIMIT_LAST_ORDER_IDS=LIMIT_LAST_ORDER_IDS,
)
async def test_duplicate_request_data(taxi_grocery_marketing, pgsql):
    stats = [
        {'yandex_uid': 'yandex_uid_1', 'usage_count': 50},
        {'yandex_uid': 'yandex_uid_1', 'usage_count': 10},
    ]
    tag = 'tag_1'
    headers = copy.deepcopy(common.DEFAULT_USER_HEADERS)

    body = {'tag': tag, 'values': stats, 'operation_id': '123'}

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/upload-statistics', json=body, headers=headers,
    )
    assert response.status_code == 400

    other_stats = [
        {'device_id': 'device_id_1', 'usage_count': 50},
        {'device_id': 'device_id_1', 'usage_count': 10},
    ]
    tag = 'tag_2'
    headers = copy.deepcopy(common.DEFAULT_USER_HEADERS)

    body = {'tag': tag, 'values': other_stats}

    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/upload-statistics', json=body, headers=headers,
    )
    assert response.status_code == 400


async def test_idempotency(taxi_grocery_marketing, pgsql):
    stats = [
        {'yandex_uid': 'yandex_uid_1', 'usage_count': 50},
        {'yandex_uid': 'yandex_uid_2', 'usage_count': 10},
    ]
    other_stats = [
        {'device_id': 'device_id_1', 'usage_count': 50},
        {'device_id': 'device_id_2', 'usage_count': 10},
    ]

    stats_operation_2 = [
        {'yandex_uid': 'yandex_uid_1', 'usage_count': 100},
        {'yandex_uid': 'yandex_uid_2', 'usage_count': 20},
    ]
    other_stats_operation_2 = [
        {'device_id': 'device_id_1', 'usage_count': 100},
        {'device_id': 'device_id_2', 'usage_count': 20},
    ]

    tag = 'tag_1'

    operation_1 = {
        'tag': tag,
        'values': stats + other_stats,
        'operation_id': 'operation_1',
    }
    operation_2 = {
        'tag': tag,
        'values': stats + other_stats,
        'operation_id': 'operation_2',
    }

    await upload_stats(taxi_grocery_marketing, operation_1)
    check_stats(pgsql, tag, stats, other_stats)

    await upload_stats(taxi_grocery_marketing, operation_1)
    check_stats(pgsql, tag, stats, other_stats)

    await upload_stats(taxi_grocery_marketing, operation_2)
    check_stats(pgsql, tag, stats_operation_2, other_stats_operation_2)

    await upload_stats(taxi_grocery_marketing, operation_1)
    check_stats(pgsql, tag, stats_operation_2, other_stats_operation_2)
