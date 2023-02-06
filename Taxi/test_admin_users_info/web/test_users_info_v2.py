import pytest

from test_admin_users_info import utils

PERMISSION_VIEW_DELETED_USERS = ['view_deleted_users']
PERMISSION_VIEW_USER_INFO = ['view_user_info']
PERMISSION_SEARCH_BY_USER_PHONE = ['search_by_user_phone']
ALL_PERMISSIONS = (
    PERMISSION_SEARCH_BY_USER_PHONE
    + PERMISSION_VIEW_USER_INFO
    + PERMISSION_VIEW_DELETED_USERS
)


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, code, mock_data, execute',
    [
        pytest.param({}, 200, {}, [], id='no filters, no data'),
        pytest.param(
            {'user_id': 'test1'}, 200, {}, [], id='one filter, no data',
        ),
        pytest.param(
            {'user_id': '00000001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000001': {
                        'yandex_uid': 'yandex_uid_00000001',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
            ],
            id='user_id filter, one entry',
        ),
        pytest.param(
            {'yandex_uuid': 'yandex_uuid_00000000000000000002'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000002',
                        'phone_id': 'phone_id_00000002',
                        'yandex_uid': 'yandex_uid_00000002',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000002': {
                        'yandex_uid': 'yandex_uid_00000002',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'personal_phone_id': 'personal_phone_id_00000002',
                'personal_email_id': 'personal_email_id_00000002',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000002',
                    'personal_phone_id': 'personal_phone_id_00000002',
                    'personal_email_id': 'personal_email_id_00000002',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
            ],
            id='yandex_uuid filter, one entry',
        ),
        pytest.param(
            {'phone': '+79505508003'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'created': '2020-10-18T20:01:47.975+0000',
                    },
                    {
                        'id': '00000004',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000004',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000004': {
                        'yandex_uid': 'yandex_uid_00000004',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                    'yandex_uid_00000003': {
                        'yandex_uid': 'yandex_uid_00000003',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'phone_ids': ['phone_id_00000003'],
                'personal_email_id': 'personal_email_id_00000003',
                'personal_phone_id': 'personal_phone_id_00000003',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000004',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
                {
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'last_authorized': '2020-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
            ],
            id='phone filter, multiple entries',
        ),
        pytest.param(
            {'yandex_uid': 'yandex_uid_00000003'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000003': {
                        'yandex_uid': 'yandex_uid_00000003',
                        'type': 'phonish',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'personal_phone_id': 'personal_phone_id_00000003',
                'personal_email_id': 'personal_email_id_00000003',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'phonish',
                    'portal_type': 'portal',
                },
            ],
            id='yandex_uid filter, one entry',
        ),
        pytest.param(
            {'phone': '+79505508001'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000001': {
                        'yandex_uid': 'yandex_uid_00000001',
                        'type': 'phonish',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'is_phone_deleted': False,
                    'uid_type': 'phonish',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                },
            ],
            id='phone filter, zalogin types check',
        ),
        pytest.param(
            {
                'yandex_uid': 'yandex_uid_00000001',
                'yandex_uuid': 'yandex_uuid_00000000000000000001',
            },
            200,
            {},
            [],
            id='uid and uuid filters, no data collected',
        ),
        pytest.param(
            {'user_id': '123456789'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000003',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000003',
                        'created': '2021-10-18T20:01:47.975+0000',
                    },
                    {
                        'id': '00000004',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000004',
                        'created': '2024-10-18T20:01:47.975+0000',
                    },
                    {
                        'id': '00000004',
                        'phone_id': 'phone_id_00000003',
                        'yandex_uid': 'yandex_uid_00000004',
                        'created': '2021-10-18T20:01:47.975+0000',
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
                'zalogin': {
                    'yandex_uid_00000003': {
                        'yandex_uid': 'yandex_uid_00000003',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                    'yandex_uid_00000004': {
                        'yandex_uid': 'yandex_uid_00000003',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'personal_phone_id': 'personal_phone_id_00000003',
                'personal_email_id': 'personal_email_id_00000003',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000003',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
                {
                    'yandex_uid': 'yandex_uid_00000004',
                    'personal_phone_id': 'personal_phone_id_00000003',
                    'personal_email_id': 'personal_email_id_00000003',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': False,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
            ],
            id='user_id filter, duplicates and sort check',
        ),
        pytest.param(
            {'user_id': '00000012'},
            200,
            {
                'users_search': [
                    {
                        'id': '00000012',
                        'phone_id': 'phone_id_00000012',
                        'yandex_uid': 'yandex_uid_00000012',
                        'created': '2021-10-18T20:01:47.975+0000',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000012',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': '',
                        },
                    ],
                },
                'zalogin': {
                    'yandex_uid_00000012': {
                        'yandex_uid': 'yandex_uid_00000012',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'type': 'deleted',
                'personal_phone_id': 'personal_phone_id_00000012',
                'personal_email_id': 'personal_email_id_00000012',
            },
            [],
            id='show deleted, filtration check - hide',
        ),
        pytest.param(
            {'user_id': '00000001', 'show_deleted': True},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'created': '2021-10-18T20:01:47.975+0000',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'deleted',
                        },
                    ],
                },
                'zalogin': {
                    'yandex_uid_00000001': {
                        'yandex_uid': 'yandex_uid_00000001',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'type': 'deleted',
                'personal_phone_id': 'personal_phone_id_00000001',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [
                {
                    'yandex_uid': 'yandex_uid_00000001',
                    'personal_phone_id': 'personal_phone_id_00000001',
                    'personal_email_id': 'personal_email_id_00000001',
                    'last_authorized': '2021-10-18T20:01:47.975+0000',
                    'is_phone_deleted': True,
                    'uid_type': 'portal',
                    'portal_type': 'portal',
                },
            ],
            id='show deleted, filtration check - show',
        ),
        pytest.param(
            {'phone': '+79999999999', 'show_deleted': True},
            200,
            {
                'users_search': [
                    {
                        'id': '00000001',
                        'phone_id': 'phone_id_00000001',
                        'yandex_uid': 'yandex_uid_00000001',
                        'created': '2021-10-18T20:01:47.975+0000',
                    },
                ],
                'user_phones': {
                    'items': [
                        {
                            'id': 'phone_id_00000001',
                            'phone': '+7-XXX-XXX-XXXX',
                            'type': 'deleted',
                        },
                    ],
                },
                'zalogin': {
                    'yandex_uid_00000001': {
                        'yandex_uid': 'yandex_uid_00000001',
                        'type': 'portal',
                        'portal_type': 'portal',
                        'bound_phone_ids': [],
                        'allow_reset_password': True,
                        'has_2fa_on': True,
                        'sms_2fa_status': True,
                    },
                },
                'type': 'deleted',
                'personal_email_id': 'personal_email_id_00000001',
            },
            [],
            id='phone not found, exception check',
        ),
    ],
)
async def test_get_user_info_v2(
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
    async def _get_all_countries(*args, **kwargs):
        data = load_json('territories.json')
        return data['countries']

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=W0612
    def _get_users(request):
        return mock_data.get('user_phones', [])

    @mockserver.json_handler('/user_api-api/users/search')
    # pylint: disable=W0612
    def _users_search(request):
        return {'items': mock_data.get('users_search', [])}

    @mockserver.json_handler('/user_api-api/user_emails/get')
    # pylint: disable=W0612
    def _get_user_emails(request):
        items = []
        items.append({'personal_email_id': mock_data.get('personal_email_id')})
        return {'items': items}

    @mockserver.json_handler('/zalogin/admin/uid-info')
    def _get_uid_info(request):
        uid = request.query['yandex_uid']
        return mock_data.get('zalogin', {}).get(uid)

    @mockserver.json_handler('/user_api-api/user_phones/get')
    # pylint: disable=W0612
    def _get_user_phone(request):
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
        return {'id': mock_data.get('personal_phone_id')}

    with utils.has_permissions(ALL_PERMISSIONS):
        response = await utils.make_post_request(
            web_app_client, '/v2/users_info', data=query,
        )
    assert response.status == code
    content = await response.json()
    assert content == execute

    with utils.has_permissions(ALL_PERMISSIONS):
        response = await utils.make_post_request(
            web_app_client, '/v2/users_info', data=query,
        )

    assert response.status == code
    content = await response.json()
    assert content == execute


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    ['permissions', 'data', 'code', 'message'],
    [
        pytest.param(
            [],
            {},
            403,
            'forbidden error Forbidden. Permission: view_user_info',
            id='no view_user_info permission',
        ),
        pytest.param(
            PERMISSION_VIEW_USER_INFO,
            {'show_deleted': True},
            403,
            'forbidden error Forbidden. Permission: view_deleted_users',
            id='view_deleted_users',
        ),
        pytest.param(
            PERMISSION_VIEW_USER_INFO,
            {'phone': '+00000000000'},
            403,
            'forbidden error Forbidden. Permission: search_by_user_phone',
            id='search_by_user_phone',
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_get_user_info_permissions(
        web_app_client, permissions, data, code, message,
):
    with utils.has_permissions(permissions):
        response = await utils.make_post_request(
            web_app_client, '/v2/users_info', data=data,
        )
        content = await response.json()
        assert response.status == code
        assert content['message'] == message
