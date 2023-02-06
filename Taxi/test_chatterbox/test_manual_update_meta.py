import datetime

import bson
import pytest

from test_chatterbox import plugins as conftest


NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.parametrize(
    ('task_id', 'data', 'meta_info', 'history', 'status'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'field': 'queue',
                'new_value': 'some_queue',
                'chatterbox_button': 'some_button',
            },
            {
                'city': 'Moscow',
                'queue': 'some_queue',
                'chatterbox_button': 'some_button',
            },
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'chatterbox_button',
                            'value': 'some_button',
                        },
                    ],
                },
            ],
            200,
        ),
        (
            '6b2cae5cb2682a976914c2a1',
            {
                'field': 'queue',
                'new_value': 'some_queue',
                'additional_tag': 'some_tag',
                'chatterbox_button': 'some_button',
            },
            {},
            [],
            404,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'field': 'order_id',
                'new_value': 'some_order_id',
                'additional_tag': 'some_tag',
            },
            {
                'antifraud_rules': ['taxi_free_trips'],
                'order_id': 'some_order_id',
                'queue': 'some_queue',
                'city': 'Moscow',
            },
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'some_order_id',
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'some_tag'},
                    ],
                },
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'antifraud_rules',
                            'value': ['taxi_free_trips'],
                        },
                    ],
                },
            ],
            200,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'field': 'queue',
                'new_value': 'another_queue',
                'additional_tag': 'some_tag',
                'chatterbox_button': 'some_button',
            },
            {
                'queue': 'another_queue',
                'city': 'Moscow',
                'chatterbox_button': 'some_button',
            },
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'queue',
                            'value': 'another_queue',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'chatterbox_button',
                            'value': 'some_button',
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'some_tag'},
                    ],
                },
            ],
            200,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_meta(
        mock,
        monkeypatch,
        cbox: conftest.CboxWrap,
        mock_antifraud_refund,
        mock_translate,
        patch_support_chat_get_history,
        task_id,
        data,
        meta_info,
        history,
        status,
):
    mock_translate('ru')
    patch_support_chat_get_history(
        response={
            'messages': [
                {
                    'id': '0',
                    'sender': {'id': 'login', 'role': 'client'},
                    'text': 'lala',
                    'metadata': {'created': '2021-01-01T20:00:00'},
                },
            ],
        },
    )

    await cbox.post('v1/tasks/%s/manual_update_meta' % task_id, params=data)
    assert cbox.status == status

    if cbox.status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        assert task['meta_info'] == meta_info
        assert task['history'] == history
