import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models


@pytest.mark.config(GROCERY_MARKETING_RETRIEVE_EATS_STATS=True)
@pytest.mark.parametrize(
    'headers, usage_count',
    (
        pytest.param(common.DEFAULT_USER_HEADERS, 3),
        pytest.param(common.DEFAULT_USER_HEADERS_WITHOUT_UID, 0),
    ),
)
@pytest.mark.parametrize('handler_version', ['v2'])
async def test_basic(
        taxi_grocery_marketing,
        eats_order_stats,
        pgsql,
        handler_version,
        headers,
        usage_count,
):
    tag = 'total_orders_count'
    appmetrica_usage_count = 4
    payment_usage_count = 3
    phone_usage_count = 2

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=tag,
        usage_count=usage_count,
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

    eats_id_tag_count = 3

    eats_order_stats.set_orders_data(
        common.EATS_USER_ID,
        eats_id_tag_count,
        [
            {
                'first_order_at': '2021-08-26T02:41:15+0000',
                'last_order_at': '2021-08-26T02:41:15+0000',
                'properties': [],
                'value': eats_id_tag_count,
            },
        ],
    )

    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/{handler_version}/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['usage_count'] == usage_count
    if handler_version == 'v1':
        assert eats_order_stats.times_orders_called == 1
        assert response.json()['eats_id_usage_count'] == eats_id_tag_count

    assert (
        response.json()['appmetrica_device_id_usage_count']
        == appmetrica_usage_count
    )
    assert response.json()['payment_id_usage_count'] == payment_usage_count
    assert (
        response.json()['personal_phone_id_usage_count'] == phone_usage_count
    )


@pytest.mark.config(GROCERY_MARKETING_RETRIEVE_EATS_STATS=True)
@pytest.mark.parametrize('handler_version', ['v2'])
@pytest.mark.parametrize(
    'total_orders_count, without_payment_count, expected_paid_count',
    [(10, 4, 6), (10, None, 10)],
)
async def test_paid_orders_tag(
        taxi_grocery_marketing,
        eats_order_stats,
        pgsql,
        handler_version,
        total_orders_count,
        without_payment_count,
        expected_paid_count,
):
    total_orders_tag = 'total_orders_count'
    without_payment_orders_tag = 'total_order_count_without_payments'

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=total_orders_tag,
        usage_count=total_orders_count,
    )

    id_types = [
        {'id': common.APPMETRICA_DEVICE_ID, 'id_type': 'appmetrica_device_id'},
        {'id': common.PERSONAL_PHONE_ID, 'id_type': 'personal_phone_id'},
        {'id': common.PAYMENT_ID, 'id_type': 'payment_id'},
    ]

    for id_type in id_types:
        models.OtherTagStatistic(
            pgsql=pgsql,
            user_id=id_type['id'],
            id_type=id_type['id_type'],
            tag=total_orders_tag,
            usage_count=total_orders_count,
        )

    if without_payment_count is not None:
        models.TagStatistic(
            pgsql=pgsql,
            yandex_uid=common.YANDEX_UID,
            tag=without_payment_orders_tag,
            usage_count=without_payment_count,
        )
        for id_type in id_types:
            models.OtherTagStatistic(
                pgsql=pgsql,
                user_id=id_type['id'],
                id_type=id_type['id_type'],
                tag=without_payment_orders_tag,
                usage_count=without_payment_count,
            )

    eats_id_tag_count = 3

    eats_order_stats.set_orders_data(
        common.EATS_USER_ID,
        eats_id_tag_count,
        [
            {
                'first_order_at': '2021-08-26T02:41:15+0000',
                'last_order_at': '2021-08-26T02:41:15+0000',
                'properties': [],
                'value': eats_id_tag_count,
            },
        ],
    )

    paid_orders_tag = 'total_paid_orders_count'
    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/{handler_version}/tag/retrieve',
        json={
            'tag': paid_orders_tag,
            'yandex_uid': common.YANDEX_UID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'payment_id': common.PAYMENT_ID,
            'eats_id': common.EATS_USER_ID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['usage_count'] == expected_paid_count

    assert (
        response.json()['appmetrica_device_id_usage_count']
        == expected_paid_count
    )
    assert eats_order_stats.times_orders_called == 1
    assert response.json()['eats_id_usage_count'] == eats_id_tag_count
    assert (
        response.json()['personal_phone_id_usage_count'] == expected_paid_count
    )
    assert response.json()['payment_id_usage_count'] == expected_paid_count


@pytest.mark.parametrize('handler_version', ['v2'])
@pytest.mark.config(GROCERY_MARKETING_RETRIEVE_EATS_STATS=False)
async def test_eats_id_retrieve_disabled(
        taxi_grocery_marketing, eats_order_stats, handler_version,
):
    eats_order_stats.set_orders_data(common.EATS_USER_ID, 'test')

    total_orders_tag = 'total_orders_count'
    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/{handler_version}/tag/retrieve',
        json={'tag': total_orders_tag, 'eats_id': common.EATS_USER_ID},
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert eats_order_stats.times_orders_called == 0
    assert response.json()['eats_id_usage_count'] == 0


@pytest.mark.parametrize('handler_version', ['v2'])
@pytest.mark.config(GROCERY_MARKETING_RETRIEVE_EATS_STATS=True)
async def test_eats_id_no_counter(
        taxi_grocery_marketing, eats_order_stats, handler_version,
):
    eats_order_stats.set_orders_data(common.EATS_USER_ID, '111')

    total_orders_tag = 'total_orders_count'
    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/{handler_version}/tag/retrieve',
        json={'tag': total_orders_tag, 'eats_id': common.EATS_USER_ID},
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert eats_order_stats.times_orders_called == 1
    assert response.json()['eats_id_usage_count'] == 0


async def test_missing_uid_tag(taxi_grocery_marketing, pgsql):
    tag = 'total_orders_count'
    appmetrica_usage_count = 4
    payment_usage_count = 3
    phone_usage_count = 2

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
        '/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
        },
    )

    assert response.status_code == 200


async def test_missing_uid_several_tags(taxi_grocery_marketing, pgsql):
    total_orders_tag = 'total_orders_count'
    without_payment_orders_tag = 'total_order_count_without_payments'

    id_types = [
        {'id': common.APPMETRICA_DEVICE_ID, 'id_type': 'appmetrica_device_id'},
        {'id': common.PERSONAL_PHONE_ID, 'id_type': 'personal_phone_id'},
        {'id': common.PAYMENT_ID, 'id_type': 'payment_id'},
    ]

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=total_orders_tag,
        usage_count=1,
    )

    for id_type in id_types:
        models.OtherTagStatistic(
            pgsql=pgsql,
            user_id=id_type['id'],
            id_type=id_type['id_type'],
            tag=total_orders_tag,
            usage_count=1,
        )

        models.OtherTagStatistic(
            pgsql=pgsql,
            user_id=id_type['id'],
            id_type=id_type['id_type'],
            tag=without_payment_orders_tag,
            usage_count=1,
        )

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': 'total_paid_orders_count',
            'yandex_uid': common.YANDEX_UID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
        },
    )

    assert response.status_code == 200


async def test_antifraud_check(taxi_grocery_marketing, pgsql, mockserver):
    tag = 'total_orders_count'
    uid_orders_count = 1
    uid_1_orders_count = 2
    uid_2_orders_count = 3

    uid_1 = 'uid-1'
    uid_2 = 'uid-2'

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=tag,
        usage_count=uid_orders_count,
    )

    models.TagStatistic(
        pgsql=pgsql, yandex_uid=uid_1, tag=tag, usage_count=uid_1_orders_count,
    )

    models.TagStatistic(
        pgsql=pgsql, yandex_uid=uid_2, tag=tag, usage_count=uid_2_orders_count,
    )

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_antifrod(request):
        return {'sources': {'grocery': {'passport_uids': [uid_1, uid_2]}}}

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'enable_antifraud': True,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()['usage_count']
        == uid_orders_count + uid_1_orders_count + uid_2_orders_count
    )
    assert (
        response.json()['usage_count_according_to_yandex_uid']
        == uid_orders_count
    )
    assert (
        response.json()['usage_count_according_to_glue']
        == uid_1_orders_count + uid_2_orders_count
    )


async def test_antifraud_unique_uids(
        taxi_grocery_marketing, pgsql, mockserver,
):
    tag = 'total_orders_count'
    uid_orders_count = 1
    uid_1_orders_count = 2
    uid_2_orders_count = 3

    uid_1 = 'uid-1'
    uid_2 = 'uid-2'

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=tag,
        usage_count=uid_orders_count,
    )

    models.TagStatistic(
        pgsql=pgsql, yandex_uid=uid_1, tag=tag, usage_count=uid_1_orders_count,
    )

    models.TagStatistic(
        pgsql=pgsql, yandex_uid=uid_2, tag=tag, usage_count=uid_2_orders_count,
    )

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_antifrod(request):
        return {
            'sources': {
                'grocery': {
                    'passport_uids': [common.YANDEX_UID, uid_1, uid_1, uid_2],
                },
            },
        }

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'enable_antifraud': True,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()['usage_count']
        == uid_orders_count + uid_1_orders_count + uid_2_orders_count
    )
    assert (
        response.json()['usage_count_according_to_yandex_uid']
        == uid_orders_count
    )
    assert (
        response.json()['usage_count_according_to_glue']
        == uid_1_orders_count + uid_2_orders_count
    )


async def test_antifraud_check_paid_orders(
        taxi_grocery_marketing, pgsql, mockserver,
):
    total_orders_tag = 'total_orders_count'
    total_orders_count = 5
    without_payment_orders_tag = 'total_order_count_without_payments'
    without_payment_orders_count = 3
    extra_uid = 'uid-1'

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=extra_uid,
        tag=total_orders_tag,
        usage_count=total_orders_count,
    )

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=extra_uid,
        tag=without_payment_orders_tag,
        usage_count=without_payment_orders_count,
    )

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_antifrod(request):
        return {'sources': {'grocery': {'passport_uids': [extra_uid]}}}

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': 'total_paid_orders_count',
            'yandex_uid': common.YANDEX_UID,
            'enable_antifraud': True,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()['usage_count']
        == total_orders_count - without_payment_orders_count
    )
    assert response.json()['usage_count_according_to_yandex_uid'] == 0
    assert (
        response.json()['usage_count_according_to_glue']
        == total_orders_count - without_payment_orders_count
    )


@pytest.mark.config(
    GROCERY_MARKETING_RETRIEVE_EATS_STATS=True,
    GROCERY_MARKETING_COUNTER_WITHOUT_PAYMENT='2019-09-08T00:00:00+00:00',
)
async def test_current_orders(
        mockserver, taxi_grocery_marketing, pgsql, headers,
):
    tags = ['total_orders_count', 'total_current_orders_count']
    usage_count = 5
    appmetrica_usage_count = 4
    payment_usage_count = 3
    phone_usage_count = 2

    usage_count_free = 3
    appmetrica_usage_count_free = 2
    payment_usage_count_free = 1
    phone_usage_count_free = 1

    for tag in tags:
        models.TagStatistic(
            pgsql=pgsql,
            yandex_uid=common.YANDEX_UID,
            tag=tag,
            usage_count=usage_count,
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

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag='total_current_orders_count_without_payments',
        usage_count=usage_count_free,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.APPMETRICA_DEVICE_ID,
        id_type='appmetrica_device_id',
        tag='total_current_orders_count_without_payments',
        usage_count=appmetrica_usage_count_free,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.PAYMENT_ID,
        id_type='payment_id',
        tag='total_current_orders_count_without_payments',
        usage_count=payment_usage_count_free,
    )

    models.OtherTagStatistic(
        pgsql=pgsql,
        user_id=common.PERSONAL_PHONE_ID,
        id_type='personal_phone_id',
        tag='total_current_orders_count_without_payments',
        usage_count=phone_usage_count_free,
    )

    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': 'total_paid_orders_count_with_current',
            'yandex_uid': common.YANDEX_UID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['usage_count'] == 2 * usage_count - usage_count_free

    assert (
        response.json()['appmetrica_device_id_usage_count']
        == 2 * appmetrica_usage_count - appmetrica_usage_count_free
    )
    assert (
        response.json()['payment_id_usage_count']
        == 2 * payment_usage_count - payment_usage_count_free
    )
    assert (
        response.json()['personal_phone_id_usage_count']
        == 2 * phone_usage_count - phone_usage_count_free
    )


@pytest.mark.now('2020-11-12T13:00:50.283761+00:00')
@pytest.mark.config(
    GROCERY_MARKETING_CACHED_TAG_STATS=True,
    GROCERY_MARKETING_RETRIEVE_EATS_STATS=True,
)
async def test_tags_cache(
        taxi_grocery_marketing, eats_order_stats, mockserver, pgsql, testpoint,
):
    order_id = 'other_order_id'
    antifraud_uid_1 = 'antifraud_uid_1'
    antifraud_uid_2 = 'antifraud_uid_2'
    tag = 'total_orders_count'
    usage_count = 1
    appmetrica_usage_count = 4
    payment_usage_count = 3
    phone_usage_count = 2

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=common.YANDEX_UID,
        tag=tag,
        usage_count=usage_count,
    )

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=antifraud_uid_1,
        tag=tag,
        usage_count=usage_count,
    )

    models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=antifraud_uid_2,
        tag=tag,
        usage_count=usage_count,
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

    eats_id_tag_count = 3

    eats_order_stats.set_orders_data(
        common.EATS_USER_ID,
        eats_id_tag_count,
        [
            {
                'first_order_at': '2021-08-26T02:41:15+0000',
                'last_order_at': '2021-08-26T02:41:15+0000',
                'properties': [],
                'value': eats_id_tag_count,
            },
        ],
    )

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_antifrod(request):
        return {
            'sources': {
                'grocery': {
                    'passport_uids': [antifraud_uid_1, antifraud_uid_2],
                },
            },
        }

    @testpoint('GOT_FROM_CACHE')
    def got_tags_from_cache(data):
        pass

    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'eats_id': common.EATS_USER_ID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'enable_antifraud': True,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['usage_count'] == usage_count * 3  # antifraud
    assert (
        response.json()['usage_count_according_to_yandex_uid'] == usage_count
    )
    assert response.json()['usage_count_according_to_glue'] == usage_count * 2

    assert eats_order_stats.times_orders_called == 1
    assert response.json()['eats_id_usage_count'] == eats_id_tag_count

    assert (
        response.json()['appmetrica_device_id_usage_count']
        == appmetrica_usage_count
    )
    assert response.json()['payment_id_usage_count'] == payment_usage_count
    assert (
        response.json()['personal_phone_id_usage_count'] == phone_usage_count
    )

    assert got_tags_from_cache.times_called == 0

    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'eats_id': common.EATS_USER_ID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'enable_antifraud': True,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert got_tags_from_cache.times_called == 1

    assert response.status_code == 200
    assert response.json()['usage_count'] == usage_count * 3
    assert (
        response.json()['appmetrica_device_id_usage_count']
        == appmetrica_usage_count
    )
    assert response.json()['payment_id_usage_count'] == payment_usage_count
    assert (
        response.json()['personal_phone_id_usage_count'] == phone_usage_count
    )

    await common.inc_stat_value(
        taxi_grocery_marketing,
        common.DEFAULT_USER_HEADERS,
        common.YANDEX_UID,
        tag,
        order_id,
        payment_id=common.PAYMENT_ID,
    )

    response = await taxi_grocery_marketing.post(
        f'/internal/v1/marketing/v2/tag/retrieve',
        json={
            'tag': tag,
            'yandex_uid': common.YANDEX_UID,
            'eats_id': common.EATS_USER_ID,
            'appmetrica_device_id': common.APPMETRICA_DEVICE_ID,
            'payment_id': common.PAYMENT_ID,
            'personal_phone_id': common.PERSONAL_PHONE_ID,
            'enable_antifraud': True,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert got_tags_from_cache.times_called == 2

    assert response.json()['usage_count'] == usage_count * 3 + 1
    assert (
        response.json()['appmetrica_device_id_usage_count']
        == appmetrica_usage_count + 1
    )
    assert response.json()['payment_id_usage_count'] == payment_usage_count + 1
    assert (
        response.json()['personal_phone_id_usage_count']
        == phone_usage_count + 1
    )
