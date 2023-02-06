import pytest


@pytest.mark.parametrize(
    [
        'code',
        'user_id',
        'expected_drive',
        'expected_promocode',
        'expected_account_id',
    ],
    [
        pytest.param(
            200,
            'user1',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'drive_user_id': 'drive_user_id',
                'group_id': 'example',
                'is_active': True,
            },
            {},
            1,
            id='has_drive_user_id',
        ),
        pytest.param(
            200,
            'user3',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'group_id': 'group_id',
                'is_active': True,
            },
            {'status': 'add', 'code': 'promocode'},
            3,
            id='expired_code',
        ),
        pytest.param(
            200,
            'user4',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'group_id': 'group_id',
                'is_active': True,
            },
            {'status': 'add', 'code': 'promocode'},
            4,
            id='removed_promocode',
        ),
        pytest.param(
            200,
            'user5',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'drive_user_id': 'drive_user_id',
                'group_id': 'group_id',
                'is_active': True,
            },
            {},
            5,
            id='has_drive_user_id_and_promo',
        ),
        pytest.param(
            200,
            'user6',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'group_id': 'group_id',
                'is_active': True,
            },
            {},
            6,
            id='no_drive_user_id_but_has_promo',
        ),
        pytest.param(
            200,
            'user7',
            {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'drive_user_id': None,
                'group_id': None,
                'is_active': True,
            },
            {},
            7,
            id='client_without_drive',
        ),
    ],
)
async def test_single_put(
        taxi_corp_auth_client,
        pd_patch,
        drive_patch,
        db,
        mockserver,
        code,
        mock_drive,
        user_id,
        expected_drive,
        expected_promocode,
        expected_account_id,
        patch,
):
    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert personal_phone_id == 'pd_id'
        assert text == 'sms.create_user'
        assert intent == 'taxi_corp_taxi_account_created'

    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    mock_drive.data.descriptions_response = {
        'accounts': [{'meta': {'parent_id': 123}}],
    }
    mock_drive.data.drive_accounts_response = {
        'soft_limit': None,
        'type_name': 'group_id',
        'is_active': False,
        'parent': {'id': 123},
    }
    mock_drive.data.promocode_response = {
        'accounts': [
            {
                'code': 'promocode',
                'account_id': expected_account_id,
                'deeplink': 'http://deeplink',
            },
        ],
    }
    mock_drive.data.expected_account_id = str(expected_account_id)

    base_user = {
        'fullname': 'Joe',
        'phone': '+79291112208',
        'role': {'limit': 1000, 'classes': ['econom']},
        'email': 'joe@mail.com',
        'is_active': True,
        'services': {
            'drive': {
                'soft_limit': '1000.00',
                'hard_limit': '1000.00',
                'group_id': 'group_id',
                'is_active': True,
            },
        },
    }
    response = await taxi_corp_auth_client.put(
        '/1.0/client/client/user/{}'.format(user_id), json=base_user,
    )
    response_json = await response.json()
    assert response.status == code, response_json
    db_item = await db.corp_users.find_one({'_id': user_id})
    for key, value in expected_drive.items():
        assert db_item['services']['drive'][key] == value

    db_items = await db.corp_drive_promocodes.find(
        {'user_id': user_id},
    ).to_list(None)
    if db_items:
        db_items_add = [code for code in db_items if code['status'] == 'add']
        for key, value in expected_promocode.items():
            assert db_items_add[0][key] == value
