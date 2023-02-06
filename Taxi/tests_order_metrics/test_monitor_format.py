import copy

import pytest

from tests_order_metrics import utils


ORDER_EVENTS_TOPIC = '/taxi/processing/testisuite/order-events'

LB_CONSUMER = 'order-events'

DEFAULT_MESSAGE = {
    'order_id': 'test_order_id',
    'status': 'test_status',
    'event_key': 'test_event_key',
    'event_index': 0,
    'testsuite': True,
}


@pytest.mark.parametrize(
    'messages',
    [
        [
            {'payment_type': 'card', 'nz': 'moscow'},
            {'payment_type': 'card', 'nz': 'moscow'},
            {'payment_type': 'cash', 'nz': 'moscow'},
            {'payment_type': 'cash'},
            {'payment_type': 'applepay'},
            {'payment_type': 'googlepay'},
        ],
    ],
)
async def test_metrics_format(
        taxi_order_metrics,
        testpoint,
        taxi_order_metrics_monitor,
        load_json,
        messages,
):
    for msg in messages:
        msg.update(copy.deepcopy(DEFAULT_MESSAGE))
        await utils.send_lb_message(
            taxi_order_metrics,
            testpoint,
            LB_CONSUMER,
            ORDER_EVENTS_TOPIC,
            msg,
        )

    monitor = taxi_order_metrics_monitor
    metrics = await monitor.get_metrics('order-events-metrics')

    expected = load_json('response.json')
    response = metrics['order-events-metrics']['testsuite_total']

    assert response == expected
