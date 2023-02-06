import datetime

import bson
import pytest

from chatterbox import stq_task


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.parametrize(
    ('fields', 'completed', 'call_id', 'task_id', 'expected_call_data'),
    [
        (
            {
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
            },
            False,
            'outgoing_5b2cae5cb2682a976914c2a5_123',
            bson.ObjectId('5b2cae5cb2682a976914c2a5'),
            {
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
            },
        ),
        (
            {
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'answered_at': '2021-12-30T09:23:59+0000',
                'status_completed': 'bridged',
            },
            False,
            'outgoing_5b2cae5cb2682a976914c2a5_123',
            bson.ObjectId('5b2cae5cb2682a976914c2a5'),
            {
                'answered_at': '2021-12-30T09:23:59+0000',
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'status_completed': 'bridged',
            },
        ),
        (
            {
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
            },
            True,
            'outgoing_5b2cae5cb2682a976914c2a5_123',
            bson.ObjectId('5b2cae5cb2682a976914c2a5'),
            {
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                'stat_created': datetime.datetime(2018, 7, 18, 11, 20),
            },
        ),
        (
            {
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_124',
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
            },
            True,
            'outgoing_5b2cae5cb2682a976914c2a5_124',
            bson.ObjectId('5b2cae5cb2682a976914c2a5'),
            {
                'answered_at': '2018-05-06T11:32:43Z',
                'call_record_id': '1234',
                'completed_at': '2021-12-30T09:23:59+0000',
                'hangup_disposition': 'caller_bye',
                'id': 'outgoing_5b2cae5cb2682a976914c2a5_124',
                'stat_created': datetime.datetime(2018, 7, 18, 11, 20),
                'status_completed': 'bridged',
            },
        ),
    ],
)
async def test_handle_outgoing_call_messages(
        cbox,
        fields,
        task_id,
        call_id,
        completed,
        expected_call_data,
        mock_support_tags_save_tags,
):
    await stq_task.chatterbox_handle_outgoing_call(
        cbox.app, task_id, fields, completed=completed,
    )
    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert (
        next(
            filter(
                lambda x: x.get('id') == call_id, task['meta_info']['calls'],
            ),
            False,
        )
        == expected_call_data
    )
    if completed:
        assert task['meta_info']['ivr_call_status'] == 'not_active'
