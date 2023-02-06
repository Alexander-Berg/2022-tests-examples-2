import datetime

import bson
import pytest

from test_chatterbox import plugins as conftest


@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_add_hidden_comment(
        cbox: conftest.CboxWrap, mock_random_str_uuid,
):
    mock_random_str_uuid()
    task = await cbox.app.tasks_manager.get_by_id(
        task_id=bson.ObjectId('5b2cae5cb2682a976914c2a1'),
    )
    updated_task = await cbox.app.tasks_manager.add_hidden_comment(
        task=task,
        login='some_user',
        hidden_comment='some comment',
        hidden_comment_metadata={'encrypt_key': '123'},
        tags=['tag'],
    )

    assert updated_task['inner_comments'] == [
        {
            'login': 'some_user',
            'comment': 'some comment',
            'created': datetime.datetime(2019, 1, 1, 12, 0),
            'encrypt_key': '123',
        },
    ]
    assert updated_task['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'hidden_comment',
        'hidden_comment': 'some comment',
        'created': datetime.datetime(2019, 1, 1, 12, 0),
        'in_addition': False,
        'line': 'first',
        'login': 'some_user',
        'latency': 43200.0,
        'tags_added': ['tag'],
        'tags_changes': [{'change_type': 'add', 'tag': 'tag'}],
    }
