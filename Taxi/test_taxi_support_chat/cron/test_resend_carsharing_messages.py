import datetime

import pytest

from taxi.util import dates

from taxi_support_chat.generated.cron import run_cron


@pytest.mark.now('2021-07-15T12:00:00+0')
@pytest.mark.config(
    RESEND_CARSHARING_MESSAGES_CRONTASK=True,
    RESEND_CARSHARING_MESSAGES_MAX_SEC=120,
    RESEND_CARSHARING_MESSAGES_MIN_SEC=60,
)
async def test_resend_carsharing_messages(cron_context, stq, mockserver):
    config = cron_context.config
    query = {
        'messages.metadata.sent_to_carsharing': {'$exists': False},
        'type': 'carsharing_support',
        'updated': {
            '$gt': dates.utcnow() - datetime.timedelta(
                seconds=config.RESEND_CARSHARING_MESSAGES_MAX_SEC,
            ),
            '$lt': dates.utcnow() - datetime.timedelta(
                seconds=config.RESEND_CARSHARING_MESSAGES_MIN_SEC,
            ),
        },
    }
    not_sent_chat = (
        await cron_context.mongo.secondary.user_chat_messages.find_one(query)
    )

    assert not_sent_chat is not None

    @mockserver.json_handler('/drive/api/taxi_chat/messages/add')
    def _mock_drive(request):
        return {}

    await run_cron.main(
        ['taxi_support_chat.crontasks.resend_carsharing_messages', '-t', '0'],
    )

    call = stq.send_events_to_carsharing.next_call()
    call.pop('id')
    assert call == {
        'queue': 'send_events_to_carsharing',
        'args': [None, {'$oid': 'f9cc2a0e6c5239fb421d496e'}],
        'kwargs': {},
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
    }
    assert stq.is_empty
