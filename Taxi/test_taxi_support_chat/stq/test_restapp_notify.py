# pylint: disable=redefined-outer-name,no-member
import datetime

import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    'chat_id, message_id, expected_args,' 'expected_kwargs',
    [
        (
            bson.ObjectId('5a433ca8779fb3302cc784bf'),
            'message_91',
            [
                '+79001234567',
                '5a433ca8779fb3302cc784bf',
                {'$date': 1531311350000},
                'ROLE_MANAGER',
            ],
            {'log_extra': None},
        ),
    ],
)
@pytest.mark.now('2019-07-10T11:20:00')
async def test_restapp_notify(
        stq3_context: stq_context.Context,
        stq,
        chat_id,
        message_id,
        expected_args,
        expected_kwargs,
):
    await stq_task.restapp_notify_task(stq3_context, chat_id, message_id, None)
    call = stq.eats_restapp_support_chat_handle_event.next_call()
    call.pop('id')
    assert call == {
        'queue': 'eats_restapp_support_chat_handle_event',
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'args': expected_args,
        'kwargs': expected_kwargs,
    }
