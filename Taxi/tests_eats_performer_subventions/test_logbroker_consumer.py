import json

import pytest

from tests_eats_performer_subventions import utils

LOGBROKER_TOPIC = '/eda/processing/production/order-client-events'
CONSUMER = 'order-client-events-consumer'

LOGBROKER_TESTPOINT = 'logbroker_commit'
CONSUMER_TESTPOINT = 'eats-performer-subventions::events-consumed'
PROCESSING_TESTPOINT = 'eats-performer-subventions::event-processed'


CONSUMER_TASK = 'order-client-events-consumer-lb_consumer'

LB_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 100,
        'queue_timeout_ms': 1,
        'config_poll_period_ms': 1,
    },
}


@pytest.mark.parametrize(
    'order_event, stq_expected_calls',
    [
        ('created', 1),
        ('finished', 1),
        ('cancelled', 1),
        ('taken', 0),
        ('payed', 0),
    ],
)
@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_LOGBROKER_CONSUMER_SETTINGS=LB_SETTINGS,
)
async def test_create_order(
        taxi_eats_performer_subventions,
        testpoint,
        stq,
        order_event,
        stq_expected_calls,
):
    order_nr = 'order-nr'
    order_status = order_event
    created_at = utils.parse_datetime('2021-09-16T12:00:00.1234+03:00')

    @testpoint(LOGBROKER_TESTPOINT)
    def commit(cookie):
        assert cookie == order_nr

    @testpoint(PROCESSING_TESTPOINT)
    def after_processing(_):
        pass

    event = utils.make_event(order_nr, order_status, created_at)
    response = await taxi_eats_performer_subventions.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': CONSUMER,
                'data': json.dumps(event),
                'topic': LOGBROKER_TOPIC,
                'cookie': order_nr,
            },
        ),
    )
    assert response.status_code == 200
    await taxi_eats_performer_subventions.run_task(CONSUMER_TASK)
    await commit.wait_call()
    await after_processing.wait_call()

    stq_called = stq.eats_performer_subventions_order_events.times_called
    assert stq_called == stq_expected_calls
    if stq_called:
        task_info = stq.eats_performer_subventions_order_events.next_call()
        kwargs = task_info['kwargs']
        assert kwargs['order_nr'] == event['order_nr']
        assert kwargs['order_status'] == event['order_event']
        assert kwargs['payment_type'] == event['payment_method']
