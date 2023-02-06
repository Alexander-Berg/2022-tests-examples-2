# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals
import datetime
import http

import bson
import pytest

NOW = datetime.datetime(2019, 8, 27, 9, 10)


@pytest.fixture(autouse=True)
def set_test_user(patch_auth):
    patch_auth(login='test_user')


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
    },
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
)
@pytest.mark.parametrize(
    'task_id, action, params, data, expected_history',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'forward',
            {'line': 'second'},
            {},
            {
                'action_id': 'test_uid',
                'action': 'forward',
                'line': 'first',
                'new_line': 'second',
                'login': 'test_user',
                'in_addition': False,
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 12,
                ),
                'query_params': {'line': 'second'},
            },
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            'forward',
            {'line': 'second'},
            {},
            {
                'action_id': 'test_uid',
                'action': 'forward',
                'line': 'first',
                'new_line': 'second',
                'login': 'test_user',
                'in_addition': False,
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 16,
                ),
                'query_params': {'line': 'second'},
            },
        ),
        ('5b2cae5cb2682a976914c2a3', 'forward', {'line': 'second'}, {}, None),
        ('5b2cae5cb2682a976914c2a4', 'forward', {'line': 'second'}, {}, None),
        ('5b2cae5cb2682a976914c2a5', 'forward', {'line': 'second'}, {}, None),
        ('5b2cae5cb2682a976914c2a6', 'forward', {'line': 'second'}, {}, None),
        (
            '5b2cae5cb2682a976914c2a1',
            'communicate',
            {},
            {'comment': 'test'},
            {
                'action_id': 'test_uid',
                'action': 'communicate',
                'comment': 'test',
                'line': 'first',
                'login': 'test_user',
                'in_addition': False,
                'created': NOW,
                'latency': 41200504,
                'speed_answer_start': datetime.datetime(2019, 8, 27, 9, 0, 12),
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'close',
            {},
            {'comment': 'test'},
            {
                'action_id': 'test_uid',
                'action': 'close',
                'line': 'first',
                'login': 'test_user',
                'in_addition': False,
                'comment': 'test',
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 12,
                ),
                'speed_answer_start': datetime.datetime(2019, 8, 27, 9, 0, 12),
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'dismiss',
            {
                'chatterbox_button': 'chatterbox_nto',
                'additional_tag': 'nto_tag',
            },
            {'tags': ['double tag', 'double tag']},
            {
                'action_id': 'test_uid',
                'action': 'dismiss',
                'line': 'first',
                'login': 'test_user',
                'in_addition': False,
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 12,
                ),
                'speed_answer_start': datetime.datetime(2019, 8, 27, 9, 0, 12),
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'chatterbox_button',
                        'value': 'chatterbox_nto',
                    },
                ],
                'tags_changes': [
                    {'change_type': 'add', 'tag': 'double tag'},
                    {'change_type': 'add', 'tag': 'nto_tag'},
                ],
                'tags_added': ['double tag', 'nto_tag'],
                'query_params': {
                    'chatterbox_button': 'chatterbox_nto',
                    'additional_tag': 'nto_tag',
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'take',
            {},
            {'lines': ['first'], 'force': True},
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            'close',
            {},
            {'comment': 'test'},
            {
                'action_id': 'test_uid',
                'action': 'close',
                'line': 'first',
                'login': 'test_user',
                'in_addition': False,
                'comment': 'test',
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 14,
                ),
                'speed_answer_start': datetime.datetime(2019, 8, 27, 9, 0, 14),
            },
        ),
        (
            '5b2cae5cb2682a976914c2a8',
            'close',
            {},
            {'comment': 'test'},
            {
                'action_id': 'test_uid',
                'action': 'close',
                'line': 'first',
                'login': 'test_user',
                'in_addition': False,
                'comment': 'test',
                'created': NOW,
                'latency': 41200504,
                'online_chat_processing_start': datetime.datetime(
                    2019, 8, 27, 9, 0, 10,
                ),
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_set_full_resolve(
        cbox,
        task_id,
        action,
        params,
        data,
        expected_history,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    await cbox.post(
        '/v1/tasks/%s/%s' % (task_id, action), params=params, data=data,
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )
    if expected_history:
        assert task['history'][-1] == expected_history
    else:
        assert not task['history'][-1].get('online_chat_processing_start')
        assert not task['history'][-1].get('speed_answer_start')
