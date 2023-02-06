import pytest


# pylint: disable=wrong-import-order, import-error, import-only-modules
import tests_driver_status.fallback_queue as fallback_queue
import tests_driver_status.utils as utils
# pylint: enable=wrong-import-order, import-error, import-only-modules


def _enqueue_events_from_json(redis_store, input_data):
    events = [
        fallback_queue.to_storage_master_order_event(item)
        for item in input_data['events']
    ]
    for event in events:
        fallback_queue.store_master_order_event(
            redis_store, fallback_queue.MASTER_ORDER_QUEUE, event,
        )
    return len(events)


@pytest.mark.suspend_periodic_tasks('fallback-queues-size-check')
@pytest.mark.config(
    DRIVER_STATUS_FALLBACK_QUEUE_COMMITTER={
        '__default__': {'batch_size': 1, 'event_max_age_s': 60},
    },
)
async def test_queue_size(
        taxi_driver_status, testpoint, redis_store, load_json, mocked_time,
):
    @testpoint('fallback_event_queues_check_tp')
    def _queue_size_check_tp(data):
        pass

    await taxi_driver_status.enable_testpoints()
    _queue_size_check_tp.flush()

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == 0

    input_data = load_json('input_5_events.json')

    mocked_time.set(utils.parse_date_str(input_data['now']))
    await taxi_driver_status.invalidate_caches(clean_update=True)

    expected_count = _enqueue_events_from_json(redis_store, input_data)

    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == expected_count

    input_data = load_json('input_3_events.json')

    mocked_time.set(utils.parse_date_str(input_data['now']))
    await taxi_driver_status.invalidate_caches(clean_update=True)

    expected_count += _enqueue_events_from_json(redis_store, input_data)

    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == expected_count

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == 0


@pytest.mark.suspend_periodic_tasks('fallback-queues-size-check')
@pytest.mark.config(
    DRIVER_STATUS_FALLBACK_QUEUE_COMMITTER={
        '__default__': {'batch_size': 1, 'event_max_age_s': 60},
    },
)
async def test_queue_size_limiter(
        taxi_driver_status, testpoint, redis_store, load_json, mocked_time,
):
    @testpoint('fallback_event_queues_check_tp')
    def _queue_size_check_tp(data):
        pass

    @testpoint('fallback_queues_age_limiter_tp')
    def _queue_size_limiter_tp(data):
        pass

    await taxi_driver_status.enable_testpoints()
    _queue_size_check_tp.flush()
    _queue_size_limiter_tp.flush()

    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    await taxi_driver_status.run_periodic_task('fallback-queues-age-limiter')
    await _queue_size_limiter_tp.wait_call()
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == 0

    input_data = load_json('input_5_events.json')

    mocked_time.set(utils.parse_date_str(input_data['now']))
    await taxi_driver_status.invalidate_caches(clean_update=True)

    _enqueue_events_from_json(redis_store, input_data)

    await taxi_driver_status.run_periodic_task('fallback-queues-age-limiter')
    await _queue_size_limiter_tp.wait_call()
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
    call_result = await _queue_size_check_tp.wait_call()
    result = call_result['data']['master_order_queue_size']
    assert result == input_data['expected_size']
