import datetime
import json

import pytest
import pytz

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import OrderStatus
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as pg_helpers
import tests_driver_status.utils as utils

MOCKED_NOW_STR = '2022-01-31T00:00:00+0003'
MOCKED_NOW = utils.parse_date_str(MOCKED_NOW_STR)


async def _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        order_id,
        status,
        provider,
        event_ts,
        expected_code=200,
):
    body = {
        'park_id': park_id,
        'profile_id': profile_id,
        'alias_id': alias_id,
        'status': status,
    }
    if order_id:
        body['order_id'] = order_id
    if provider:
        body['provider'] = provider
    if event_ts:
        body['timestamp'] = event_ts

    response = await taxi_driver_status.post(
        'v2/order/store', data=json.dumps(body),
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'status,expected_code',
    [
        pytest.param(OrderStatus.kNone, 200, id='none'),
        pytest.param(OrderStatus.kDriving, 200, id='driving'),
        pytest.param(OrderStatus.kWaiting, 200, id='waiting'),
        pytest.param(OrderStatus.kTransporting, 200, id='transporting'),
        pytest.param(OrderStatus.kComplete, 200, id='complete'),
        pytest.param(OrderStatus.kFailed, 200, id='failed'),
        pytest.param(OrderStatus.kCancelled, 200, id='cancelled'),
        pytest.param(OrderStatus.kExpired, 200, id='expired'),
        pytest.param(OrderStatus.kPreexpired, 200, id='preexpired'),
        pytest.param(OrderStatus.kUnknown, 200, id='unknown'),
        pytest.param('nonexistent', 400, id='nonexistent status'),
    ],
)
async def test_order_status(
        taxi_driver_status, pgsql, mocked_time, status, expected_code,
):
    alias_id = 'alias'
    park_id = 'somepark'
    profile_id = 'someprofile'

    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        None,
        status,
        None,
        None,
        expected_code,
    )

    if expected_code == 200:
        pg_helpers.check_master_orders_table(
            pgsql,
            alias_id,
            park_id,
            profile_id,
            None,
            status,
            'unknown',
            mocked_time.now().replace(tzinfo=pytz.utc),
        )


@pytest.mark.now(MOCKED_NOW_STR)
@pytest.mark.parametrize(
    'order_status_db_lookup_for_notification',
    [
        pytest.param(False, id='cache race prevention disabled'),
        pytest.param(True, id='cache race prevention enabled'),
    ],
)
@pytest.mark.parametrize(
    'enable_terminal_status_preference',
    [
        pytest.param(True, id='enable terminal status preferece'),
        pytest.param(False, id='no termination preferece'),
    ],
)
@pytest.mark.parametrize(
    'prev_status, prev_event_ts, new_status,new_event_ts,'
    'expect_change_enabled, expect_change_disabled',
    [
        pytest.param(
            OrderStatus.kNone,
            None,
            OrderStatus.kDriving,
            MOCKED_NOW,
            True,
            True,
            id='incoming new active status, previous is absent',
        ),
        pytest.param(
            OrderStatus.kNone,
            None,
            OrderStatus.kComplete,
            MOCKED_NOW,
            True,
            True,
            id='incoming new terminal status, previous is absent',
        ),
        pytest.param(
            OrderStatus.kDriving,
            MOCKED_NOW,
            OrderStatus.kComplete,
            MOCKED_NOW + datetime.timedelta(seconds=110),
            True,
            True,
            id='incoming fresh terminal status, previous is an active',
        ),
        pytest.param(
            OrderStatus.kDriving,
            MOCKED_NOW,
            OrderStatus.kComplete,
            MOCKED_NOW - datetime.timedelta(seconds=110),
            True,
            False,
            id='incoming stale terminal status, previous is an active',
        ),
        pytest.param(
            OrderStatus.kComplete,
            MOCKED_NOW,
            OrderStatus.kDriving,
            MOCKED_NOW + datetime.timedelta(seconds=110),
            False,
            True,
            id='incoming fresh active status, previous is a terminal status',
        ),
        pytest.param(
            OrderStatus.kComplete,
            MOCKED_NOW,
            OrderStatus.kDriving,
            MOCKED_NOW - datetime.timedelta(seconds=110),
            False,
            False,
            id='incoming stale active status, previous is a terminal status',
        ),
        pytest.param(
            OrderStatus.kComplete,
            MOCKED_NOW,
            OrderStatus.kFailed,
            MOCKED_NOW + datetime.timedelta(seconds=110),
            True,
            True,
            id='incoming fresh terminal status, previous is a terminal status',
        ),
        pytest.param(
            OrderStatus.kComplete,
            MOCKED_NOW,
            OrderStatus.kFailed,
            MOCKED_NOW - datetime.timedelta(seconds=110),
            False,
            False,
            id='incoming stale terminal status, previous is a terminal status',
        ),
        pytest.param(
            OrderStatus.kWaiting,
            MOCKED_NOW,
            OrderStatus.kDriving,
            MOCKED_NOW + datetime.timedelta(seconds=110),
            True,
            True,
            id='incoming fresh active status, previous is an active status',
        ),
        pytest.param(
            OrderStatus.kDriving,
            MOCKED_NOW,
            OrderStatus.kWaiting,
            MOCKED_NOW - datetime.timedelta(seconds=110),
            False,
            False,
            id='incoming stale active status, previous is an active status',
        ),
    ],
)
async def test_terminal_status_preference(
        taxi_driver_status,
        taxi_config,
        pgsql,
        mocked_time,
        enable_terminal_status_preference,
        prev_status,
        prev_event_ts,
        new_status,
        new_event_ts,
        expect_change_enabled,
        expect_change_disabled,
        order_status_db_lookup_for_notification,
):
    pg_helpers.clear_master_orders(pgsql)

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': False,
                'start_by_processing': False,
                'enable_terminal_status_preference': (
                    enable_terminal_status_preference
                ),
                'order_status_db_lookup_for_notification': (
                    order_status_db_lookup_for_notification
                ),
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    alias_id = 'alias'
    park_id = 'somepark'
    profile_id = 'someprofile'

    if prev_status != OrderStatus.kNone:
        await _post_order(
            taxi_driver_status,
            park_id,
            profile_id,
            alias_id,
            None,
            prev_status,
            None,
            utils.date_to_ms(prev_event_ts),
            200,
        )

        pg_helpers.check_master_orders_table(
            pgsql,
            alias_id,
            park_id,
            profile_id,
            None,
            prev_status,
            'unknown',
            prev_event_ts,
        )

    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        None,
        new_status,
        None,
        utils.date_to_ms(new_event_ts),
        200,
    )

    is_change_expected = False
    if (enable_terminal_status_preference and expect_change_enabled) or (
            not enable_terminal_status_preference and expect_change_disabled
    ):
        is_change_expected = True

    expected_status = new_status if is_change_expected else prev_status
    expected_event_ts = new_event_ts if is_change_expected else prev_event_ts

    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        None,
        expected_status,
        'unknown',
        expected_event_ts,
    )


@pytest.mark.parametrize(
    'order_id',
    [
        pytest.param(None, id='order is not specified'),
        pytest.param('some_order_id', id='order specified'),
    ],
)
async def test_order_id(taxi_driver_status, pgsql, mocked_time, order_id):
    alias_id = 'alias'
    park_id = 'somepark'
    profile_id = 'someprofile'
    status = OrderStatus.kDriving

    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        order_id,
        status,
        None,
        None,
        200,
    )

    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        order_id,
        status,
        'unknown',
        mocked_time.now().replace(tzinfo=pytz.utc),
    )


@pytest.mark.redis_store(
    [
        'hset',
        'Order:SetCar:Items:Providers:parkid000',
        'alias_id_000',
        2,  # yandex
    ],
)
@pytest.mark.parametrize(
    'alias_id,request_provider,expected_stored_provider',
    [
        pytest.param(
            'alias_id_000',
            None,
            'yandex',
            id='order present in redis, provider is not specified in request',
        ),
        pytest.param(
            'alias_id_000',
            'formula',
            'formula',
            id=(
                'order present in redis, '
                'but other provider is specified in request'
            ),
        ),
        pytest.param(
            'alias_id_001',
            None,
            'unknown',
            id='order absent in redis, provider is not specified in request',
        ),
        pytest.param(
            'alias_id_001',
            'formula',
            'formula',
            id='order absent in redis, provider is specified in request',
        ),
    ],
)
async def test_provider(
        taxi_driver_status,
        pgsql,
        mocked_time,
        alias_id,
        request_provider,
        expected_stored_provider,
):
    park_id = 'parkid000'
    profile_id = 'profileid000'
    status = OrderStatus.kDriving

    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        None,
        status,
        request_provider,
        None,
        200,
    )

    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        None,
        status,
        expected_stored_provider,
        mocked_time.now().replace(tzinfo=pytz.utc),
    )


async def test_fallback_store(
        taxi_driver_status, redis_store, taxi_config, mocked_time, testpoint,
):
    # clear redis storage from the previous tests
    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)

    # set call timestamp
    event_ts = utils.parse_date_str('2021-05-17 00:01:07.0+00')
    mocked_time.set(event_ts)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    alias_id = 'alias01'
    park_id = 'park01'
    profile_id = 'profile01'
    status = OrderStatus.kDriving
    provider = 'yandex'
    event_ts_ms = utils.date_to_ms(event_ts)

    # inject persistet storage failure
    @testpoint('persistent_storage_store_tp')
    def _inject_failure_tp(data):
        return {'inject_failure': True}

    await _post_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        None,
        status,
        provider,
        event_ts_ms,
        200,
    )

    expected_event = {
        (alias_id, park_id, profile_id): {
            'order_id': None,
            'status': status,
            'provider': provider,
            'event_ts': event_ts_ms,
        },
    }

    result = fallback_queue.read_events(
        redis_store, fallback_queue.MASTER_ORDER_QUEUE,
    )
    assert expected_event == fallback_queue.to_comparable_master_order_repr(
        result,
    )
