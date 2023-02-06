# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals
import http

import bson
import pytest


@pytest.mark.parametrize(
    'task_id_str, query, expected_update_kwargs',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'tags': ['retry_csat'],
            },
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': True,
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'tags': ['tag_1', 'tag_2'],
            },
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'comment': 'chat closed', 'tags': ['no_csat', 'UpperКир']},
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {'comment': 'chat closed', 'tags': ['no_csat', 'UpperКир']},
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'tags': ['tag_1', 'tag_2'],
            },
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': True,
                },
            },
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'tags': ['tag_1', 'tag_2'],
            },
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': True,
                },
            },
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_RETRY_CSAT_CONDITIONS=[
        {'tags': {'#in': ['retry_csat', 'test_tag']}},
        {'meta_info/phone_type': 'yandex'},
    ],
)
async def test_close(
        cbox,
        task_id_str,
        query,
        expected_update_kwargs,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_comments,
):
    mock_chat_get_history({'messages': []})
    mock_st_get_comments([])
    await cbox.post('/v1/tasks/{}/close'.format(task_id_str), data=query)
    assert cbox.status == http.HTTPStatus.OK
    task_id = bson.ObjectId(task_id_str)
    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    if expected_update_kwargs is not None:
        add_update_call = mock_chat_add_update.calls[0]
        assert add_update_call['args'] == (task['external_id'],)
        add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == expected_update_kwargs
