# pylint:disable=redefined-outer-name
import datetime

import pytest

from taxi_support_chat.generated.cron import run_cron


@pytest.fixture
def mock_eats_order(mockserver, cron_context):
    @mockserver.json_handler('/eda-api', prefix=True)
    def _dummy_request(request):
        if request.url.endswith('/pending_order/work-status'):
            return mockserver.make_response(
                json={'order_nr': 'pending_order', 'status': 'in_work'},
            )
        if request.url.endswith('/finished_order/work-status'):
            return mockserver.make_response(
                json={'order_nr': 'finished_order', 'status': 'finished'},
            )
        if request.url.endswith('/recently_finished_order/work-status'):
            return mockserver.make_response(
                json={
                    'order_nr': 'recently_finished_order',
                    'status': 'finished',
                },
            )
        return mockserver.make_response(status=404)

    return _dummy_request


@pytest.mark.now('2018-01-01T00:00:00')
async def test_refresh_pending_eats_orders(mock_eats_order, cron_context):
    await run_cron.main(
        ['taxi_support_chat.crontasks.refresh_pending_eats_orders', '-t', '0'],
    )
    chats_by_id = {
        chat['_id']: chat
        async for chat in cron_context.mongo.user_chat_messages.find()
    }
    assert chats_by_id['finished_order_chat_id']['order_finished'] == (
        datetime.datetime(2017, 12, 31, 20, 26, 40)
    )
    assert chats_by_id['recently_finished_order_chat_id'][
        'order_finished'
    ] == (datetime.datetime(2018, 1, 1, 0, 0))
    assert chats_by_id['missing_order_chat_id']['order_missing']
    assert 'order_finished' not in chats_by_id['pending_order_chat_id']
    assert 'order_finished' not in chats_by_id['client_chat_id']
    assert mock_eats_order.times_called
