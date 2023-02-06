import json

import pytest

from tests_eats_retail_business_alerts import utils
from tests_eats_retail_business_alerts.lb_consumers.order_client_events_consumer import (  # noqa: E501
    constants,
)

MESSAGE_COOKIE = 'cookie1'


@pytest.mark.pgsql('eats_retail_business_alerts', files=['init_place.sql'])
@pytest.mark.parametrize(
    **utils.gen_list_params('order_type', ['retail', 'shop']),
)
async def test_created_event(
        testpoint,
        push_lb_message,
        stq,
        # parametrize params
        order_type,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == MESSAGE_COOKIE

    payload = {
        'order_event': 'created',
        'order_nr': constants.ORDER_NR,
        'place_id': str(constants.PLACE_ID),
        'order_type': order_type,
    }
    await push_lb_message(
        topic_name=constants.LOGBROKER_TOPIC,
        consumer_name=constants.CONSUMER_NAME,
        cookie=MESSAGE_COOKIE,
        data=json.dumps(payload),
    )
    await commit.wait_call()

    assert stq.eats_retail_business_alerts_save_order.times_called == 1
    task_info = stq.eats_retail_business_alerts_save_order.next_call()
    assert task_info['kwargs']['order_nr'] == payload['order_nr']
    assert task_info['kwargs']['place_id'] == int(payload['place_id'])
