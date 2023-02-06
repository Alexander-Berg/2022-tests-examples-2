# pylint: disable=wrong-import-order, import-error
import pytest

import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils

DRIVER_STATUS_PG_CACHES_CONFIG = {
    '__default__': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
    },
    'driver-orders-cache': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 10000},
    },
}


def _clean_and_store_events_from_input_data(redis_store, input_events):
    fallback_queue.clear(redis_store, fallback_queue.STATUS_EVENT_QUEUE)
    events = [
        fallback_queue.to_storage_status_event(item) for item in input_events
    ]
    for event in events:
        fallback_queue.store_status_event(
            redis_store, fallback_queue.STATUS_EVENT_QUEUE, event,
        )
    assert len(input_events) == fallback_queue.size(
        redis_store, fallback_queue.STATUS_EVENT_QUEUE,
    )


def _convert_cache_result(data):
    converted = {}
    if not data:
        return converted

    for item in data:
        contractor_id = (item['profile_id'], item['park_id'])
        if contractor_id not in converted:
            converted[contractor_id] = {'orders': {}}
        updated_ts = int(item['db_updated_ts'] / 1000)
        if updated_ts not in converted[contractor_id]['orders']:
            converted[contractor_id]['orders'][updated_ts] = {}
        alias_id = item['alias_id']
        order_info = {'provider': item['provider'], 'status': item['status']}
        converted[contractor_id]['orders'][updated_ts][alias_id] = order_info
    return converted


# pylint: disable=redefined-outer-name
# NOTE: we must properly set 'updated_ts' for events for the fallback
# status event queue because we can't reset 'last_fallback_revision_' time!
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param(
            'test2.json', id='persistence and fallback queue update. 0 events',
        ),
        pytest.param(
            'test3.json', id='only persistence storage update. 10 events',
        ),
        pytest.param('test4.json', id='only fallback queue update. 10 events'),
        pytest.param(
            'test5.json',
            id='5 persistence + 5 fallback events. Not overlapping. Both.',
        ),
        pytest.param(
            'test7.json',
            id='overlapping orders: persistent older than the fallback',
        ),
        pytest.param(
            'test8.json',
            id='overlapping orders: fallback older than the persistent',
        ),
        pytest.param('test9.json', id='overlapping orders: mixed freshness'),
    ],
)
@pytest.mark.config(DRIVER_STATUS_PG_CACHES=DRIVER_STATUS_PG_CACHES_CONFIG)
async def test_cache_update(
        pgsql,
        testpoint,
        mocked_time,
        taxi_driver_status,
        load_json,
        taxi_config,
        input_file,
        redis_store,
):
    @testpoint('orders_testpoint')
    def _orders_testpoint(data):
        pass

    await taxi_driver_status.enable_testpoints()

    input_data = load_json(input_file)

    # 1. set mocked_time
    mocked_time.set(utils.parse_date_str(input_data['now']))

    # 2. invalidate and clean all caches to distribute time value.
    # We make full update of the caches to set the mocked time
    # in 'revision' value
    await taxi_driver_status.invalidate_caches(clean_update=True)

    # 3. drop initial call of testpoint
    _orders_testpoint.flush()

    # 4. storing events into the fallback queue
    _clean_and_store_events_from_input_data(redis_store, input_data['events'])
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')

    # 5. storing data into the persistent storage
    persistent_storage_data = helpers.to_input_repr(input_data.get('storage'))
    helpers.upsert_orders(pgsql, persistent_storage_data)

    # 6. triggering cache update
    await taxi_driver_status.invalidate_caches(clean_update=True)
    result = await _orders_testpoint.wait_call()

    # 7. comparing expected value of the update mode
    expected_is_full_update = not input_data['events']

    assert result['data']['is_full_update'] == expected_is_full_update

    # . comparing expected value of the cache
    expected = fallback_queue.to_comparable_status_repr(input_data['expected'])
    for _, contractor in expected.items():
        contractor.pop('statuses')
    converted = _convert_cache_result(result['data']['records'])
    assert converted == expected
