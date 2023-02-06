import pytest

# pylint: disable=wrong-import-order, import-error, import-only-modules
from tests_driver_status.enum_constants import OrderStatus
# pylint: enable=wrong-import-order, import-error, import-only-modules
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils


def to_input_repr(events):
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


async def _run_component(taxi_driver_status):
    await taxi_driver_status.run_task('fallback-queue-committer.testsuite')


async def _peek_and_commit(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
):
    input_data = load_json(input_file)
    mocked_time.set(utils.parse_date_str(input_data['now']))

    @testpoint('master-order-queue-peek-testpoint')
    def _peek_testpoint(data):
        pass

    await taxi_driver_status.enable_testpoints()
    _peek_testpoint.flush()

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    events = [
        fallback_queue.to_storage_master_order_event(item)
        for item in input_data['events']
    ]
    for event in events:
        fallback_queue.store_master_order_event(
            redis_store, fallback_queue.MASTER_ORDER_QUEUE, event,
        )

    await _run_component(taxi_driver_status)
    call_result = await _peek_testpoint.wait_call()
    result = fallback_queue.to_comparable_master_order_repr(
        call_result['data'],
    )
    expected = fallback_queue.to_comparable_master_order_repr(events)
    assert result == expected
    assert (
        fallback_queue.size(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
        == 0
    )


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('proper_events.json', id='with all proper events'),
        pytest.param('corrupted_events.json', id='with some corrupted events'),
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_peek_oldest(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
):
    await _peek_and_commit(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
    )


@pytest.mark.parametrize(
    'input_file, enable_terminal_status_preference,',
    [
        pytest.param('proper_events.json', False, id='with all proper events'),
        pytest.param(
            'proper_events_with_terminals.json',
            True,
            id='with all proper events - with terminal status preferece',
        ),
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_commit(
        taxi_driver_status,
        taxi_config,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
        enable_terminal_status_preference,
        pgsql,
):
    helpers.clear_master_orders(pgsql)
    input_data = load_json(input_file)

    if 'initial' in input_data:
        initial_orders = to_input_repr(input_data.get('initial'))
        helpers.upsert_master_orders(pgsql, initial_orders)
        pg_orders = helpers.get_pg_master_orders(pgsql)
        expected = fallback_queue.to_comparable_master_order_repr(
            input_data['initial'],
        )
        assert pg_orders == expected

    taxi_config.set_values(
        {
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

    await _peek_and_commit(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
    )

    # checking data in postgres
    pg_orders = helpers.get_pg_master_orders(pgsql)
    # print(pg_orders)
    expected = fallback_queue.to_comparable_master_order_repr(
        input_data['expected'],
    )
    assert pg_orders == expected
