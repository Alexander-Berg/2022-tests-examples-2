import json

import pytest

from tests_eats_retail_business_alerts import utils
from tests_eats_retail_business_alerts.lb_consumers.order_client_events_consumer import (  # noqa: E501
    constants,
)

MESSAGE_COOKIE = 'cookie1'


@pytest.mark.parametrize(
    **utils.gen_list_params('cancelled_by', ['courier', 'some_another_type']),
)
async def test_cancelled_event(
        testpoint,
        push_lb_message,
        stq,
        # parametrize params
        cancelled_by,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    payload = {
        'order_event': 'cancelled',
        'order_nr': constants.ORDER_NR,
        'cancelled_by': cancelled_by,
    }
    await push_lb_message(
        topic_name=constants.LOGBROKER_TOPIC,
        consumer_name=constants.CONSUMER_NAME,
        cookie=MESSAGE_COOKIE,
        data=json.dumps(payload),
    )
    await commit.wait_call()

    assert stq.eats_retail_business_alerts_cancel_order.times_called == 1
    task_info = stq.eats_retail_business_alerts_cancel_order.next_call()
    assert task_info['kwargs']['order_nr'] == payload['order_nr']
    assert task_info['kwargs']['cancelled_by'] == payload['cancelled_by']
