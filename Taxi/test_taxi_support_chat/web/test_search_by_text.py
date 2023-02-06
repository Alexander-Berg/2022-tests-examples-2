# pylint: disable=broad-except

import http
import json

import pytest


@pytest.mark.parametrize(
    'data, chat_ids',
    [
        (
            {'text': 'text_1', 'offset': 1},
            [
                '539eb65be7e5b1f53980dfa8',
                '5a436ca8779fb3302cc784bf',
                '5b436ca8779fb3302cc784bf',
                '5b436ece779fb3302cc784bb',
                '5b436ece779fb3302cc784bd',
                '5b436ece779fb3302cc784bf',
            ],
        ),
        ({'text': 'text_1 +79991112233'}, ['5b436ece779fb3302cc784bf']),
        (
            {
                'text': 'text_1',
                'include_history': True,
                'date': {'newer_than': '2018-07-07'},
            },
            ['539eb65be7e5b1f53980dfa8', '5b436ca8779fb3302cc784ba'],
        ),
        (
            {'text': 'text_1', 'date': {'older_than': '2018-07-07'}},
            [
                '5a436ca8779fb3302cc784bf',
                '5b436ca8779fb3302cc784bf',
                '5b436ece779fb3302cc784bb',
                '5b436ece779fb3302cc784bd',
                '5b436ece779fb3302cc784bf',
            ],
        ),
        ({'text': 'text_1', 'limit': 1}, ['5b436ca8779fb3302cc784ba']),
        (
            {
                'text': 'text_1',
                'owners': {
                    'ids': ['5bbf8048779fb35d847fdb1e', '1960892827353512'],
                    'role': 'client',
                },
            },
            ['5a436ca8779fb3302cc784bf', '5b436ca8779fb3302cc784bf'],
        ),
        (
            {
                'text': 'text_1',
                'owners': {
                    'ids': ['5bbf8048779fb35d847fdb1e', '1960892827353512'],
                    'role': 'client',
                },
                'substring_search': True,
            },
            [
                '5a436ca8779fb3302cc784bf',
                '5b436ca8779fb3302cc7844f',
                '5b436ca8779fb3302cc784bf',
            ],
        ),
        (
            {
                'text': 'text_1',
                'offset': 1,
                'meta_fields': {'attachment_id_in_messages': 'attachment_id'},
            },
            ['539eb65be7e5b1f53980dfa8'],
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_CHAT_META_FIELDS_FOR_SEARCH_BY_PATH={
        'attachment_id_in_messages': 'messages.metadata.attachments.id',
    },
)
async def test_search_by_text(web_app_client, db, data, chat_ids):
    # TODO: remove index manipulation after TAXIDATA-285
    try:
        await db.user_chat_messages.drop_index('messages.message_text')
    except Exception:  # noqa
        pass
    await db.user_chat_messages.ensure_index(
        [('messages.message', 'text')],
        default_language='ru',
        background=True,
        partialFilterExpression={'text_indexed': True},
    )
    response = await web_app_client.post(
        '/v1/chat/search_by_text/', data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert sorted([chat['id'] for chat in result['chats']]) == chat_ids
    for chat in result['chats']:
        if 'include_history' in data:
            assert 'messages' in chat
        else:
            assert 'messages' not in chat
    try:
        await db.user_chat_messages.drop_index('messages.message_text')
    except Exception:  # noqa
        pass
