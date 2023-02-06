import datetime

import bson
import pytest


@pytest.mark.now('2019-07-24T10:00:00')
@pytest.mark.parametrize(
    'task_id, expected_status, expected_db_record',
    [
        (bson.ObjectId('5d388906779fb318087520d5'), 404, {}),
        (bson.ObjectId('5b2cae5db2682a976914c2a2'), 409, {}),
        (bson.ObjectId('5b2cae5cb2682a976914c2a3'), 409, {}),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            200,
            {
                '_id': bson.ObjectId('5b2cae5cb2682a976914c2a1'),
                'external_id': 'chat_1',
                'status': 'accepted',
                'support_admin': 'superuser',
                'updated': datetime.datetime(2019, 7, 24, 10),
                'history': [
                    {
                        'action': 'accept_task',
                        'login': 'superuser',
                        'created': datetime.datetime(2019, 7, 24, 10),
                    },
                ],
            },
        ),
    ],
)
async def test_accept_task(cbox, task_id, expected_status, expected_db_record):
    await cbox.post('/v1/tasks/{}/accept'.format(task_id), data={})
    assert cbox.status == expected_status

    if expected_status == 200:
        task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
        assert task == expected_db_record
