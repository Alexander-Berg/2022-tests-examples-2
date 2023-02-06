import http
import json
from typing import List

import bson
import pytest

from taxi.clients import archive_api

TRANSLATIONS = {
    'ivan': {'ru': 'Иван', 'en': 'Ivan'},
    'petr': {'ru': 'Петр', 'en': 'Petr'},
}


@pytest.mark.parametrize('include_history', [False, True])
@pytest.mark.parametrize(
    'data, chat_ids, expected_total',
    [
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'chat_ids': [
                    '5b436ece779fb3302cc784bf',
                    '5b436ece779fb3302cc784bb',
                ],
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'chat_ids': ['5b436ece779fb3302cc784bf'],
            },
            ['5b436ece779fb3302cc784bf'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'chat_ids': [
                    '5b436ece779fb3302cc784bf',
                    '5e2f207a779fb3831c8b4ad4',
                ],
            },
            ['5b436ece779fb3302cc784bf'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'exclude_request_id': 'message_61',
            },
            ['5b436ece779fb3302cc784bb'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc2615', 'role': 'client'},
                'type': 'archive',
                'owner_search_mode': 'right_like',
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5059779fb332fcc29999', 'role': 'client'},
                'type': 'visible',
            },
            ['539eb65be7e5b1f53980dfa9', '539eb65be7e5b1f53980dfa8'],
            2,
        ),
        (
            {
                'owner': {
                    'id': '5b4f5059779fb332fcc29999',
                    'role': 'client',
                    'platform': 'yandex',
                },
                'type': 'visible',
            },
            ['539eb65be7e5b1f53980dfa8'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'offset': 1,
            },
            ['5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'limit': 1,
            },
            ['5b436ece779fb3302cc784bf'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'limit': 1,
                'offset': 0,
            },
            ['5b436ece779fb3302cc784bf'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'limit': 1,
                'offset': 1,
            },
            ['5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'limit': 1,
                'offset': 2,
            },
            [],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'date': {'newer_than': '2019-01-01'},
            },
            [],
            0,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'date': {'older_than': '2018-01-01'},
            },
            [],
            0,
        ),
        (
            {
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
                'type': 'open',
            },
            ['5b436ca8779fb3302cc784ba'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26155', 'role': 'client'},
                'type': 'visible',
            },
            ['5b436ece779fb3302cc784bd'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26155', 'role': 'client'},
                'type': 'archive',
            },
            [],
            0,
        ),
        (
            {
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
                'type': 'visible',
                'meta_fields': {'attachment_id_in_messages': 'attachment_id'},
            },
            ['5b436ca8779fb3302cc784ba'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26154', 'role': 'driver'},
                'type': 'visible',
                'meta_fields': {'car_number': 'AM777R999'},
            },
            ['5df208a0779fb3085850a6d0', 'solved_driver_chat_id'],
            2,
        ),
        (
            {
                'owner': {
                    'id': '5b4f5092779fb332fcc26154',
                    'role': 'driver',
                    'platform': 'taximeter',
                },
                'type': 'visible',
                'meta_fields': {'car_number': 'AM777R999'},
            },
            ['solved_driver_chat_id'],
            1,
        ),
        (
            {
                'owner': {
                    'id': '5b4f5092779fb332fcc26154',
                    'role': 'driver',
                    'platform': 'uberdriver',
                },
                'type': 'visible',
                'meta_fields': {'car_number': 'AM777R999'},
            },
            ['5df208a0779fb3085850a6d0'],
            1,
        ),
        (
            {
                'owner': {
                    'id': '5b4f5092779fb332fcc26154',
                    'role': 'driver',
                    'platform': 'taximeter',
                },
                'type': 'archive',
                'meta_fields': {'car_number': 'AM777R999'},
            },
            ['closed_driver_chat_id'],
            1,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26154', 'role': 'driver'},
                'type': 'archive',
                'meta_fields': {'car_number': 'AM777R999'},
            },
            ['closed_driver_chat_id'],
            1,
        ),
        (
            {
                'owners': {
                    'ids': [
                        '5b4f5092779fb332fcc26153',
                        '5b4f5092779fb332fcc2615',
                    ],
                    'role': 'client',
                },
                'type': 'archive',
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owners': {
                    'ids': ['5b4f5059779fb332fcc26', '5b4f5092779fb332fcc261'],
                    'role': 'client',
                },
                'type': 'archive',
                'owner_search_mode': 'right_like',
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'order_by': 'incident_timestamp',
                'limit': 2,
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'order_by': 'updated',
                'limit': 2,
            },
            ['5b436ece779fb3302cc784bb', '5b436ece779fb3302cc784bf'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'order_by': 'updated',
                'order_direction': 'desc',
                'limit': 2,
            },
            ['5b436ece779fb3302cc784bb', '5b436ece779fb3302cc784bf'],
            2,
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'order_by': 'updated',
                'order_direction': 'asc',
                'limit': 2,
            },
            ['5b436ece779fb3302cc784bf', '5b436ece779fb3302cc784bb'],
            2,
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_CHAT_OWNER_LIKE_SEARCH_MIN_LEN={'client_support': 20},
    SUPPORT_CHAT_META_FIELDS_FOR_SEARCH_BY_PATH={
        'attachment_id_in_messages': 'messages.metadata.attachments.id',
        'car_number': 'car_number',
    },
    SUPPORT_CHAT_PLATFORM_MAPPING={
        'yandex': 'yandex',
        'android': 'yandex',
        'iphone': 'yandex',
        'uber': 'uber',
        'uber_android': 'uber',
        'uber_iphone': 'uber',
        'yango_android': 'yandex',
        'yango_iphone': 'yandex',
        'taximeter': 'taximeter',
        'uberdriver': 'uberdriver',
    },
)
@pytest.mark.filldb(user_chat_messages='search')
async def test_search(
        web_app_client, data, chat_ids, expected_total, include_history,
):
    if include_history:
        data['include_history'] = True
    response = await web_app_client.post(
        '/v1/chat/search/',
        data=json.dumps(data),
        headers={'X-Ya-Service-Ticket': 'backend_service_ticket'},
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert [chat['id'] for chat in result['chats']] == chat_ids
    assert result['total'] == expected_total
    if data.get('limit'):
        assert result['limit'] == data['limit']
    if data.get('offset'):
        assert result['offset'] == data['offset']
    for chat in result['chats']:
        assert chat['metadata']
        if include_history:
            assert chat['messages']


@pytest.mark.parametrize(
    ('data', 'expected_text'),
    [
        (
            {
                'owner': {'id': '5b4f5092779fb', 'role': 'client'},
                'type': 'archive',
                'owner_search_mode': 'right_like',
            },
            'Owner like search len should be more than 24',
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb', 'role': 'client'},
                'type': 'archive',
                'owner_search_mode': 'right_like',
            },
            'Owner like search len should be more than 24',
        ),
        (
            {
                'owners': {'ids': ['5b4f5092779fb'], 'role': 'driver'},
                'type': 'archive',
                'owner_search_mode': 'right_like',
            },
            'Owner like search not permitted for chat_type: driver_support',
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'order_by': 'bad_field',
            },
            '400: Bad Request',
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'all',
                'chat_ids': ['not object id'],
            },
            'Invalid object id',
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'all',
                'chat_ids': [
                    '5e2f2076779fb3831c8b4ad3',
                    '5e2f207a779fb3831c8b4ad4',
                ],
            },
            'Too much ids for search',
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_CHAT_OWNER_LIKE_SEARCH_MIN_LEN={'client_support': 24},
    SUPPORT_CHAT_SEARCH_IDS_MAX_COUNT=1,
    TVM_ENABLED=True,
)
async def test_search_bad_request(
        web_app_client, mock_tvm_keys, data, expected_text,
):
    response = await web_app_client.post(
        '/v1/chat/search/',
        json=data,
        headers={'X-Ya-Service-Ticket': 'backend_service_ticket'},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST
    text = await response.text()
    assert text == expected_text


@pytest.mark.config(
    USER_CHAT_MESSAGES_USE_ARCHIVE_API_SEARCH=True,
    SUPPORT_CHAT_OWNER_LIKE_SEARCH_MIN_LEN={'client_support': 24},
)
async def test_search_in_archive(web_app_client, db, monkeypatch, mock):
    @mock
    async def select_rows(*args, **kwargs):
        kwargs.pop('log_extra')
        assert kwargs == {
            'query_string': (
                'index.incident_timestamp, chat.doc AS doc '
                'FROM %t AS index JOIN %t AS chat '
                'on index.id=chat.id WHERE index.owner_id IN %p '
                'AND index.type = %p AND index.platform in %p AND '
                'index.open = %p AND index.visible = %p AND '
                'index.incident_timestamp > %p AND '
                'NOT (index.id IN %p) '
                'ORDER BY index.incident_timestamp DESC LIMIT %p'
            ),
            'query_params': [
                '//home/taxi/unstable/replica/mongo/indexes/user_chat_messages'
                '/owner_id_type_open_visible_incident_timestamp',
                '//home/taxi/unstable/private/mongo/bson/'
                'user_chat_messages',
                ['5b4f5092779fb332fcc26153'],
                'client_support',
                ['yango', 'yandex'],
                False,
                False,
                1514754000.0,
                ['5b436ece779fb3302cc784bf'],
                2,
            ],
            'replication_rules': [
                {'max_delay': 43200, 'name': 'user_chat_messages_bson'},
                {
                    'max_delay': 43200,
                    'name': (
                        'user_chat_messages_owner_id_type_'
                        'open_visible_incident_timestamp_index'
                    ),
                },
            ],
            'return_bson': True,
        }
        doc = await db.user_chat_messages.find_one(
            {'_id': bson.ObjectId('5b436ca8779fb3302cc784ba')},
        )
        return [{'doc': doc}]

    monkeypatch.setattr(
        archive_api.ArchiveApiClient, 'select_rows', select_rows,
    )

    response = await web_app_client.post(
        '/v1/chat/search/',
        data=json.dumps(
            {
                'owner': {
                    'id': '5b4f5092779fb332fcc26153',
                    'role': 'client',
                    'platform': 'yandex',
                },
                'type': 'all',
                'date': {'newer_than': '2018-01-01', 'limit': 3},
            },
        ),
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    assert sorted([chat['id'] for chat in result['chats']]) == [
        '5b436ca8779fb3302cc784ba',
        '5b436ece779fb3302cc784bf',
    ]
    assert len(select_rows.calls) == 1


@pytest.mark.parametrize(
    'data, lang_map',
    [
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
                'type': 'archive',
                'date': {'newer_than': '2018-01-01', 'limit': 1},
            },
            {None: 'Иван', 'ru': 'Иван', 'en': 'Ivan'},
        ),
        (
            {
                'owner': {'id': '5b4f5092779fb332fcc26155', 'role': 'client'},
                'type': 'visible',
            },
            {None: 'Петр', 'ru': 'Петр', 'en': 'Petr'},
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.filldb(user_chat_messages='translation')
async def test_search_translations(web_app_client, data, lang_map):

    for lang, support_name in lang_map.items():
        headers = {}
        if lang:
            headers['Accept-Language'] = lang
        response = await web_app_client.post(
            '/v1/chat/search/', data=json.dumps(data), headers=headers,
        )
        assert response.status == http.HTTPStatus.OK
        result = await response.json()

        chat = result['chats'][0]

        assert chat['participants'][0]['nickname'] == support_name


@pytest.mark.config(SUPPORT_CHAT_MULTI_OWNER_SEARCH_LIMIT=2)
@pytest.mark.parametrize(
    ('owners', 'expected_status', 'expected_result'),
    (
        (
            [
                '5b4f5092779fb332fcc26173',
                '5b4f5092579fb332fcc2615',
                '5b4f5092579fb332fcc2616',
            ],
            400,
            {
                'code': 'validation_error',
                'message': 'Owners search limit set to 2 but 3 in query',
                'status': 'error',
            },
        ),
    ),
)
async def test_search_multi_owner_limit(
        web_app_client,
        owners: List[str],
        expected_status: int,
        expected_result: dict,
):

    response = await web_app_client.post(
        '/v1/chat/search/',
        json={'owners': {'ids': owners, 'role': 'client'}, 'type': 'archive'},
    )
    assert response.status == expected_status
    assert await response.json() == expected_result
