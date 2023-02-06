# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=C0103
import json

import pytest

from eats_retail_magnit_parser.components import loyalty
from eats_retail_magnit_parser.stq import loyalty as stq_loyalty

TASK_ID = 'task_id'
ORDER_ID = 'order_id'
USER_ID = 1000
PLACE_ID = 'place_id'
ORIGIN_PLACE_ID = 'origin_place_id'


class TaskInfo:
    id = 'task_id'
    exec_tries = 0


@pytest.fixture(name='bonus_points_notification')
def _bonus_points_notification(mockserver, load_json):
    @mockserver.handler('/eats-core-order-integration/v1/bonus-points')
    def notification(request):
        assert request.json == load_json('notification.json')
        return mockserver.make_response('', 201)

    return notification


@pytest.fixture(name='order_revision')
def _order_revision(mockserver, load_json):
    @mockserver.handler(
        '/eats-order-revision/v1/revision/latest/customer-services/details',
    )
    def order_revision(request):
        return mockserver.make_response(
            json.dumps(load_json('order_revision.json')), 200,
        )

    return order_revision


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_RETRIES_SETTINGS={'loyalty': 999},
)
@pytest.mark.parametrize('card_blocked', [True, False])
@pytest.mark.parametrize('process_card_blocked', [True, False])
async def test_stq(
        stq3_context,
        magnit_loyalty_mocks,
        bonus_points_notification,
        order_revision,
        card_blocked,
        process_card_blocked,
):
    magnit_loyalty_mocks['sales'].set_card_blocked(card_blocked)
    stq3_context.config.EATS_RETAIL_MAGNIT_PARSER_LOYALTY_PROCESS_BLOCKED = (
        process_card_blocked
    )
    task_info = TaskInfo()
    exception_occured = False
    try:
        await stq_loyalty.task(
            stq3_context,
            task_info,
            **{
                'order_id': ORDER_ID,
                'user_id': USER_ID,
                'origin_place_id': PLACE_ID,
            },
        )
    except loyalty.magnit_loyalty_client.MagnitLoyaltyClientException:
        exception_occured = True

    # if feature flag enabled
    # then there should not be exception
    assert not card_blocked or (process_card_blocked != exception_occured)
    assert order_revision.has_calls
    assert bonus_points_notification.has_calls != card_blocked
