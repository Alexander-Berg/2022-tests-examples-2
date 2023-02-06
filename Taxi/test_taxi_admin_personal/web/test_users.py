import pytest

from test_taxi_admin_personal import utils


PHONE_IDS = ['a1', 'a2', 'a3', 'a4']
USERS_PD = {
    '1': {
        'phone': '+79111111111',
        'email': 'email04@test.com',
        'email_status': 'confirmed',
        'phone_id': '54f031119cc7a09257112b01',
        'yandex_uid': 'yandex_uid_1',
        'personal_email_id': 'personal_email_id_1',
        'personal_phone_id': 'personal_phone_id_1',
        'yandex_uid_type': 'portal',
        'application': 'yataxi_test',
    },
    '2': {
        'phone': '+79023000000',
        'email': 'email03@test.com',
        'email_status': 'unconfirmed',
        'phone_id': '54f031119cc7a09257112b02',
        'yandex_uid': 'yandex_uid_2',
        'personal_email_id': 'personal_email_id_2',
        'personal_phone_id': 'personal_phone_id_2',
        'yandex_uid_type': 'phonish',
    },
    '3': {
        'phone': '+79009890000',
        'email': 'email02@test.com',
        'email_status': 'confirmed',
        'phone_id': '54f031119cc7a09257112b03',
        'yandex_uid': 'yandex_uid_3',
        'personal_email_id': 'personal_email_id_3',
        'personal_phone_id': 'personal_phone_id_3',
        'yandex_uid_type': 'web_cookie',
    },
    '4': {
        'phone': '+79444444444',
        'email': 'email01@test.com',
        'email_status': 'unconfirmed',
        'phone_id': '54f031119cc7a09257112b04',
        'yandex_uid': 'yandex_uid_4',
        'personal_email_id': 'personal_email_id_4',
        'personal_phone_id': 'personal_phone_id_4',
    },
}


async def test_search_by_pd_no_parameters(taxi_admin_personal):
    response = await utils.make_post_request(
        taxi_admin_personal, '/user/search/', data={},
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'REQUEST_VALIDATION_ERROR'


async def test_search_by_phone(
        web_app_client, mock_countries, mockserver, patch,
):
    @patch('taxi.clients.personal.PersonalApiClient.find')
    # pylint: disable=unused-variable
    async def find(*args, **kwargs):
        return {'id': '123123123123123123', 'phone': '+79000000000'}

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_personal/retrieve_bulk',
    )
    # pylint: disable=unused-variable
    async def get_phones_info_by_personal(*args, **kwargs):
        items = [{'id': phone_id} for phone_id in PHONE_IDS]
        return {'items': items}

    content = await utils.post_ok_json_response(
        '/user/search/', {'phone': '+79000000000'}, web_app_client,
    )
    assert set(content['phone_ids']) == set(PHONE_IDS)
    assert list(content.keys()) == ['phone_ids']


async def test_get_pd_no_user(web_app_client):
    response = await utils.make_get_request(web_app_client, '/user/retrieve/')
    assert response.status == 404


@pytest.mark.parametrize('user_id', USERS_PD.keys())
@pytest.mark.parametrize(
    'permissions,expected_fields',
    [
        (['view_user_phones'], ['phone']),
        (['view_user_emails'], ['email', 'email_status']),
        (
            ['view_user_phones', 'view_user_emails'],
            ['phone', 'email', 'email_status'],
        ),
        (['view_driver_licenses', 'view_driver_phones'], []),
    ],
)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={
        '__default__': 'yataxi',
        'yataxi_test': 'test_brand',
    },
    API_OVER_DATA_WORK_MODE={'__default__': {'__default__': 'newway'}},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_get_pd(
        web_app_client,
        mock_countries,
        user_id,
        permissions,
        expected_fields,
        patch,
        mockserver,
):
    @patch('taxi.clients.user_api.UserApiClient.get_user')
    # pylint: disable=unused-variable
    async def get_user(*args, **kwargs):
        user_data = {
            'id': user_id,
            'phone_id': USERS_PD[user_id]['phone_id'],
            'yandex_uid': USERS_PD[user_id]['yandex_uid'],
        }
        application = USERS_PD[user_id].get('application')
        if application:
            user_data['application'] = application

        yandex_uid_type = USERS_PD[user_id].get('yandex_uid_type')
        if yandex_uid_type:
            user_data['yandex_uid_type'] = yandex_uid_type

        return user_data

    @patch('taxi.clients.user_api.UserApiClient.get_user_emails')
    # pylint: disable=unused-variable
    async def get_user_emails(
            email_ids, phone_ids, yandex_uids, brand, log_extra=None,
    ):
        if user_id == '1':
            assert brand == 'test_brand'
        else:
            assert brand == 'yataxi'

        yandex_uid = USERS_PD[user_id]['yandex_uid']
        user_email_data = {
            'id': 'email_id_{}'.format(user_id),
            'phone_id': USERS_PD[user_id]['phone_id'],
            'yandex_uid': yandex_uid,
            'personal_email_id': USERS_PD[user_id]['personal_email_id'],
            'confirmed': False,
        }
        if USERS_PD[user_id]['email_status'] == 'confirmed':
            user_email_data['confirmed'] = True

        return [user_email_data]

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone')
    # pylint: disable=unused-variable
    async def get_user_phone(*args, **kwargs):
        user_phone_data = {
            'id': 'phone_id_{}'.format(user_id),
            'personal_phone_id': USERS_PD[user_id]['personal_phone_id'],
        }
        return user_phone_data

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    # pylint: disable=unused-variable
    async def find(*args, **kwargs):
        return {'id': user_id, 'value': USERS_PD[user_id]['phone']}

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    # pylint: disable=unused-variable
    async def email_retrieve(*args, **kwargs):
        email_data = {
            'id': USERS_PD[user_id]['personal_email_id'],
            'value': USERS_PD[user_id]['email'],
        }
        return email_data

    expected = {field: USERS_PD[user_id][field] for field in expected_fields}
    with utils.has_permissions(permissions):
        response = await utils.make_post_request(
            web_app_client, f'/user/{user_id}/retrieve/',
        )
    assert response.status == 200
    content = await response.json()
    assert content == expected


async def test_exception(patch, web_app_client):
    from taxi_admin_personal import exceptions

    @patch('taxi_admin_personal.internal.users._clean_phone')
    async def _clean_phone(*args, **kwargs):
        raise exceptions.NotFound('test msg')

    response = await utils.make_post_request(
        web_app_client, '/user/search/', data={'phone': '+791111'},
    )
    expected = {'message': 'test msg', 'code': 'NOT_FOUND'}

    assert response.status == 404
    content = await response.json()
    assert content == expected
