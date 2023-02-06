import datetime

import pytest


FINISHED_SENSOR_NAME = 'order_finished'
CANCELLED_SENSOR_NAME = 'order_cancelled'

TASK_NAME = 'eats-order-stats-reset-metrics-periodic'

PLACE_ID = [1, 2, 3]
BRAND_ID = [101, 102, 103]
BRAND_NAME = ['BRAND_NAME1', 'BRAND_NAME2', 'BRAND_NAME3']
OTHER_BRAND_NAME = 'other'
OTHER_BRAND_COUNTER_VALUE = 7.0
ORDER_TYPE = 'native'
PICKUP_SHIPPING_TYPE = 'pickup'
DELIVERY_SHIPPING_TYPE = 'delivery'
CANCELLATION_REASON = 'some_reason'
NO_CANCELLATION_REASON = None
EATS_CATALOG_STORAGE_CACHE_SETTINGS = [
    {
        'id': PLACE_ID[0],
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': BRAND_ID[0],
            'slug': 'slug1',
            'name': BRAND_NAME[0],
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
    {
        'id': PLACE_ID[1],
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': BRAND_ID[1],
            'slug': 'slug2',
            'name': BRAND_NAME[1],
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
    {
        'id': PLACE_ID[2],
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': BRAND_ID[2],
            'slug': 'slug3',
            'name': BRAND_NAME[2],
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
]


@pytest.fixture(name='prepare_order')
def _prepare_order():
    def prepare(order_nr, place_id, shipping_type, order_type):
        return {
            'order_nr': order_nr,
            'place_id': place_id,
            'order_type': order_type,
            'shipping_type': shipping_type,
            'finished_at': '2021-08-27T18:01:00+00:00',
            'cancelled_at': '2021-08-27T18:01:00+00:00',
            'cancellation_reason': CANCELLATION_REASON,
            'cancelled_by': 'restaurant',
        }

    return prepare


@pytest.fixture(name='compare_metrics')
def _compare_metrics():
    def _compare(
            result,
            shipping_type,
            order_type,
            brand_name,
            cancellation_reason,
            value,
            called=True,
    ):
        brand_name_subdict = {
            cancellation_reason: value,
            '$meta': {'solomon_children_labels': 'cancellation_reason'},
        }
        expected = {
            shipping_type: {
                order_type: {
                    brand_name: (
                        value
                        if cancellation_reason is None
                        else brand_name_subdict
                    ),
                    '$meta': {'solomon_children_labels': 'brand_name'},
                },
                '$meta': {'solomon_children_labels': 'order_type'},
            },
            '$meta': {'solomon_children_labels': 'shipping_type'},
        }
        expected_empty = {
            '$meta': {'solomon_children_labels': 'shipping_type'},
        }
        assert result == (expected if called else expected_empty)

    return _compare


@pytest.mark.pgsql('eats_order_stats', files=['orders_metrics.sql'])
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
@pytest.mark.parametrize(
    'shipping_type', [PICKUP_SHIPPING_TYPE, DELIVERY_SHIPPING_TYPE],
)
@pytest.mark.parametrize(
    'order_type,allowed_order_type',
    [(ORDER_TYPE, True), ('fast_food', False)],
)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('brand_save', [True, False])
@pytest.mark.parametrize('place_brand_index,value', [(0, 3), (1, 5), (2, 1)])
async def test_finished_metrics(
        prepare_order,
        compare_metrics,
        mocked_time,
        stq_runner,
        taxi_config,
        taxi_eats_order_stats,
        taxi_eats_order_stats_monitor,
        pgsql,
        shipping_type,
        order_type,
        allowed_order_type,
        enabled,
        brand_save,
        place_brand_index,
        value,
):

    brand_id = str(BRAND_ID[place_brand_index])
    place_id = str(PLACE_ID[place_brand_index])
    brand_name = BRAND_NAME[place_brand_index]
    taxi_config.set(
        EATS_ORDER_STATS_METRICS_SENDER_SETTINGS={
            'cancelled_metrics_enabled': True,
            'finished_metrics_enabled': enabled,
            'brand_ids_to_save': [],
            'brands_to_save': ([{'brand_id': brand_id}] if brand_save else []),
            'allowed_order_types': [ORDER_TYPE],
        },
    )
    await taxi_eats_order_stats.tests_control(reset_metrics=True)

    await stq_runner.eats_order_stats_finish_order.call(
        task_id='finish_order',
        kwargs=prepare_order('200-300', place_id, shipping_type, order_type),
    )

    result = await taxi_eats_order_stats_monitor.get_metric(
        FINISHED_SENSOR_NAME,
    )
    compare_metrics(
        result,
        shipping_type,
        order_type,
        (brand_name if brand_save else OTHER_BRAND_NAME),
        NO_CANCELLATION_REASON,
        (value if brand_save else OTHER_BRAND_COUNTER_VALUE),
        allowed_order_type and enabled,
    )

    mocked_time.sleep(1)

    await stq_runner.eats_order_stats_finish_order.call(
        task_id='finish_order',
        kwargs=prepare_order('300-400', place_id, shipping_type, order_type),
    )

    result = await taxi_eats_order_stats_monitor.get_metric(
        FINISHED_SENSOR_NAME,
    )
    compare_metrics(
        result,
        shipping_type,
        order_type,
        (brand_name if brand_save else OTHER_BRAND_NAME),
        NO_CANCELLATION_REASON,
        (value + 1 if brand_save else OTHER_BRAND_COUNTER_VALUE + 1),
        allowed_order_type and enabled,
    )


@pytest.mark.pgsql('eats_order_stats', files=['orders_metrics.sql'])
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
@pytest.mark.parametrize(
    'shipping_type', [PICKUP_SHIPPING_TYPE, DELIVERY_SHIPPING_TYPE],
)
@pytest.mark.parametrize(
    'order_type,allowed_order_type',
    [(ORDER_TYPE, True), ('fast_food', False)],
)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('brand_save', [True, False])
@pytest.mark.parametrize(
    'place_brand_index,value', [(0, 3.0), (1, 5.0), (2, 1.0)],
)
async def test_cancelled_metrics(
        prepare_order,
        compare_metrics,
        mocked_time,
        stq_runner,
        taxi_config,
        taxi_eats_order_stats,
        taxi_eats_order_stats_monitor,
        pgsql,
        shipping_type,
        order_type,
        allowed_order_type,
        enabled,
        brand_save,
        place_brand_index,
        value,
):
    brand_id = str(BRAND_ID[place_brand_index])
    place_id = str(PLACE_ID[place_brand_index])
    brand_name = BRAND_NAME[place_brand_index]
    taxi_config.set(
        EATS_ORDER_STATS_METRICS_SENDER_SETTINGS={
            'cancelled_metrics_enabled': enabled,
            'finished_metrics_enabled': True,
            'brand_ids_to_save': [],
            'brands_to_save': ([{'brand_id': brand_id}] if brand_save else []),
            'allowed_order_types': [ORDER_TYPE],
        },
    )
    await taxi_eats_order_stats.tests_control(reset_metrics=True)

    await stq_runner.eats_order_stats_cancel_order.call(
        task_id='cancel_order',
        kwargs=prepare_order('200-300', place_id, shipping_type, order_type),
    )
    result = await taxi_eats_order_stats_monitor.get_metric(
        CANCELLED_SENSOR_NAME,
    )
    compare_metrics(
        result,
        shipping_type,
        order_type,
        (brand_name if brand_save else OTHER_BRAND_NAME),
        CANCELLATION_REASON,
        (value if brand_save else OTHER_BRAND_COUNTER_VALUE),
        allowed_order_type and enabled,
    )

    mocked_time.sleep(1)

    await stq_runner.eats_order_stats_cancel_order.call(
        task_id='cancel_order',
        kwargs=prepare_order('300-400', place_id, shipping_type, order_type),
    )
    result = await taxi_eats_order_stats_monitor.get_metric(
        CANCELLED_SENSOR_NAME,
    )
    compare_metrics(
        result,
        shipping_type,
        order_type,
        (brand_name if brand_save else OTHER_BRAND_NAME),
        CANCELLATION_REASON,
        (value + 1 if brand_save else OTHER_BRAND_COUNTER_VALUE + 1),
        allowed_order_type and enabled,
    )


@pytest.mark.pgsql('eats_order_stats', files=['orders_metrics.sql'])
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
@pytest.mark.config(
    EATS_ORDER_STATS_METRICS_SENDER_SETTINGS={
        'cancelled_metrics_enabled': True,
        'finished_metrics_enabled': True,
        'brand_ids_to_save': [],
        'brands_to_save': [{'brand_id': str(BRAND_ID[0])}],
        'allowed_order_types': [ORDER_TYPE],
    },
)
@pytest.mark.parametrize(
    'sensor,cancellation_reason',
    [
        (CANCELLED_SENSOR_NAME, CANCELLATION_REASON),
        (FINISHED_SENSOR_NAME, NO_CANCELLATION_REASON),
    ],
)
@pytest.mark.parametrize(
    'time_to_reset,last_order_at,now_time,reseted',
    [
        ('21:00:00', '2022-01-01 23:00:00', '2022-01-02T01:00:00', True),
        ('09:00:00', '2022-01-01 11:00:00', '2022-01-01T13:00:00', True),
        ('21:00:00', '2022-01-01 00:00:00', '2022-01-10T00:00:00', True),
        ('21:00:00', '2022-01-01 20:00:00', '2022-01-01T22:00:00', False),
        ('21:00:00', '2022-01-10 23:00:00', '2022-01-01T01:00:00', False),
    ],
)
async def test_reset(
        prepare_order,
        compare_metrics,
        stq_runner,
        taxi_eats_order_stats,
        taxi_eats_order_stats_monitor,
        pgsql,
        mocked_time,
        taxi_config,
        sensor,
        cancellation_reason,
        time_to_reset,
        last_order_at,
        now_time,
        reseted,
):
    order_type = ORDER_TYPE
    shipping_type = PICKUP_SHIPPING_TYPE
    brand_name = BRAND_NAME[0]
    place_id = str(PLACE_ID[0])
    taxi_config.set(
        EATS_ORDER_STATS_RESET_METRICS_CONFIG={
            'check_interval': 60,
            'time_to_reset': time_to_reset,
            'enabled': True,
        },
    )
    await taxi_eats_order_stats.tests_control(reset_metrics=True)
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        (
            'UPDATE eats_order_stats_v2.orders_metrics_data'
            ' SET last_order_at=\'{}+03\''
        ).format(last_order_at),
    )

    mocked_time.set(
        datetime.datetime.fromisoformat('{}+03:00'.format(now_time)),
    )
    if sensor == CANCELLED_SENSOR_NAME:
        await stq_runner.eats_order_stats_cancel_order.call(
            task_id='cancel_order',
            kwargs=prepare_order(
                '200-300', place_id, PICKUP_SHIPPING_TYPE, ORDER_TYPE,
            ),
        )
    else:
        await stq_runner.eats_order_stats_finish_order.call(
            task_id='finish_order',
            kwargs=prepare_order(
                '200-300', place_id, PICKUP_SHIPPING_TYPE, ORDER_TYPE,
            ),
        )
    result = await taxi_eats_order_stats_monitor.get_metric(sensor)
    compare_metrics(
        result,
        shipping_type,
        order_type,
        brand_name,
        cancellation_reason,
        (1 if reseted else 3),
    )


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
@pytest.mark.config(
    EATS_ORDER_STATS_METRICS_SENDER_SETTINGS={
        'cancelled_metrics_enabled': True,
        'finished_metrics_enabled': True,
        'brand_ids_to_save': [],
        'brands_to_save': [],
        'allowed_order_types': [ORDER_TYPE],
    },
)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize(
    'sensor', [FINISHED_SENSOR_NAME, CANCELLED_SENSOR_NAME],
)
@pytest.mark.parametrize(
    'time_to_reset,order_time,now_time,reseted',
    [
        pytest.param(
            '00:00:00',
            '2022-01-01 23:00:00',
            '2022-01-02T01:00:00',
            True,
            id='Next day, reset_time passed',
        ),
        pytest.param(
            '15:00:00',
            '2022-01-01 14:00:01',
            '2022-01-01T16:00:00',
            True,
            id='Same day, reset_time passed',
        ),
        pytest.param(
            '00:00:00',
            '2022-01-01 00:00:00',
            '2022-01-10T00:00:00',
            True,
            id='More than one day passed',
        ),
        pytest.param(
            '12:00:00',
            '2022-01-01 20:00:00',
            '2022-01-01T22:00:00',
            False,
            id='Same day, reset_time not passed (will be just on next day)',
        ),
        pytest.param(
            '14:00:00',
            '2022-01-01 08:00:00',
            '2022-01-01T12:00:00',
            False,
            id='Same day, reset_time not passed (will be today, but later)',
        ),
        pytest.param(
            '00:00:00',
            '2022-01-10 23:00:00',
            '2022-01-01T01:00:00',
            False,
            id='Going back in time',
        ),
    ],
)
async def test_reset_periodic(
        testpoint,
        compare_metrics,
        prepare_order,
        taxi_eats_order_stats,
        taxi_eats_order_stats_monitor,
        stq_runner,
        pgsql,
        taxi_config,
        mocked_time,
        enabled,
        sensor,
        time_to_reset,
        order_time,
        now_time,
        reseted,
):
    brand_name = OTHER_BRAND_NAME
    shipping_type = DELIVERY_SHIPPING_TYPE
    cancellation_reason = (
        NO_CANCELLATION_REASON
        if sensor == FINISHED_SENSOR_NAME
        else CANCELLATION_REASON
    )
    value = 0 if reseted and enabled else 1

    taxi_config.set(
        EATS_ORDER_STATS_RESET_METRICS_CONFIG={
            'check_interval': 60,
            'time_to_reset': time_to_reset,
            'enabled': enabled,
        },
    )

    await taxi_eats_order_stats.tests_control(reset_metrics=True)

    mocked_time.set(
        datetime.datetime.fromisoformat('{0}+00:00'.format(order_time)),
    )

    reset_time = None

    last_reset_time_to_zero = True

    @testpoint('zero_reset_time')
    def _zero_reset_time(data):  # pylint: disable=unused-variable
        nonlocal reset_time
        reset_time = data
        nonlocal last_reset_time_to_zero
        return {'last_reset_time_to_zero': last_reset_time_to_zero}

    await taxi_eats_order_stats.run_periodic_task(TASK_NAME)

    last_reset_time_to_zero = False

    if sensor == FINISHED_SENSOR_NAME:
        queue = stq_runner.eats_order_stats_finish_order
    elif sensor == CANCELLED_SENSOR_NAME:
        queue = stq_runner.eats_order_stats_cancel_order
    else:
        assert False, 'Unknown sensor name'

    await queue.call(
        task_id='finish_order',
        kwargs=prepare_order(
            '200-300', str(PLACE_ID[0]), shipping_type, ORDER_TYPE,
        ),
    )

    mocked_time.set(
        datetime.datetime.fromisoformat('{0}+00:00'.format(now_time)),
    )

    await taxi_eats_order_stats.run_periodic_task(TASK_NAME)

    result = await taxi_eats_order_stats_monitor.get_metric(sensor)
    compare_metrics(
        result,
        shipping_type,
        ORDER_TYPE,
        brand_name,
        cancellation_reason,
        value,
        True,
    )

    cursor = pgsql['eats_order_stats'].cursor()
    query = 'SELECT * FROM eats_order_stats_v2.orders_metrics_data'
    cursor.execute(query)
    result = list(row for row in cursor)
    assert len(result) == 1
    assert len(result[0]) == 7
    assert result[0][0] == sensor
    assert result[0][1] == brand_name
    assert result[0][2] == ORDER_TYPE
    assert result[0][3] == shipping_type
    assert result[0][4] == cancellation_reason
    assert (
        result[0][5].astimezone(datetime.timezone.utc).isoformat()
        == datetime.datetime.fromisoformat(
            reset_time
            if (reseted and enabled)
            else '{0}+00:00'.format(order_time),
        ).isoformat()
    )
