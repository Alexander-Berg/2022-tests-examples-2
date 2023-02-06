from aiohttp import web
import pytest

from test_admin_users_info import utils

CAN_VIEW_ALL_FIELDS = ['view_deleted_users', 'delete_user']
CAN_VIEW_DELETED_USERS = ['view_deleted_users']


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, code, mock_data, execute',
    [
        ({}, 200, {}, []),
        ({'user_id': 'test1'}, 200, {}, []),
        (
            {'user_id': '00000001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'uber_id': '',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'user_id': '00000001',
                    'uber_id': '',
                    'yandex_uuid': 'yandex_uuid_00000000000000000001',
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'yandex_uuid': 'yandex_uuid_00000000000000000002'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000002',
                        'phone_id': 'phone_id_00000002',
                        'yandex_uuid': 'yandex_uuid_00000000000000000002',
                        'yandex_uid': 'yandex_uid_00000002',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000002',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'uber',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000002',
                'personal_email_id': 'personal_email_id_00000002',
            },
            [
                {
                    'user_id': '00000002',
                    'yandex_uuid': 'yandex_uuid_00000000000000000002',
                    'yandex_uid': 'yandex_uid_00000002',
                    'personal_phone_id': 'personal_phone_id_00000002',
                    'personal_email_id': 'personal_email_id_00000002',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'phone': '+79505508003'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uuid': 'yandex_uuid_00000000000000000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'uber_id': '123456789',
                    },
                    {
                        'id': '00000004',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uuid': 'yandex_uuid_00000000000000000003',
                        'yandex_uid': 'yandex_uid_00000004',
                        'uber_id': '123456789',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000003',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'partner',
                        },
                    ],
                },
                'phone_ids': ['phone_id_00000003'],
                'personal_email_id': 'personal_email_id_00000003',
                'personal_phone_id': 'personal_phone_id_00000003',
            },
            [
                {
                    'user_id': '00000003',
                    'uber_id': '123456789',
                    'yandex_uuid': 'yandex_uuid_00000000000000000003',
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'phone_can_be_deleted': True,
                },
                {
                    'user_id': '00000004',
                    'uber_id': '123456789',
                    'yandex_uuid': 'yandex_uuid_00000000000000000003',
                    'yandex_uid': 'yandex_uid_00000004',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'yandex_uid': 'yandex_uid_00000003'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uuid': 'yandex_uuid_00000000000000000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'uber_id': '123456789',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000003',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000003',
                'personal_email_id': 'personal_email_id_00000003',
            },
            [
                {
                    'user_id': '00000003',
                    'uber_id': '123456789',
                    'yandex_uuid': 'yandex_uuid_00000000000000000003',
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'phone': '+79505508001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'uber_id': '',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'user_id': '00000001',
                    'uber_id': '',
                    'yandex_uuid': 'yandex_uuid_00000000000000000001',
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'phone_id': 'phone_id_00000001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'uber_id': '',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'user_id': '00000001',
                    'uber_id': '',
                    'yandex_uuid': 'yandex_uuid_00000000000000000001',
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {
                'yandex_uid': 'yandex_uid_00000001',
                'yandex_uuid': 'yandex_uuid_00000000000000000002',
            },
            200,
            {},
            [],
        ),
        (
            {'uber_id': '123456789'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uuid': 'yandex_uuid_00000000000000000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'uber_id': '123456789',
                    },
                    {
                        'id': '00000004',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uuid': 'yandex_uuid_00000000000000000003',
                        'yandex_uid': 'yandex_uid_00000004',
                        'uber_id': '123456789',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000003',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000003',
                'personal_email_id': 'personal_email_id_00000003',
            },
            [
                {
                    'user_id': '00000003',
                    'uber_id': '123456789',
                    'yandex_uuid': 'yandex_uuid_00000000000000000003',
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'phone_can_be_deleted': True,
                },
                {
                    'user_id': '00000004',
                    'uber_id': '123456789',
                    'yandex_uuid': 'yandex_uuid_00000000000000000003',
                    'yandex_uid': 'yandex_uid_00000004',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'phone_can_be_deleted': True,
                },
            ],
        ),
        (
            {'user_id': '00000001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'uber_id': '',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': '',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
                'type': '',
            },
            [],
        ),
        (
            {'user_id': '00000001', 'show_deleted': True},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': '',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
                'type': '',
            },
            [
                {
                    'user_id': '00000001',
                    'yandex_uuid': 'yandex_uuid_00000000000000000001',
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'is_phone_deleted': True,
                },
            ],
        ),
    ],
)
async def test_get_user_info(
        web_app_client,
        patch,
        load_json,
        mockserver,
        query,
        code,
        mock_data,
        execute,
):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    # pylint: disable=W0612
    async def get_all_countries(*args, **kwargs):
        data = load_json('territories.json')
        return data['countries']

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=W0612
    def get_users(request):
        return mock_data.get('user_phones', [])

    @mockserver.json_handler('/user_api-api/users/search')
    # pylint: disable=W0612
    def users_search(request):
        return {'items': mock_data.get('users_search', [])}

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=W0612
    def get_user_emails(request):
        items = []
        items.append({'personal_email_id': mock_data.get('personal_email_id')})
        return {'items': items}

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=W0612
    def get_user_phone(request):
        response = {
            'id': '00000d26b5f273e600000001',
            'stat': 'stat',
            'is_loyal': 'is_loyal',
            'is_yandex_staff': 'is_yandex_staff',
            'is_taxi_staff': 'is_taxi_staff',
            'phone': 'phone',
            'type': mock_data.get('type', 'yandex'),
            'spam_stat': 'spam_stat',
            'blocked_times': 'blocked_times',
            'personal_phone_id': mock_data.get('personal_phone_id', ''),
        }
        return response

    @patch('taxi.clients.personal.PersonalApiClient.find')
    # pylint: disable=W0612
    async def find(*args, **kwargs):
        return {'id': mock_data.get('personal_phone_id', '')}

    with utils.has_permissions(CAN_VIEW_ALL_FIELDS):
        response = await utils.make_post_request(
            web_app_client, '/v1/users_info', data=query,
        )
    assert response.status == code
    content = await response.json()
    assert content == execute


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, code, mock_data, execute',
    [
        ({}, 200, {}, []),
        (
            {'phone': '+79505508001'},
            400,
            {},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'Unexpected fields: [\'phone\']'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {'phone_id': 'phone_id_00000001'},
            400,
            {},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'Unexpected fields: [\'phone_id\']'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {'user_id': '00000001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uuid': 'yandex_uuid_00000000000000000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'uber_id': '',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'user_id': '00000001',
                    'uber_id': '',
                    'yandex_uuid': 'yandex_uuid_00000000000000000001',
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                },
            ],
        ),
        (
            {'yandex_uuid': 'yandex_uuid_00000000000000000002'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000002',
                        'phone_id': 'phone_id_00000002',
                        'yandex_uuid': 'yandex_uuid_00000000000000000002',
                        'yandex_uid': 'yandex_uid_00000002',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000002',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000002',
                'personal_email_id': 'personal_email_id_00000002',
            },
            [
                {
                    'user_id': '00000002',
                    'yandex_uuid': 'yandex_uuid_00000000000000000002',
                    'yandex_uid': 'yandex_uid_00000002',
                    'personal_phone_id': 'personal_phone_id_00000002',
                    'personal_email_id': 'personal_email_id_00000002',
                },
            ],
        ),
        (
            {'yandex_uuid': 'yandex_uuid_00000000000000000002'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000002',
                        'phone_id': 'phone_id_00000002',
                        'yandex_uuid': 'yandex_uuid_00000000000000000002',
                        'yandex_uid': 'yandex_uid_00000002',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000002',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'yandex',
                        },
                    ],
                },
                'personal_phone_id': 'personal_phone_id_00000002',
            },
            [
                {
                    'user_id': '00000002',
                    'yandex_uuid': 'yandex_uuid_00000000000000000002',
                    'yandex_uid': 'yandex_uid_00000002',
                    'personal_phone_id': 'personal_phone_id_00000002',
                },
            ],
        ),
    ],
)
async def test_general_get_user_info(
        web_app_client,
        patch,
        mockserver,
        load_json,
        query,
        code,
        mock_data,
        execute,
):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    # pylint: disable=W0612
    async def get_all_countries(*args, **kwargs):
        data = load_json('territories.json')
        return data['countries']

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=W0612
    def get_users(request):
        return mock_data.get('user_phones', [])

    @mockserver.json_handler('/user_api-api/users/search')
    # pylint: disable=W0612
    def users_search(request):
        return {'items': mock_data.get('users_search', [])}

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=W0612
    def get_user_emails(request):
        items = []
        if not mock_data.get('personal_email_id'):
            return web.json_response({}, status=404)
        items.append({'personal_email_id': mock_data.get('personal_email_id')})
        return {'items': items}

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=W0612
    def get_user_phones(request):
        response = {
            'stat': 'stat',
            'is_loyal': 'is_loyal',
            'is_yandex_staff': 'is_yandex_staff',
            'is_taxi_staff': 'is_taxi_staff',
            'id': '00000d26b5f273e600000001',
            'phone': 'phone',
            'type': 'yandex',
            'spam_stat': 'spam_stat',
            'blocked_times': 'blocked_times',
            'personal_phone_id': mock_data.get('personal_phone_id', ''),
        }
        return response

    with utils.has_permissions(CAN_VIEW_DELETED_USERS):
        response = await utils.make_post_request(
            web_app_client, '/v1/general/users_info', data=query,
        )

    assert response.status == code
    content = await response.json()
    assert content == execute
