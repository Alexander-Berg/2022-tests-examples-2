import pytest

from taxi.clients import personal

from test_taxi_corp import test_user_post


@pytest.mark.parametrize(
    ['post_content', 'expected_pd_calls', 'pd_doc_fields'],
    [
        pytest.param(
            {
                'fullname': 'Boe',
                'phone': '+79291112214',
                'role': {'limit': 5000, 'classes': ['econom']},
                'email': 'boe@mail.com',
                'is_active': True,
            },
            {
                personal.PERSONAL_TYPE_EMAILS: 'boe@mail.com',
                personal.PERSONAL_TYPE_PHONES: '+79291112214',
            },
            ['email_id', 'phone_id'],
            id='simple_create',
        ),
        pytest.param(
            {
                'fullname': 'Boe',
                'phone': '+79291112214',
                'role': {'limit': 5000, 'classes': ['econom']},
                'email': '',
                'is_active': True,
            },
            {personal.PERSONAL_TYPE_PHONES: '+79291112214'},
            ['email_id', 'phone_id'],
            id='create_without_pd',
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=test_user_post.CORP_USER_PHONES_SUPPORTED_79,
    PERSONAL_PHONES_STORE_PYTHON3_ENABLED=True,
)
async def test_personal_post(
        taxi_corp_auth_client,
        db,
        patch,
        response_mock,
        post_content,
        expected_pd_calls,
        pd_doc_fields,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': phone_id, 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, phone_type, *args, **kwargs):
        def phone_to_hex(phone):
            if phone.startswith('+'):
                phone = phone[1:]
            return 'A' * (24 - len(phone)) + phone

        return {
            'id': phone_to_hex(phone),
            'phone': phone,
            'type': phone_type,
            'personal_phone_id': 'pd_id',
        }

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert personal_phone_id == 'pd_id'
        assert text == 'sms.create_user'
        assert intent == 'taxi_corp_taxi_account_created'

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        response = {'id': 'pd_id'}
        if data_type == personal.PERSONAL_TYPE_PHONES:
            response['phone'] = request_value
        elif data_type == personal.PERSONAL_TYPE_EMAILS:
            response['email'] = request_value

        return response

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user', json=post_content,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_users.find_one({'_id': response_json['_id']})
    for expected_field in pd_doc_fields:
        assert expected_field in db_item


@pytest.mark.translations(
    corp={
        'role.others_name': {'ru': 'role.others_name'},
        'sms.eats_activate_sms': {'ru': 'Еда подключена!'},
    },
)
@pytest.mark.parametrize(
    'client_id, user_id, put_content, expected_pd_calls, pd_doc_fields',
    [
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'limit': 1000, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                personal.PERSONAL_TYPE_EMAILS: 'joe@mail.com',
                personal.PERSONAL_TYPE_PHONES: '+79291112204',
            },
            ['email_id'],
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=test_user_post.CORP_USER_PHONES_SUPPORTED_79,
    COST_CENTERS_VALUES_MAX_COUNT=2,
)
async def test_personal_put(
        taxi_corp_auth_client,
        pd_patch,
        db,
        patch,
        client_id,
        user_id,
        put_content,
        expected_pd_calls,
        pd_doc_fields,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'12345': 'user_id'}]}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return None

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/user/{}'.format(client_id, user_id), json=put_content,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_users.find_one({'_id': user_id})
    for expected_field in pd_doc_fields:
        assert expected_field in db_item


@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=test_user_post.CORP_USER_PHONES_SUPPORTED_79,
    CORP_DRIVE_USE_PRESTABLE=True,
)
@pytest.mark.parametrize(
    'passport_mock, put_content, expected_pd_calls, pd_doc_fields',
    [
        pytest.param(
            'client1',
            {
                'fullname': 'Restore',
                'phone': '+79291112210',
                'role': {'limit': 7000, 'classes': ['econom']},
                'email': 'restore@mail.com',
                'is_active': False,
            },
            {
                personal.PERSONAL_TYPE_EMAILS: 'restore@mail.com',
                personal.PERSONAL_TYPE_PHONES: '+79291112210',
            },
            ['email_id'],
            id='client_restore',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_personal_restore(
        taxi_corp_real_auth_client,
        pd_patch,
        drive_patch,
        db,
        patch,
        passport_mock,
        put_content,
        expected_pd_calls,
        pd_doc_fields,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _descriptions(*args, **kwargs):
        return {
            'accounts': [
                {
                    'name': 'corp_yataxi_client1_default',
                    'soft_limit': 1000,
                    'hard_limit': 1000,
                    'meta': {'parent_id': 123},
                },
            ],
        }

    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'userRestore_uid': 'user_id'}]}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return {
            'id': 100,
            'type_name': None,
            'soft_limit': None,
            'hard_limit': None,
            'is_active': False,
            'parent': {'id': 123},
        }

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/client1/user/userRestore/restore', json=put_content,
    )

    response_json = await response.json()
    assert response_json == {}
    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_users.find_one({'_id': 'userRestore'})
    for expected_field in pd_doc_fields:
        assert expected_field in db_item


@pytest.mark.parametrize(
    'post_content, expected_pd_calls, pd_doc_fields',
    [
        pytest.param(
            {
                'phone': '+79291112211',
                'role': {'limit': 5000, 'classes': ['econom']},
                'is_active': True,
                'fullname': 'Full Name',
                'email': 'test@email.com',
                'nickname': 'tester',
                'cost_center': 'TAXI',
            },
            {
                personal.PERSONAL_TYPE_EMAILS: 'test@email.com',
                personal.PERSONAL_TYPE_PHONES: '+79291112211',
            },
            ['email_id'],
            id='patch_user',
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=test_user_post.CORP_USER_PHONES_SUPPORTED_79,
)
async def test_personal_patch(
        taxi_corp_auth_client,
        pd_patch,
        patch,
        db,
        post_content,
        expected_pd_calls,
        pd_doc_fields,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert personal_phone_id == 'pd_id'
        assert text == 'sms.create_user'
        assert intent == 'taxi_corp_taxi_account_created'

    response = await taxi_corp_auth_client.patch(
        '/1.0/client/client1/user', json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_users.find_one({'_id': response_json['_id']})
    for expected_field in pd_doc_fields:
        assert expected_field in db_item
