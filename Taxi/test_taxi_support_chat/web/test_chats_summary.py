import http

import pytest

from taxi.clients import archive_api


@pytest.mark.now('2019-07-17 12:00:01')
@pytest.mark.config(
    USER_CHAT_MESSAGES_USE_ARCHIVE_API_SEARCH=False,
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
@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {'owner': {'id': 'owner_without_chat', 'role': 'client'}},
            {
                'archive': False,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_only_archive_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': True,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_only_visible_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': False,
                'open': False,
                'visible': True,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 1,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_only_open_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': False,
                'open': True,
                'visible': False,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 0,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_visible_and_open_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 3,
                'visible_chat_new_messages_count': 3,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_all_types_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': True,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 3,
                'visible_chat_new_messages_count': 3,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_with_all_types_chat_id',
                    'role': 'client',
                    'platform': 'yandex',
                },
            },
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 3,
                'visible_chat_new_messages_count': 3,
            },
        ),
        (
            {
                'owner': {
                    'id': 'driver_id',
                    'role': 'driver',
                    'platform': 'taximeter',
                },
            },
            {
                'archive': True,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 3,
                'visible_chat_new_messages_count': 3,
            },
        ),
        (
            {
                'owner': {
                    'id': 'driver_id',
                    'role': 'driver',
                    'platform': 'uberdriver',
                },
            },
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 5,
                'visible_chat_new_messages_count': 5,
            },
        ),
        (
            {'owner': {'id': 'driver_id', 'role': 'driver'}},
            {
                'archive': True,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 3,
                'visible_chat_new_messages_count': 3,
            },
        ),
        (
            {'owner': {'id': 'selfreg_id', 'role': 'selfreg_driver'}},
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 2,
            },
        ),
    ],
)
async def test_chats_summary(web_app_client, data, expected_result):
    response = await web_app_client.post('/v1/chat/summary', json=data)
    assert response.status == http.HTTPStatus.OK, response
    assert await response.json() == expected_result


@pytest.mark.now('2019-07-17 12:00:01')
@pytest.mark.config(
    USER_CHAT_MESSAGES_USE_ARCHIVE_API_SEARCH=True,
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
@pytest.mark.parametrize(
    'data, archive_result, expected_result',
    [
        (
            {'owner': {'id': 'owner_without_chat', 'role': 'client'}},
            1,
            {
                'archive': True,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        ),
        (
            {'owner': {'id': 'owner_without_chat', 'role': 'client'}},
            0,
            {
                'archive': False,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        ),
        (
            {
                'owner': {
                    'id': 'owner_without_chat',
                    'role': 'client',
                    'platform': 'yandex',
                },
            },
            0,
            {
                'archive': False,
                'open': False,
                'visible': False,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
        ),
    ],
)
async def test_chats_summary_archive_call(
        web_app_client,
        mock,
        monkeypatch,
        data,
        archive_result,
        expected_result,
):
    @mock
    async def select_rows(*args, **kwargs):
        kwargs.pop('log_extra')
        query_string = (
            'index.owner_id AS owner_id FROM %t AS index '
            'WHERE index.owner_id = %p AND '
            'index.type = %p AND '
            '{platform}'
            'index.open = %p AND '
            'index.visible = %p AND index.incident_timestamp > %p LIMIT 1'
        )
        query_params = [
            '//home/taxi/unstable/replica/mongo/indexes/user_chat_messages'
            '/owner_id_type_open_visible_incident_timestamp',
            'owner_without_chat',
            'client_support',
            False,
            False,
            1555588801.0,
        ]
        platform_str = ''
        if 'platform' in data['owner']:
            platform_str = 'index.platform in %p AND '
            query_params.insert(3, ['yango', 'yandex'])
        query_string = query_string.format(platform=platform_str)
        assert kwargs == {
            'query_string': query_string,
            'query_params': query_params,
            'replication_rules': [
                {
                    'max_delay': 43200,
                    'name': (
                        'user_chat_messages_owner_id_type_'
                        'open_visible_incident_timestamp_index'
                    ),
                },
            ],
            'return_bson': False,
        }
        return [item for item in range(archive_result)]

    monkeypatch.setattr(
        archive_api.ArchiveApiClient, 'select_rows', select_rows,
    )

    response = await web_app_client.post('/v1/chat/summary', json=data)
    assert response.status == http.HTTPStatus.OK, response
    assert await response.json() == expected_result


@pytest.mark.now('2019-07-17 12:00:01')
@pytest.mark.config(USER_CHAT_MESSAGES_USE_ARCHIVE_API_SEARCH=False)
@pytest.mark.parametrize(
    'data, expected_result',
    [
        (
            {
                'owner': {
                    'id': 'owner_with_two_visible_chat_id',
                    'role': 'client',
                },
            },
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 2,
            },
        ),
    ],
)
async def test_chats_summary_priority(web_app_client, data, expected_result):
    response = await web_app_client.post('/v1/chat/summary', json=data)
    assert response.status == http.HTTPStatus.OK, response
    assert await response.json() == expected_result
