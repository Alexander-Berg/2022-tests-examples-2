import json
import pytest

from taxi.core import async

from django import test as django_test


@pytest.mark.parametrize(
    'request_params, history_request, history_response, expected_response', [
        (
            '?newer_than=newer_than_id',
            {
                'include_metadata': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'newer_than_id',
                    },
                },
            },
            {
                'metadata': {},
                'updates': [
                    {
                        "created_date": "created_date",
                        "message": {
                            "id": "msg_id",
                            "metadata": {},
                            "location": [
                                0, 1
                            ],
                            "sender": {
                                "id": "client_id",
                                "role": "client",
                            },
                            "text": "string",
                        },
                        "newest_message_id": "string",
                    },
                ],
            },
            {
                'items': [
                    {
                        'id': 'msg_id',
                        'author': 'client_id',
                        'author_role': 'client',
                        'timestamp': 'created_date',
                        'text': 'string',
                        'geopoint': {
                            'lon': 0,
                            'lat': 1
                        },
                    },
                ],
            },
        ),
        (
            '',
            {
                'include_metadata': True,
            },
            {
                'metadata': {
                    'comment': 'order comment',
                    'created_date': 'created_date',
                },
                'updates': [],
            },
            {
                'items': [
                    {
                        'id': 'comment_id',
                        'author': 'system',
                        'author_role': 'system',
                        'timestamp': 'created_date',
                        'text': 'order comment',
                    },
                ],
            },
        ),
        (
            '?newer_than=comment_id',
            {
                'include_metadata': True,
            },
            {
                'metadata': {
                    'comment': 'order comment',
                    'created_date': 'created_date',
                },
                'updates': [],
            },
            {
                'items': [],
            },
        ),
        (
            '?older_than=comment_id',
            {
                'must not': 'be called',
            },
            None,
            {
                'items': [],
            },
        ),
        (
            '?older_than=someid',
            {
                'include_metadata': True,
                'range': {
                    'message_ids': {
                        'older_than': 'someid',
                    },
                },
            },
            {
                'metadata': {
                    'comment': 'order comment',
                    'created_date': 'created_date',
                },
                'updates': [],
            },
            {
                'items': [
                    {
                        'id': 'comment_id',
                        'author': 'system',
                        'author_role': 'system',
                        'timestamp': 'created_date',
                        'text': 'order comment',
                    },
                ],
            },
        ),
        (
            '?older_than=someid',
            {
                'include_metadata': True,
                'range': {
                    'message_ids': {
                        'older_than': 'someid',
                    },
                },
            },
            {
                'metadata': {},
                'updates': [],
            },
            {
                'items': [],
            },
        ),
        (
            '',
            {
                'include_metadata': True,
            },
            {
                'metadata': {
                    'comment': 'order comment',
                    'created_date': 'created_date',
                },
                'updates': [
                    {
                        "created_date": "created_date",
                        "message": {
                            "id": "msg_id",
                            "metadata": {},
                            "location": [
                                0, 1
                            ],
                            "sender": {
                                "id": "client_id",
                                "role": "client",
                            },
                            "text": "string",
                        },
                        "newest_message_id": "string",
                    },
                    {
                        "created_date": "created_date",
                        "message": {
                            "id": "msg_id_z",
                            "metadata": {},
                            "sender": {
                                "id": "client_id",
                                "role": "client",
                            },
                            "text": "string",
                        },
                        'update_metadata': {
                            'key': 'value'
                        },
                        'update_participants': {
                            'action': 'add',
                            'role': 'client',
                            'id': 'client_id'
                        },
                        "newest_message_id": "string",
                    },
                ],
            },
            {
                'items': [
                    {
                        'id': 'msg_id',
                        'author': 'client_id',
                        'author_role': 'client',
                        'timestamp': 'created_date',
                        'text': 'string',
                        'geopoint': {
                            'lon': 0,
                            'lat': 1
                        },
                    },
                    {
                        'id': 'msg_id_z',
                        'author': 'client_id',
                        'author_role': 'client',
                        'timestamp': 'created_date',
                        'text': '[update chat metadata: {"key": "value"}]\n'
                                '[add client(id=client_id)]\nstring',
                    },
                    {
                        'id': 'comment_id',
                        'author': 'system',
                        'author_role': 'system',
                        'timestamp': 'created_date',
                        'text': 'order comment',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.asyncenv('blocking')
def test_get_history(patch, request_params, history_request, history_response,
                     expected_response):
    @patch('taxi.internal.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def find_one_by_id(order_id, **kwargs):
        assert order_id == 'order_id'

        yield async.return_value({'chat_id': 'chat_id'})

    @patch('taxi.external.chat.get_history')
    @async.inline_callbacks
    def get_history(chat_id, payload, chat_base_url, **kwrags):
        assert chat_id == 'chat_id'
        assert payload == history_request
        yield async.return_value(history_response)

    response = django_test.Client().get(
        '/api/chat/driverclient/order_id/' + request_params
    )
    assert response.status_code == 200, response.content

    content = json.loads(response.content)
    assert content == expected_response


@pytest.mark.asyncenv('blocking')
def test_get_yt_history(patch):
    @patch('taxi.internal.archive.get_order_proc_by_id')
    def get_order_proc_by_id(order_id, **kwargs):
        return {'chat_id': 'chat_id'}

    @patch('taxi.external.chat.get_history')
    @async.inline_callbacks
    def get_history(chat_id, payload, chat_base_url, **kwrags):
        assert chat_id == 'chat_id'
        assert payload == {
            'include_metadata': True,
        }
        yield async.return_value({
            'metadata': {
                'comment': 'order comment',
                'created_date': 'created_date',
            },
            'updates': [],
        })

    response = django_test.Client().get(
        '/api/chat/driverclient/order_id/'
    )
    assert response.status_code == 200, response.content

    content = json.loads(response.content)
    assert content == {
        'items': [
            {
                'id': 'comment_id',
                'author': 'system',
                'author_role': 'system',
                'timestamp': 'created_date',
                'text': 'order comment',
            },
        ],
    }
