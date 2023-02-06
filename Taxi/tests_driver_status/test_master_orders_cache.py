import datetime
import json

import pytest
import pytz

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.enum_constants import ProcessingStatus
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils


DRIVER_STATUS_PG_CACHES_CONFIG = {
    '__default__': {
        'full_update': {'chunk_size': 0, 'correction_ms': 0},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 0},
    },
    'master-orders-cache': {
        'full_update': {'chunk_size': 0, 'correction_ms': 3000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 2000},
    },
}


def _to_input_repr(events):
    if not events:
        return {}

    converted = {}
    for event in events:
        profile_id = event.get('profile_id')
        park_id = event.get('park_id')
        order_id = event.get('order_id')
        alias_id = event.get('alias_id')
        order_status = event.get('status')
        provider = event.get('provider')
        updated_ts = event.get('updated_ts')
        event_ts = event.get('event_ts')

        assert profile_id
        assert park_id
        assert order_id
        assert alias_id
        assert order_status
        assert OrderStatus.contains(order_status)
        assert provider
        assert event_ts

        order_value = {
            'order_id': order_id,
            'status': order_status,
            'updated_ts': updated_ts if updated_ts else event_ts,
            'event_ts': event_ts,
        }
        key = (profile_id, park_id)

        if key not in converted:
            converted[key] = {alias_id: order_value}
        else:
            converted[key][alias_id] = order_value

    return converted


def _convert_cache_result(data):
    if not data:
        return {}

    converted = {}
    for item in data:
        alias_id = item.get('alias_id')
        profile_id = item.get('profile_id')
        park_id = item.get('park_id')
        status = item.get('status')
        provider = item.get('provider')
        event_ts = int(item.get('event_ts') / 1000)

        key = (alias_id, park_id, profile_id)
        converted[key] = {
            'status': status,
            'provider': provider,
            'event_ts': event_ts,
        }

    return converted


async def _insert_order(
        taxi_driver_status,
        park_id,
        profile_id,
        alias_id,
        status=OrderStatus.kDriving,
        provider=None,
        event_ts=None,
):
    body = {
        'alias_id': alias_id,
        'park_id': park_id,
        'profile_id': profile_id,
        'status': status,
    }
    if provider:
        body['provider'] = provider
    if event_ts:
        body['timestamp'] = event_ts

    response = await taxi_driver_status.post(
        'v2/order/store', data=json.dumps(body),
    )
    assert response.status_code == 200


def _replace_updated_ts(pgsql, park_id, profile_id, alias_id, updated_ts):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        f"""
        UPDATE ds.master_orders
        SET updated_ts = '{updated_ts}'
        WHERE contractor_id IN (
            SELECT id FROM ds.drivers
            WHERE park_id = '{park_id}' AND driver_id = '{profile_id}'
            AND alias_id = '{alias_id}'
        );
        """,
    )


def _clear_row(pgsql, park_id, profile_id, alias_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        f"""
        DELETE FROM ds.master_orders
        WHERE alias_id = '{alias_id}'
        AND contractor_id IN (
            SELECT id FROM ds.drivers
            WHERE park_id = '{park_id}' AND driver_id = '{profile_id}'
            AND alias_id = '{alias_id}'
        );
        """,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
@pytest.mark.parametrize('finish_order_by_client', [True, False])
async def test_cache_update_full(
        taxi_driver_status,
        taxi_config,
        pgsql,
        testpoint,
        mocked_time,
        finish_order_by_client,
):
    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    def _check_record(profile_id, alias_id, status, provider):
        assert record['profile_id'] == profile_id
        assert record['alias_id'] == alias_id
        assert record['status'] == status
        assert record['provider'] == provider

    taxi_config.set_values(
        {
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': True,
                'start_by_processing': False,
                'finish_by_client': finish_order_by_client,
            },
        },
    )

    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()

    # insert active order
    await _insert_order(
        taxi_driver_status,
        'park0',
        'profile0',
        'alias0',
        OrderStatus.kDriving,
        'yandex',
    )
    _replace_updated_ts(
        pgsql,
        'park0',
        'profile0',
        'alias0',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )
    # insert complete order
    await _insert_order(
        taxi_driver_status,
        'park1',
        'profile1',
        'alias1',
        OrderStatus.kComplete,
        None,
    )
    _replace_updated_ts(
        pgsql,
        'park1',
        'profile1',
        'alias1',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )
    # insert cancelled order
    await _insert_order(
        taxi_driver_status,
        'park2',
        'profile2',
        'alias2',
        OrderStatus.kCancelled,
        None,
    )
    _replace_updated_ts(
        pgsql,
        'park2',
        'profile2',
        'alias2',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )

    # now we expect that cache contains all records:
    # active as it should be
    # complete depending on finish_by_client config
    # cancelled because of update correction
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert data['is_full_update']
    records = data['records']
    assert len(records) == 3 if finish_order_by_client else 2
    for record in records:
        park_id = record['park_id']
        assert park_id in ('park0', 'park1', 'park2')
        if park_id == 'park0':
            _check_record('profile0', 'alias0', OrderStatus.kDriving, 'yandex')
        elif park_id == 'park1':
            _check_record(
                'profile1', 'alias1', OrderStatus.kComplete, 'unknown',
            )
        else:
            _check_record(
                'profile2', 'alias2', OrderStatus.kCancelled, 'unknown',
            )

    # after 5 minutes we expect active order
    # and complete order depending on finish_by_client config
    mocked_time.sleep(300)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert data['is_full_update']
    records = data['records']
    assert len(records) == 2 if finish_order_by_client else 1
    for record in records:
        park_id = record['park_id']
        assert park_id in ('park0', 'park1')
        if park_id == 'park0':
            _check_record('profile0', 'alias0', OrderStatus.kDriving, 'yandex')
        else:
            _check_record(
                'profile1', 'alias1', OrderStatus.kComplete, 'unknown',
            )

    # after 15 minutes we expect only active order
    mocked_time.sleep(600)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert data['is_full_update']
    records = data['records']
    assert len(records) == 1
    assert records[0]['alias_id'] == 'alias0'

    # remove active orders
    # and now we expect empty cache
    _clear_row(pgsql, 'park0', 'profile0', 'alias0')
    mocked_time.sleep(600)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert data['is_full_update']
    assert not data['records']


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
async def test_cache_update_incr(
        taxi_driver_status, pgsql, testpoint, mocked_time,
):
    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()

    # insert active order
    await _insert_order(
        taxi_driver_status,
        'park0',
        'profile0',
        'alias0',
        OrderStatus.kDriving,
        'yandex',
    )
    _replace_updated_ts(
        pgsql,
        'park0',
        'profile0',
        'alias0',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )
    # insert complete order
    await _insert_order(
        taxi_driver_status,
        'park1',
        'profile1',
        'alias1',
        OrderStatus.kComplete,
        None,
    )
    _replace_updated_ts(
        pgsql,
        'park1',
        'profile1',
        'alias1',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )

    # we expect both records in incr update
    await taxi_driver_status.invalidate_caches(clean_update=False)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    assert len(data['records']) == 2

    # after 10 minutes we expect to see the same orders
    # (incr update doesn't modify cache data)
    mocked_time.sleep(600)
    await taxi_driver_status.invalidate_caches(clean_update=False)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    assert len(data['records']) == 2

    # after full update
    # we expect to see only active orders
    # (incr update doesn't modify cache data as it was after full update)
    mocked_time.sleep(600)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()
    await taxi_driver_status.invalidate_caches(clean_update=False)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    records = data['records']
    assert len(records) == 1
    assert records[0]['alias_id'] == 'alias0'


@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
@pytest.mark.suspend_periodic_tasks('fallback-queues-size-check')
async def test_fallback(
        taxi_driver_status, pgsql, redis_store, testpoint, mocked_time,
):
    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()

    # insert active order
    await _insert_order(
        taxi_driver_status,
        'park0',
        'profile0',
        'alias0',
        OrderStatus.kDriving,
        'yandex',
    )
    _replace_updated_ts(
        pgsql,
        'park0',
        'profile0',
        'alias0',
        mocked_time.now().replace(tzinfo=pytz.UTC),
    )

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    fallback_queue.store_master_order_event(
        redis_store,
        fallback_queue.MASTER_ORDER_QUEUE,
        fallback_queue.to_storage_master_order_event(
            {
                'alias_id': 'alias1',
                'park_id': 'park1',
                'profile_id': 'profile1',
                'status': OrderStatus.kTransporting,
                'provider': 'yandex',
                'event_ts': mocked_time.now().replace(tzinfo=pytz.UTC),
            },
        ),
    )
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    assert len(data['records']) == 2


@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
@pytest.mark.suspend_periodic_tasks('fallback-queues-size-check')
async def test_fallback_timestamp(
        taxi_driver_status, pgsql, redis_store, testpoint, mocked_time,
):
    # clear redis storage from the previous tests
    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)

    # inject persistet storage failure
    @testpoint('persistent_storage_store_tp')
    def _inject_failure_tp(data):
        return {'inject_failure': True}

    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    now = mocked_time.now().replace(tzinfo=pytz.UTC)

    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()

    await _insert_order(
        taxi_driver_status,
        'park0',
        'profile0',
        'alias0',
        OrderStatus.kDriving,
        'yandex',
        utils.date_to_ms(now + datetime.timedelta(seconds=5)),
    )

    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    await taxi_driver_status.invalidate_caches(
        cache_names=['master-orders-cache'],
    )
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    assert len(data['records']) == 1

    await _insert_order(
        taxi_driver_status,
        'park1',
        'profile1',
        'alias1',
        OrderStatus.kDriving,
        'yandex',
        utils.date_to_ms(now - datetime.timedelta(seconds=5)),
    )

    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    await taxi_driver_status.invalidate_caches(
        cache_names=['master-orders-cache'],
    )
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    assert len(data['records']) == 2


@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
async def test_processing_event(
        taxi_driver_status,
        pgsql,
        processing_lb,
        testpoint,
        mocked_time,
        redis_store,
):
    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')

    await taxi_driver_status.invalidate_caches(clean_update=True)
    _master_orders_testpoint.flush()

    alias_id = 'alias1'
    park_id = 'park1'
    profile_id = 'profile1'
    status = OrderStatus.kWaiting
    processing_status = ProcessingStatus.kAssigned

    now = mocked_time.now().replace(tzinfo=pytz.utc)
    lb_event = {
        'alias': alias_id,
        'order_id': 'order1',
        'db_id': park_id,
        'driver_uuid': profile_id,
        'taxi_status': status,
        'status': processing_status,
        'event_key': 'unimportant',
        'event_index': 1,
    }
    await processing_lb.push(lb_event, now.timestamp())
    _replace_updated_ts(pgsql, park_id, profile_id, alias_id, now)

    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert data['is_full_update']
    records = data['records']
    assert len(records) == 1
    record = records[0]
    assert record['park_id'] == park_id
    assert record['profile_id'] == profile_id
    assert record['alias_id'] == alias_id
    assert record['status'] == status
    assert record['provider'] == 'yandex'

    mocked_time.sleep(10)
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    status = OrderStatus.kTransporting
    lb_event['taxi_status'] = status
    lb_event['event_index'] = 2
    await processing_lb.push(lb_event, now.timestamp())
    _replace_updated_ts(pgsql, park_id, profile_id, alias_id, now)

    await taxi_driver_status.invalidate_caches(clean_update=False)
    data = (await _master_orders_testpoint.wait_call())['data']
    assert not data['is_full_update']
    records = data['records']
    assert len(records) == 1
    record = records[0]
    assert record['park_id'] == park_id
    assert record['profile_id'] == profile_id
    assert record['alias_id'] == alias_id
    assert record['status'] == status
    assert record['provider'] == 'yandex'


# pylint: disable=redefined-outer-name
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.suspend_periodic_tasks('fallback-queues-size-check')
@pytest.mark.parametrize(
    'input_file,enable_terminal_status_preference',
    [
        pytest.param(
            'test1.json',
            False,
            id='cache update with terminal status preference disabled',
        ),
        pytest.param(
            'test2.json',
            True,
            id='cache update with terminal status preference enabled',
        ),
    ],
)
@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
async def test_fallback_cache_update_with_termination(
        pgsql,
        testpoint,
        mocked_time,
        taxi_driver_status,
        load_json,
        taxi_config,
        input_file,
        enable_terminal_status_preference,
        redis_store,
):
    @testpoint('master_orders_testpoint')
    def _master_orders_testpoint(data):
        pass

    await taxi_driver_status.enable_testpoints()

    taxi_config.set_values(
        {
            'DRIVER_STATUS_PG_CACHES': DRIVER_STATUS_PG_CACHES_CONFIG,
            'DRIVER_STATUS_ORDERS_FEATURES': {
                'merge_statuses': False,
                'start_by_processing': False,
                'enable_terminal_status_preference': (
                    enable_terminal_status_preference
                ),
            },
        },
    )
    await taxi_driver_status.invalidate_caches()

    input_data = load_json(input_file)

    # 1. set mocked_time
    mocked_time.set(utils.parse_date_str(input_data['now']))

    # 2. invalidate and clean all caches to distribute time value.
    # We make full update of the caches to set the mocked time
    # in 'revision' value
    await taxi_driver_status.invalidate_caches(clean_update=True)

    # 3. drop initial call of testpoint
    _master_orders_testpoint.flush()

    # 4. storing events into the fallback queue
    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    events = [
        fallback_queue.to_storage_master_order_event(item)
        for item in input_data['events']
    ]
    for event in events:
        fallback_queue.store_master_order_event(
            redis_store, fallback_queue.MASTER_ORDER_QUEUE, event,
        )
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')

    # 5. storing data into the persistent storage
    persistent_storage_data = _to_input_repr(input_data.get('initial'))
    helpers.upsert_master_orders(pgsql, persistent_storage_data)
    pg_orders = helpers.get_pg_master_orders(pgsql)
    expected = fallback_queue.to_comparable_master_order_repr(
        input_data['initial'],
    )
    assert pg_orders == expected

    # 6. triggering cache update
    await taxi_driver_status.invalidate_caches(clean_update=True)
    data = (await _master_orders_testpoint.wait_call())['data']

    # 7. comparing expected value of the update mode
    expected_is_full_update = not input_data['events']

    assert data['is_full_update'] == expected_is_full_update

    # 8. comparing expected value of the cache
    expected = fallback_queue.to_comparable_master_order_repr(
        input_data['expected'],
    )

    for _, order in expected.items():
        order.pop('order_id')
    converted = _convert_cache_result(data['records'])
    assert converted == expected
