import pytest

import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils


async def _run_component(taxi_driver_status):
    await taxi_driver_status.run_task('fallback-queue-committer.testsuite')


def _merge_pg_results(statuses, orders):
    result = {
        key: {
            'statuses': {utils.date_to_ms(item['updated_ts']): item['status']},
        }
        for key, item in statuses.items()
    }
    for key, contractor_orders in orders.items():
        for alias_id, order_info in contractor_orders.items():
            if 'orders' not in result[key]:
                result[key]['orders'] = {}
            updated_ts = utils.date_to_ms(order_info['updated_ts'])
            if updated_ts not in result[key]['orders']:
                result[key]['orders'][updated_ts] = {}
            result[key]['orders'][updated_ts][alias_id] = {
                'status': order_info['status'],
                'provider': order_info['provider'],
            }

    return result


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

    @testpoint('status-event-queue-peek-testpoint')
    def _peek_testpoint(data):
        pass

    await taxi_driver_status.enable_testpoints()
    _peek_testpoint.flush()

    fallback_queue.clear(redis_store, fallback_queue.STATUS_EVENT_QUEUE)
    events = [
        fallback_queue.to_storage_status_event(item)
        for item in input_data['events']
    ]
    for event in events:
        fallback_queue.store_status_event(
            redis_store, fallback_queue.STATUS_EVENT_QUEUE, event,
        )

    await _run_component(taxi_driver_status)
    call_result = await _peek_testpoint.wait_call()
    result = fallback_queue.to_comparable_status_repr(call_result['data'])
    expected = fallback_queue.to_comparable_status_repr(events)
    assert result == expected
    assert (
        fallback_queue.size(redis_store, fallback_queue.STATUS_EVENT_QUEUE)
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
    'input_file',
    [pytest.param('proper_events.json', id='with all proper events')],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_commit(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
        pgsql,
):
    await _peek_and_commit(
        taxi_driver_status,
        testpoint,
        redis_store,
        load_json,
        input_file,
        mocked_time,
    )

    input_data = load_json(input_file)

    # checking data in postgres
    pg_statuses = helpers.get_pg_driver_statuses(pgsql)
    pg_orders = helpers.get_pg_orders(pgsql)

    merged_result = _merge_pg_results(pg_statuses, pg_orders)
    expected = fallback_queue.to_comparable_status_repr(input_data['expected'])
    assert merged_result == expected
