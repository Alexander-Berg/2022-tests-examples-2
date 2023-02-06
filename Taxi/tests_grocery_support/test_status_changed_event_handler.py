# pylint: disable=import-only-modules
import pytest

from .events import GroceryOrderStatusChangedEvent

CONSUMER = 'grocery-order-status-changed'
CONSUMER_TASK = '{}-consumer-task'.format(CONSUMER)

TEST_BULK_MAX_SIZE = 2


def _assert_stq(stq_handler, task_id=None, **vargs):
    stq_call = stq_handler.next_call()
    if task_id is not None:
        assert stq_call['id'] == task_id
    kwargs = stq_call['kwargs']
    for key in vargs:
        assert kwargs[key] == vargs[key], key


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
        taxi_grocery_support, push_event_bulk, testpoint, stq,
):
    @testpoint('logbroker_commit')
    def event_commit(cookie):
        pass

    events = [
        GroceryOrderStatusChangedEvent(order_id=f'test_order_id_{i}')
        for i in range(1, 4)
    ]

    # consumer == topic == event in grocery_event_bus
    await push_event_bulk(events, consumer=CONSUMER)

    # start component: bulk consumption of tasks 0, 1
    await taxi_grocery_support.run_task(CONSUMER_TASK)

    _assert_stq(
        stq.grocery_support_process_status_changed_events,
        task_id='{}-{}-process-status-changed-events'.format(
            events[0].order_id, events[0].order_status,
        ),
        status_change_infos=[events[0].dict(), events[1].dict()],
    )
    assert await event_commit.wait_call(1) == {'cookie': 'cookie_0'}
    assert await event_commit.wait_call(1) == {'cookie': 'cookie_1'}

    # start component: bulk consumption of task 2
    # two starts because consumption lasts only 1 iteration in testuite
    await taxi_grocery_support.run_task(CONSUMER_TASK)

    _assert_stq(
        stq.grocery_support_process_status_changed_events,
        task_id='{}-{}-process-status-changed-events'.format(
            events[2].order_id, events[2].order_status,
        ),
        status_change_infos=[events[2].dict()],
    )
    assert await event_commit.wait_call(1) == {'cookie': 'cookie_2'}
