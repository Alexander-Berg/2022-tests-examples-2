import pytest

from taxi.clients import support_chat


@pytest.mark.parametrize(
    'data, expected_status, expected_search_request, expected_result',
    [
        (
            {'user_phone_id': 'user_phone_id', 'limit': 1},
            200,
            {
                'owner_id': 'user_phone_id',
                'owner_role': 'client',
                'chat_type': 'all',
                'include_history': True,
                'limit': 1,
                'offset': None,
            },
            {
                'status': 'ok',
                'data': [
                    {
                        'chat_id.json': (
                            '[{"text": "text", '
                            '"created": "2019-01-22T12:34:56"}]'
                        ),
                    },
                ],
            },
        ),
        (
            {'yandex_uid': 'yandex_uid', 'limit': 1},
            200,
            {
                'owner_id': 'yandex_uid',
                'owner_role': 'safety_center_client',
                'chat_type': 'all',
                'include_history': True,
                'offset': None,
                'limit': 1,
            },
            {
                'status': 'ok',
                'data': [
                    {
                        'chat_id.json': (
                            '[{"text": "text", '
                            '"created": "2019-01-22T12:34:56"}]'
                        ),
                    },
                ],
            },
        ),
        (
            {'driver_uuid': 'driver_uuid', 'offset': 1},
            200,
            {
                'owner_id': 'driver_uuid',
                'owner_role': 'driver',
                'chat_type': 'all',
                'include_history': True,
                'offset': 1,
                'limit': None,
            },
            {
                'status': 'ok',
                'data': [
                    {
                        'chat_id.json': (
                            '[{"text": "text", '
                            '"created": "2019-01-22T12:34:56"}]'
                        ),
                    },
                ],
            },
        ),
        (
            {'user_phone': 'user_phone'},
            200,
            {
                'owner_id': 'user_phone_id',
                'owner_role': 'client',
                'chat_type': 'all',
                'include_history': True,
                'offset': None,
                'limit': None,
            },
            {'status': 'no_data'},
        ),
        (
            {'driver_license': 'driver_license'},
            200,
            {
                'owner_id': 'user_phone_id',
                'owner_role': 'client',
                'chat_type': 'all',
                'include_history': True,
                'offset': None,
                'limit': None,
            },
            {'status': 'no_data'},
        ),
        (
            {'driver_license': 'driver_license', 'user_phone': 'user_phone'},
            400,
            {},
            {
                'error': 'Required set only 1 key in the body',
                'status': 'error',
            },
        ),
    ],
)
async def test_takeout(
        support_info_client,
        monkeypatch,
        data,
        expected_status,
        expected_search_request,
        expected_result,
):
    async def _dummy_zendesk_search(self, *args, **kwargs):
        if self.profile == 'yataxi':
            return {'results': [{'id': 'ticket_id'}]}
        return {'results': []}

    async def _dummy_get_comments(*args, **kwargs):
        return {
            'comments': [
                {
                    'body': 'public',
                    'created_at': '2019-01-22T12:34:56',
                    'public': True,
                },
                {
                    'body': 'hidden',
                    'created_at': '2019-01-22T12:34:56',
                    'public': False,
                },
            ],
        }

    async def _dummy_chat_search(*args, **kwargs):
        assert expected_search_request['owner_id'] == kwargs['owner_id']
        assert expected_search_request['owner_role'] == kwargs['owner_role']
        assert expected_search_request['chat_type'] == kwargs['chat_type']
        assert (
            expected_search_request['include_history']
            == kwargs['include_history']
        )
        assert expected_search_request['offset'] == kwargs.get('offset', None)
        assert expected_search_request['limit'] == kwargs.get(
            'date_limit', None,
        )
        return {
            'chats': [
                {
                    'id': 'chat_id',
                    'messages': [
                        {
                            'text': 'text',
                            'metadata': {'created': '2019-01-22T12:34:56'},
                        },
                    ],
                },
            ],
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'search', _dummy_chat_search,
    )

    response = await support_info_client.post(
        '/v1/takeout',
        json=data,
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'YaTaxi-Api-Key': 'api-key',
        },
    )
    assert response.status == expected_status
    assert await response.json() == expected_result
