import collections

import pytest

from tests_order_metrics import utils


ORDER_EVENTS_TOPIC = '/taxi/processing/testisuite/order-events'

LB_CONSUMER = 'order-events'

# dict annotation makes mypy happy for some reason
# https://github.com/python/mypy/issues/5849
DEFAULT_MESSAGE: dict = {
    'order_id': 'test_order_id',
    'status': 'test_status',
    'event_key': 'test_event_key',
    'event_index': 0,
}


async def test_logbroker_read(taxi_order_metrics, testpoint):
    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        DEFAULT_MESSAGE,
    )


async def test_required_fields(taxi_order_metrics, testpoint):
    empty_message = {}

    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        empty_message,
        need_commit=False,
    )


async def test_has_metrics_output(
        taxi_order_metrics, testpoint, taxi_order_metrics_monitor,
):
    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        DEFAULT_MESSAGE,
    )

    monitor = taxi_order_metrics_monitor
    metrics = await monitor.get_metrics('order-events-metrics')

    assert metrics['order-events-metrics']


@pytest.mark.parametrize(
    'message,expected_diff',
    [
        pytest.param(
            {
                **DEFAULT_MESSAGE,
                'is_cashback': True,
                'is_plus_cashback': True,
                'is_discount_cashback': False,
            },
            {'cashback.created': 1, 'cashback.created.plus': 1},
            id='plus cashback only',
        ),
        pytest.param(
            {
                **DEFAULT_MESSAGE,
                'is_cashback': True,
                'is_plus_cashback': False,
                'is_discount_cashback': True,
            },
            {'cashback.created': 1, 'cashback.created.discount': 1},
            id='discount cashback only',
        ),
        pytest.param(
            {
                **DEFAULT_MESSAGE,
                'is_cashback': True,
                'is_plus_cashback': True,
                'is_discount_cashback': True,
            },
            {
                'cashback.created': 1,
                'cashback.created.plus': 1,
                'cashback.created.discount': 1,
            },
            id='both cashbacks',
        ),
        pytest.param(
            {
                **DEFAULT_MESSAGE,
                'is_cashback': None,
                'is_plus_cashback': None,
                'is_discount_cashback': None,
            },
            {},
            id='no cashback',
        ),
    ],
)
async def test_cashback_metrics(
        taxi_order_metrics,
        testpoint,
        taxi_order_metrics_monitor,
        message,
        expected_diff,
):
    base_metrics = collections.defaultdict(int)
    update = (
        await taxi_order_metrics_monitor.get_metrics(
            prefix='order-events-metrics.cashback',
        )
    )['order-events-metrics'] or {}
    base_metrics.update(**update)

    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        message,
    )

    new_metrics = (
        await taxi_order_metrics_monitor.get_metrics(
            prefix='order-events-metrics.cashback',
        )
    )['order-events-metrics']

    diff = {}
    for metric in new_metrics:
        if not metric.startswith('cashback'):
            continue
        metric_diff = new_metrics[metric] - base_metrics[metric]
        if metric_diff:
            diff[metric] = metric_diff

    assert diff == expected_diff


@pytest.mark.config(ORDER_METRICS_CONSUMERS_ENABLED=[])
async def test_disable_consumer(taxi_order_metrics, testpoint):
    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        DEFAULT_MESSAGE,
        need_commit=False,
    )


@pytest.mark.config(ORDER_METRICS_SENDING_ENABLED=False)
async def test_disable_sending(
        taxi_order_metrics, testpoint, taxi_order_metrics_monitor,
):
    await utils.send_lb_message(
        taxi_order_metrics,
        testpoint,
        LB_CONSUMER,
        ORDER_EVENTS_TOPIC,
        DEFAULT_MESSAGE,
    )

    monitor = taxi_order_metrics_monitor
    metrics = await monitor.get_metrics('order-events-metrics')

    assert metrics['order-events-metrics'] == {}
