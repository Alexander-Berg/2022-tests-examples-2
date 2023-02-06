import datetime

import pytest

from chatterbox.crontasks import webhooks_monitor
from chatterbox.internal import startrack_manager

NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.now(NOW.isoformat())
async def test_webhooks_monotor(
        cbox_context,
        db,
        loop,
        mock_st_search,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_update_ticket,
):
    mock_st_get_comments([])
    mock_st_update_ticket('open')
    with pytest.raises(startrack_manager.PendingTicketsError):
        await webhooks_monitor.do_stuff(cbox_context, loop)
    search_call = mock_st_search.calls[0]
    assert search_call['kwargs'] == {
        'json_filter': {
            'queue': ['SUPPORT', 'TICKETSFORMS'],
            'webhookStatus': 'pending',
            'updated': {'to': '2018-06-15T15:29:00+0300'},
        },
    }

    task = await db.support_chatterbox.find_one(
        {'external_id': 'YANDEXTAXI-0'},
    )
    assert task
    assert task['chat_type'] == 'startrack'
    assert task['line'] == 'mail'
    assert task['status'] == 'predispatch'
    assert task['tags'] == []
    assert task['meta_info'] == {
        'queue': 'YANDEXTAXI',
        'support_email': 'test@support',
        'ticket_subject': 'some summary',
        'user_email': 'some_client@email',
        'webhook_calls': 1,
    }
