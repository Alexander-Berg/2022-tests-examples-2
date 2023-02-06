# pylint: disable=redefined-outer-name
import datetime
import io

import aiohttp
import pytest

from taxi.clients import support_chat

NOW = datetime.datetime(2018, 6, 15, 12, 34)
UUID = '00000000000040008000000000000000'


@pytest.fixture
def mock_api_requests(cbox, monkeypatch, patch_aiohttp_session, response_mock):
    async def create_chat(*args, **kwargs):
        return {'id': 'chat_id'}

    async def get_history(*args, **kwargs):
        return {
            'messages': [
                {
                    'sender': {'role': 'client', 'id': 'some_client_id'},
                    'text': 'some message',
                    'metadata': {'created': NOW.isoformat()},
                    'id': 'some id',
                },
            ],
            'total': 1,
        }

    async def detect_language(*args, **kwargs):
        return {'code': '200', 'lang': 'ru'}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'create_chat', create_chat,
    )
    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', get_history,
    )
    monkeypatch.setattr(
        cbox.app.predispatcher.translate_client,
        'detect_language',
        detect_language,
    )


@pytest.mark.config(CHATTERBOX_PREDISPATCH=True)
@pytest.mark.now(NOW.isoformat())
async def test_import_chats(
        cbox,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_api_requests,
        mock_uuid_uuid4,
):
    body = (
        'message;user_id;user_phone_id;order_id;order_alias_id;user_phone'
        ';driver_id;'
        'park_db_id;tag1,tag2'
    )

    form_data = aiohttp.FormData()
    form_data.add_field(
        'csv_file',
        io.BytesIO(body.encode('utf8')),
        filename='test.csv',
        content_type='text/csv',
    )

    await cbox.post(
        '/test/import',
        raw_data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert cbox.status == 200

    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    assert cbox.status == 200
    task = cbox.body_data
    assert task['external_id'] == 'chat_id'
    task['meta_info'].pop('ml_request_id')
    assert task['meta_info'] == {
        'user_id': 'user_id',
        'user_phone_id': 'user_phone_id',
        'order_id': 'order_id',
        'order_alias_id': 'order_alias_id',
        'user_phone': 'user_phone',
        'driver_id': 'driver_id',
        'park_db_id': 'park_db_id',
        'task_language': 'ru',
        'status_before_assign': 'new',
        'antifraud_rules': ['taxi_free_trips'],
        'recently_used_macro_ids': ['1', '2'],
    }
    assert task['tags'] == ['tag1', 'tag2', 'lang_ru']
    assert task['chat_messages'] == {
        'messages': [
            {
                'sender': {'role': 'client', 'id': 'some_client_id'},
                'text': 'some message',
                'metadata': {'created': NOW.isoformat()},
                'id': 'some id',
            },
        ],
        'total': 1,
    }
    task['history'].pop()
    assert task['history'] == [
        {
            'action': 'create',
            'created': '2018-06-15T12:34:00+0000',
            'line': 'first',
            'login': 'superuser',
        },
        {
            'action': 'update_meta',
            'created': '2018-06-15T12:34:00+0000',
            'login': 'superuser',
            'line': 'first',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'user_id',
                    'value': 'user_id',
                },
                {
                    'change_type': 'set',
                    'field_name': 'order_id',
                    'value': 'order_id',
                },
                {
                    'change_type': 'set',
                    'field_name': 'order_alias_id',
                    'value': 'order_alias_id',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone_id',
                    'value': 'user_phone_id',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': 'user_phone',
                },
                {
                    'change_type': 'set',
                    'field_name': 'driver_id',
                    'value': 'driver_id',
                },
                {
                    'change_type': 'set',
                    'field_name': 'park_db_id',
                    'value': 'park_db_id',
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': 'tag1'},
                {'change_type': 'add', 'tag': 'tag2'},
            ],
        },
        {
            'action': 'update_meta',
            'created': '2018-06-15T12:34:00+0000',
            'line': 'first',
            'login': 'superuser',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'recently_used_macro_ids',
                    'value': ['1', '2'],
                },
            ],
        },
        {
            'action': 'predispatch',
            'created': '2018-06-15T12:34:00+0000',
            'line': 'first',
            'login': 'superuser',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'task_language',
                    'value': 'ru',
                },
                {
                    'change_type': 'set',
                    'field_name': 'ml_request_id',
                    'value': UUID,
                },
            ],
            'tags_changes': [{'change_type': 'add', 'tag': 'lang_ru'}],
        },
        {
            'action': 'update_meta',
            'created': '2018-06-15T12:34:00+0000',
            'line': 'first',
            'login': 'superuser',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'antifraud_rules',
                    'value': ['taxi_free_trips'],
                },
            ],
        },
        {
            'action': 'ensure_predispatched',
            'created': '2018-06-15T12:34:00+0000',
            'line': 'first',
            'login': 'superuser',
        },
    ]


@pytest.mark.config(CHATTERBOX_PREDISPATCH=True)
async def test_import_rand_chats(
        cbox,
        mock_api_requests,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
):
    body = (
        'message;user_id;rand;order_id;order_alias_id;user_phone'
        ';driver_id;park_db_id'
    )

    form_data = aiohttp.FormData()
    form_data.add_field(
        'csv_file',
        io.BytesIO(body.encode('utf8')),
        filename='test.csv',
        content_type='text/csv',
    )

    await cbox.post(
        '/test/import',
        raw_data=form_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    assert cbox.status == 200

    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    assert cbox.status == 200
    task = cbox.body_data
    assert task['external_id'] == 'chat_id'
    assert len(task['meta_info']['user_phone_id']) == 24
    assert task['tags'] == ['lang_ru']
    assert task['chat_messages'] == {
        'messages': [
            {
                'sender': {'role': 'client', 'id': 'some_client_id'},
                'text': 'some message',
                'metadata': {'created': NOW.isoformat()},
                'id': 'some id',
            },
        ],
        'total': 1,
    }
