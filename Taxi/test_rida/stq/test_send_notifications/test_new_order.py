import datetime

import pytest

from rida.stq import send_notifications
from test_rida import experiments_utils


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.mongodb_collections('rida_drivers')
@pytest.mark.filldb()
@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer.title': {'en': 'New ride'},
        'notifications.driver.new_offer.body': {
            'en': (
                'New ride suggestion for {price}'
                ' {currency} {point_a} - {point_b}'
            ),
        },
    },
)
async def test_new_offer(
        stq3_context,
        get_stats_by_list_label_values,
        validate_stq3_sent_notifications,
):

    await send_notifications.task(
        stq3_context,
        intent='new_offer',
        offer_guid='some_offer_guid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        start_point=[23.45, 45.23],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
        currency='NGN',
    )
    validate_stq3_sent_notifications(
        expected_notifications=[
            {
                'id': '00000000000000000000000000000000',
                'firebase_token': 'firebase_token1',
                'title': 'New ride',
                'body': 'New ride suggestion for 500 NGN point_a - point_b',
                'data': {'offer_guid': 'some_offer_guid', 'push_type': 1},
                'sound': {'apns': 'new_order.caf'},
                'notification_channel': {'android': 'tada_new_order_chanel'},
            },
        ],
    )
    query = (
        'SELECT intent, push_id, user_guid, created_at, expired_at '
        'FROM push_notifications;'
    )
    async with stq3_context.pg.ro_pool.acquire() as conn:
        records = await conn.fetch(query)
        assert len(records) == 1
        record = records[0]
        assert record['intent'] == 'new_offer'
        assert record['push_id'] == '00000000000000000000000000000000'
        assert record['user_guid'] == '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G'
        assert record['expired_at'] - record[
            'created_at'
        ] == datetime.timedelta(minutes=10)

    stats = get_stats_by_list_label_values(
        stq3_context,
        [
            {'sensor': 'notifications.sent'},
            {'sensor': 'notifications.sent_amount'},
        ],
    )
    assert stats[0] == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'notifications.sent',
                'intent': 'new_offer',
                'is_success': 'true',
            },
            'value': 1,
            'timestamp': None,
        },
    ]
    assert stats[1] == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'amount': '1',
                'intent': 'new_offer',
                'sensor': 'notifications.sent_amount',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


_NOTIFICATIONS = [
    {
        'id': '00000000000000000000000000000000',
        'firebase_token': 'firebase_token0',
        'title': 'New ride',
        'body': 'New ride suggestion for 500 NGN point_a - point_b',
        'data': {'offer_guid': 'some_offer_guid', 'push_type': 1},
        'sound': {'apns': 'new_order.caf'},
        'notification_channel': {'android': 'tada_new_order_chanel'},
    },
    {
        'id': '00000000000000000000000000000001',
        'firebase_token': 'firebase_token1',
        'title': 'New ride',
        'body': 'New ride suggestion for 500 NGN point_a - point_b',
        'data': {'offer_guid': 'some_offer_guid', 'push_type': 1},
        'sound': {'apns': 'new_order.caf'},
        'notification_channel': {'android': 'tada_new_order_chanel'},
    },
]


_USER_GUIDS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J',
]


@pytest.mark.now('2020-02-26T13:50:00.000')
@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer.title': {'en': 'New ride'},
        'notifications.driver.new_offer.body': {
            'en': (
                'New ride suggestion for {price}'
                ' {currency} {point_a} - {point_b}'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'expected_notifications',
    [
        pytest.param(
            _NOTIFICATIONS[:1],
            marks=experiments_utils.get_dispatch_exp(
                user_guid=_USER_GUIDS[2], application='rida_ios',
            ),
            id='no experiment',
        ),
        pytest.param(
            _NOTIFICATIONS,
            marks=[
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[0],
                ),
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[1],
                ),
                experiments_utils.get_dispatch_exp(
                    user_guid=_USER_GUIDS[2], application='rida_ios',
                ),
            ],
            id='no limits',
        ),
        pytest.param(
            _NOTIFICATIONS,
            marks=[
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[0], max_search_distance_meters=1000,
                ),
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[1],
                ),
                experiments_utils.get_dispatch_exp(
                    user_guid=_USER_GUIDS[2], application='rida_ios',
                ),
            ],
            id='close driver has limit in 1km',
        ),
        pytest.param(
            _NOTIFICATIONS[:1],
            marks=[
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[0],
                ),
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[1], max_search_distance_meters=1000,
                ),
                experiments_utils.get_dispatch_exp(
                    user_guid=_USER_GUIDS[2], application='rida_ios',
                ),
            ],
            id='distant driver has limit in 1km',
        ),
        pytest.param(
            _NOTIFICATIONS[:1],
            marks=[
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[0],
                ),
                experiments_utils.get_driver_dispatch_exp(
                    user_guid=_USER_GUIDS[1],
                ),
                experiments_utils.get_dispatch_exp(
                    user_guid=_USER_GUIDS[2],
                    max_search_distance_meters=1000,
                    application='rida_ios',
                ),
            ],
            id='all drivers are being searched in 1km',
        ),
    ],
)
async def test_dispatch_experiment(
        stq3_context,
        mongodb,
        validate_stq3_sent_notifications,
        expected_notifications,
):
    mongodb.rida_drivers.update(
        {'user_guid': _USER_GUIDS[1]},
        {
            '$set': {
                'location': {'coordinates': [23.46, 45.24], 'type': 'Point'},
            },
        },
        multi=True,
    )
    await send_notifications.task(
        stq3_context,
        intent='new_offer',
        offer_guid='some_offer_guid',
        user_guid=_USER_GUIDS[2],
        start_point=[23.45, 45.23],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
        currency='NGN',
    )
    validate_stq3_sent_notifications(
        expected_notifications=expected_notifications,
    )


@pytest.mark.now('2020-02-26T13:50:00.000')
@experiments_utils.get_dispatch_exp(
    user_guid=_USER_GUIDS[2], nearest_drivers_limit=1, application='rida_ios',
)
@experiments_utils.get_driver_dispatch_exp(user_guid=_USER_GUIDS[0])
@pytest.mark.translations(
    rida={
        'notifications.driver.new_offer.title': {'en': 'New ride'},
        'notifications.driver.new_offer.body': {
            'en': (
                'New ride suggestion for {price}'
                ' {currency} {point_a} - {point_b}'
            ),
        },
    },
)
async def test_nearest_drivers_limit(
        stq3_context, mongodb, validate_stq3_sent_notifications,
):
    mongodb.rida_drivers.update(
        {'user_guid': _USER_GUIDS[0]},
        {
            '$set': {
                'location': {'coordinates': [23.45, 45.25], 'type': 'Point'},
            },
        },
        multi=True,
    )
    await send_notifications.task(
        stq3_context,
        intent='new_offer',
        offer_guid='some_offer_guid',
        user_guid=_USER_GUIDS[2],
        start_point=[23.44, 45.24],
        point_a='point_a',
        point_b='point_b',
        initial_price=500.4,
        currency='NGN',
    )
    validate_stq3_sent_notifications(expected_notifications=_NOTIFICATIONS[:1])
