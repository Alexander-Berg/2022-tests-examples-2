# pylint: disable=import-only-modules, import-error
import base64

from grocery_event_bus import test_protobuf_event_pb2
import pytest

# noqa: IS001
from tests_grocery_dispatch_tracking.events import (  # noqa: IS001
    BadBulkEvent,  # noqa: IS001
    BulkEvent,  # noqa: IS001
    Event,  # noqa: IS001
)  # noqa: IS001

TEST_BULK_MAX_SIZE = 2

EVENT_BUS_SETTINGS = pytest.mark.config(
    GROCERY_EVENT_BUS_EVENT_SETTINGS={
        '__default__': {
            'is-processing-enabled': True,
            'fetch-delay-if-disabled-ms': 1,
            'fetch-deadline-ms': 1,
            'bulk-max-size': TEST_BULK_MAX_SIZE,
            'start-retry-sleep-ms': 1,
            'max-retry-sleep-ms': 2000,
            'max-retries': 5,
        },
    },
)


async def test_basic(taxi_grocery_dispatch_tracking, push_event, testpoint):
    event = Event()

    @testpoint('test_event')
    def event_handle(data):
        assert data == {'event': event.dict()}

    # Testpoint kicks in every commit
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        assert cookie == 'cookie_1'

    @testpoint('logbroker_publish')
    def event_publish(data):
        assert data['data'] == event.json()
        assert data['name'] == 'test-event'

    await push_event(event, consumer='test-event')
    await taxi_grocery_dispatch_tracking.run_task('test-event-consumer-task')

    await event_handle.wait_call()
    await event_commit.wait_call()
    await event_publish.wait_call()


async def test_proto(taxi_grocery_dispatch_tracking, push_event, testpoint):
    event = test_protobuf_event_pb2.TestProtobufEvent()
    event.first_int32 = 1000
    event.second_str = 'Test'

    @testpoint('test_protobuf_event')
    def event_handle(data):
        assert data[0] == (
            f'first_int32: {event.first_int32}\n'
            f'second_str: "{event.second_str}"\n'
        )

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        assert cookie == 'cookie_1'

    @testpoint('logbroker_publish_b64')
    def event_publish(data):
        expected_event = test_protobuf_event_pb2.TestProtobufEvent()
        event_data = base64.b64decode(data['data'])
        expected_event.ParseFromString(event_data)

        assert data['name'] == 'test-protobuf-event'
        assert expected_event == event

    await push_event(event, consumer='test-protobuf-event')
    await taxi_grocery_dispatch_tracking.run_task(
        'test-protobuf-event-consumer-task',
    )

    await event_handle.wait_call()
    await event_commit.wait_call()
    await event_publish.wait_call()


@pytest.mark.config(
    GROCERY_EVENT_BUS_EVENT_SETTINGS={
        '__default__': {
            'is-processing-enabled': True,
            'fetch-delay-if-disabled-ms': 1,
            'fetch-deadline-ms': 1,
            'bulk-max-size': TEST_BULK_MAX_SIZE,
        },
    },
)
async def test_bulk_events(
        taxi_grocery_dispatch_tracking,
        push_event_bulk,
        testpoint,
        taxi_config,
):
    @testpoint('test_bulk_event')
    def event_handle(events):
        pass

    # Testpoint kicks in every commit
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    events = [BulkEvent(test_key=f'test_value_{i}') for i in range(1, 4)]

    await push_event_bulk(events, consumer='test-bulk-event')
    # 1st bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )
    # 2nd bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    # 1st bulk
    assert await event_handle.wait_call(1) == {
        'events': [events[0].dict(), events[1].dict()],
    }
    # 2nd bulk
    assert await event_handle.wait_call(1) == {'events': [events[2].dict()]}

    assert await event_commit.wait_call(1) == {'cookie': 'cookie_0'}
    assert await event_commit.wait_call(1) == {'cookie': 'cookie_1'}
    assert await event_commit.wait_call(1) == {'cookie': 'cookie_2'}


@EVENT_BUS_SETTINGS
async def test_skip_failed_to_parse_in_bulk_events(
        taxi_grocery_dispatch_tracking, push_event_bulk, testpoint,
):
    @testpoint('test_bulk_event')
    def event_handle(events):
        pass

    # Testpoint kicks in every commit
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    events = [
        BulkEvent(test_key='test_value_1'),
        BulkEvent(test_key='test_value_2'),
        BadBulkEvent(bad_key='bad_value_3'),
        BulkEvent(test_key='test_value_4'),
    ]

    await push_event_bulk(events, consumer='test-bulk-event')
    # 1st bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )
    # 2nd bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    # 1st bulk
    assert await event_handle.wait_call() == {
        'events': [events[0].dict(), events[1].dict()],
    }
    # 2nd bulk
    assert await event_handle.wait_call() == {'events': [events[3].dict()]}

    assert await event_commit.wait_call() == {'cookie': 'cookie_0'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_1'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_2'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_3'}


@EVENT_BUS_SETTINGS
async def test_all_events_parse_failed_in_bulk(
        taxi_grocery_dispatch_tracking, push_event_bulk, testpoint,
):
    @testpoint('test_bulk_event')
    def event_handle(events):
        pass

    # Testpoint kicks in every commit
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    events = [
        BadBulkEvent(bad_key='bad_value_1'),
        BadBulkEvent(bad_key='bad_value_2'),
        BulkEvent(test_key='test_value_3'),
    ]

    await push_event_bulk(events, consumer='test-bulk-event')
    # 1st bulk event loop iteration
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )
    # 2nd bulk event loop iteration
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    # Kicks in only 2nd bulk
    assert await event_handle.wait_call() == {'events': [events[2].dict()]}

    assert await event_commit.wait_call() == {'cookie': 'cookie_0'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_1'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_2'}


async def test_is_processing_enabled_one_message(
        taxi_grocery_dispatch_tracking, push_event, testpoint, taxi_config,
):
    event = Event()

    @testpoint('after_fetch_message_sleep')
    def after_sleep(data):
        pass

    # initial config
    taxi_config.set_values(
        {
            'GROCERY_EVENT_BUS_EVENT_SETTINGS': {
                '__default__': {
                    'is-processing-enabled': False,
                    'fetch-delay-if-disabled-ms': 1,
                    'fetch-deadline-ms': 1,
                },
            },
        },
    )
    await taxi_grocery_dispatch_tracking.invalidate_caches()

    await push_event(event, consumer='test-event')
    await taxi_grocery_dispatch_tracking.run_task('test-event-consumer-task')

    await after_sleep.wait_call()

    # update config
    taxi_config.set_values(
        {
            'GROCERY_EVENT_BUS_EVENT_SETTINGS': {
                '__default__': {
                    'is-processing-enabled': True,
                    'fetch-delay-if-disabled-ms': 1,
                    'fetch-deadline-ms': 1,
                },
            },
        },
    )
    await taxi_grocery_dispatch_tracking.invalidate_caches()

    # basic commit-publish test
    @testpoint('test_event')
    def event_handle(data):
        assert data == {'event': event.dict()}

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        assert cookie == 'cookie_1'

    @testpoint('logbroker_publish')
    def event_publish(data):
        assert data['data'] == event.json()
        assert data['name'] == 'test-event'

    await taxi_grocery_dispatch_tracking.run_task('test-event-consumer-task')

    await event_handle.wait_call(1)
    await event_commit.wait_call(1)
    await event_publish.wait_call(1)


async def test_is_processing_enabled_bulk_message(
        taxi_grocery_dispatch_tracking,
        push_event_bulk,
        testpoint,
        taxi_config,
):
    @testpoint('after_fetch_message_sleep')
    def after_sleep(data):
        pass

    # initial config
    taxi_config.set_values(
        {
            'GROCERY_EVENT_BUS_EVENT_SETTINGS': {
                '__default__': {
                    'is-processing-enabled': False,
                    'fetch-delay-if-disabled-ms': 1,
                    'fetch-deadline-ms': 1,
                    'bulk-max-size': TEST_BULK_MAX_SIZE,
                },
            },
        },
    )
    await taxi_grocery_dispatch_tracking.invalidate_caches()

    events = [BulkEvent(test_key=f'test_value_{i}') for i in range(1, 4)]

    await push_event_bulk(events, consumer='test-bulk-event')
    # 1st bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )
    await after_sleep.wait_call()

    # update config
    taxi_config.set_values(
        {
            'GROCERY_EVENT_BUS_EVENT_SETTINGS': {
                '__default__': {
                    'is-processing-enabled': True,
                    'fetch-delay-if-disabled-ms': 1,
                    'fetch-deadline-ms': 1,
                    'bulk-max-size': TEST_BULK_MAX_SIZE,
                },
            },
        },
    )
    await taxi_grocery_dispatch_tracking.invalidate_caches()

    @testpoint('test_bulk_event')
    def event_handle(events):
        pass

    # Testpoint kicks in every commit
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    # 1st bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )
    # 2nd bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    # 1st bulk
    assert await event_handle.wait_call() == {
        'events': [events[0].dict(), events[1].dict()],
    }
    # 2nd bulk
    assert await event_handle.wait_call() == {'events': [events[2].dict()]}

    assert await event_commit.wait_call() == {'cookie': 'cookie_0'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_1'}
    assert await event_commit.wait_call() == {'cookie': 'cookie_2'}


@EVENT_BUS_SETTINGS
async def test_bulk_event_retry_if_retryable_exception_catched(
        taxi_grocery_dispatch_tracking,
        push_event_bulk,
        testpoint,
        taxi_config,
):
    inject = True

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    @testpoint('retry_inject_error_bulk_event')
    def inject_error(data):
        nonlocal inject
        res = {'is_inject_error': inject}
        inject = False  # don't inject on next invocation
        return res

    await push_event_bulk([BulkEvent()], consumer='test-bulk-event')

    # handle bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    assert await event_commit.wait_call() == {'cookie': 'cookie_0'}
    assert inject_error.times_called == 2  # 1 retry expected


@EVENT_BUS_SETTINGS
async def test_event_retry_if_retryable_exception_catched(
        taxi_grocery_dispatch_tracking, push_event, testpoint, taxi_config,
):
    inject = True

    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    @testpoint('retry_inject_error_event')
    def inject_error(data):
        nonlocal inject
        res = {'is_inject_error': inject}
        inject = False  # don't inject on next invocation
        return res

    await push_event(Event(), consumer='test-event')

    # handle bulk
    await taxi_grocery_dispatch_tracking.run_task('test-event-consumer-task')

    assert await event_commit.wait_call() == {'cookie': 'cookie_1'}
    assert inject_error.times_called == 2  # 1 retry expected


@EVENT_BUS_SETTINGS
async def test_max_retries(
        taxi_grocery_dispatch_tracking, push_event_bulk, testpoint,
):
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    @testpoint('retry_inject_error_bulk_event')
    def inject_error(data):
        res = {'is_inject_error': True}  # always inject
        return res

    await push_event_bulk([BulkEvent()], consumer='test-bulk-event')

    # handle bulk
    await taxi_grocery_dispatch_tracking.run_task(
        'test-bulk-event-consumer-task',
    )

    assert await event_commit.wait_call() == {'cookie': 'cookie_0'}
    assert inject_error.times_called == 6  # initial + 5 retries
