# pylint: disable=redefined-outer-name,no-member
import datetime

import bson
import pytest

from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    'chat_id, message_id, update_type, put_task, expected_args,'
    'expected_kwargs',
    [
        (
            bson.ObjectId('5a433ca8779fb3302cc784bf'),
            'message_91',
            'reply',
            True,
            [
                'park_id',
                '5a433ca8779fb3302cc784bf',
                'reply',
                {'$date': 1531311350000},
            ],
            {'message_id': 'message_91', 'log_extra': None},
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784bf'),
            '',
            'update',
            True,
            [
                'park_id',
                '5a433ca8779fb3302cc784bf',
                'update',
                {'$date': 1531311350000},
            ],
            {'log_extra': None},
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784bb'),
            '',
            'update',
            True,
            [
                'park_id',
                '5a433ca8779fb3302cc784bb',
                'update',
                {'$date': 1531311350000},
            ],
            {'log_extra': None},
        ),
        (
            bson.ObjectId('5a433ca8779fb3302cc784b1'),
            'message_opteum',
            'reply',
            False,
            [
                'park_id',
                '5a433ca8779fb3302cc784bf',
                'reply',
                {'$date': 1531311350000},
            ],
            {'message_id': 'message_91', 'log_extra': None},
        ),
    ],
)
@pytest.mark.now('2019-07-10T11:20:00')
async def test_task(
        stq3_context,
        stq,
        chat_id,
        message_id,
        update_type,
        put_task,
        expected_args,
        expected_kwargs,
):
    await stq_task.opteum_notify_task(
        stq3_context, chat_id, message_id, None, update_type=update_type,
    )
    if put_task:
        call = stq.taxi_fleet_support_chat_handle_event.next_call()
        call.pop('id')
        assert call == {
            'queue': 'taxi_fleet_support_chat_handle_event',
            'eta': datetime.datetime(1970, 1, 1, 0, 0),
            'args': expected_args,
            'kwargs': expected_kwargs,
        }
    else:
        assert stq.is_empty
