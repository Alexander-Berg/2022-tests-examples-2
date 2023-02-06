import pytest

BLACKBOX_UID = '101'
USER_IP = '1.2.3.4'

DUPLICATE_LOGIN = 'duplicate_login'
DUPLICATE_UID = '777'


@pytest.mark.parametrize(
    'params, post_content, expected_doc',
    [
        pytest.param(
            {'manager_id': 'department_manager1'},
            {
                'department_id': 'd1',
                'email': 'mr_anderson@matrix.corp',
                'phone': '+79161237700',
                'fullname': 'Mr. Anderson',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
            },
            {
                'department_id': 'd1',
                'client_id': 'client1',
                'email': 'mr_anderson@matrix.corp',
                'email_id': 'mr_anderson@matrix.corp_id',
                'phone': '+79161237700',
                'phone_id': '+79161237700_id',
                'fullname': 'Mr. Anderson',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
                'yandex_login_id': 'mr_anderson_id',
                'yandex_uid': '101',
            },
            id='max fill',
        ),
        pytest.param(
            {'manager_id': 'department_manager2'},
            {
                'fullname': 'Mr. Anderson',
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
            },
            {
                'fullname': 'Mr. Anderson',
                'client_id': 'client1',
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
                'yandex_login_id': 'mr_anderson_id',
                'yandex_uid': '101',
                'phone': '+79161237704',
                'phone_id': '+79161237704_id',
                'email': 'department_manager2@client1',
                'email_id': 'department_manager2@client1_id',
            },
            id='min fill',
        ),
        pytest.param(
            {'manager_id': 'department_manager2'},
            {
                'fullname': 'Mr. Anderson',
                'department_id': 'd1',
                'role': 'department_secretary',
                'yandex_login': 'department_manager2',
            },
            {
                'fullname': 'Mr. Anderson',
                'client_id': 'client1',
                'department_id': 'd1',
                'role': 'department_secretary',
                'yandex_login': 'department_manager2',
                'yandex_login_id': 'department_manager2_id',
                'yandex_uid': 'department_manager2_uid',
                'phone': '+79161237704',
                'phone_id': '+79161237704_id',
                'email': 'department_manager2@client1',
                'email_id': 'department_manager2@client1_id',
            },
            id='change role from manager to secretary',
        ),
        pytest.param(
            {'yandex_uid': 'department_manager2_uid'},
            {
                'fullname': 'Mr. Anderson',
                'department_id': 'd1',
                'role': 'department_secretary',
                'yandex_login': 'department_manager2',
            },
            {
                'fullname': 'Mr. Anderson',
                'client_id': 'client1',
                'department_id': 'd1',
                'role': 'department_secretary',
                'yandex_login': 'department_manager2',
                'yandex_login_id': 'department_manager2_id',
                'yandex_uid': 'department_manager2_uid',
                'phone': '+79161237704',
                'phone_id': '+79161237704_id',
                'email': 'department_manager2@client1',
                'email_id': 'department_manager2@client1_id',
            },
            id='change role from manager to secretary',
        ),
    ],
)
async def test_managers_update(
        taxi_corp_managers,
        mock_personal,
        blackbox_service,
        mongodb,
        params,
        post_content,
        expected_doc,
):
    blackbox_service.set_user_info(BLACKBOX_UID, post_content['yandex_login'])

    query = {}
    if params.get('manager_id'):
        query['_id'] = params['manager_id']
    if params.get('yandex_uid'):
        query['yandex_uid'] = params['yandex_uid']

    db_original_item = mongodb.corp_managers.find_one(query)
    response = await taxi_corp_managers.post(
        '/v1/managers/update',
        params=params,
        headers={'X-Remote-IP': USER_IP},
        json=post_content,
    )

    assert response.status == 200
    assert response.json() == {}

    db_updated_item = mongodb.corp_managers.find_one(query)
    assert db_original_item.get('created') == db_updated_item.get('created')
    assert db_original_item.get('updated') != db_updated_item['updated']

    for name in ['_id', 'created', 'updated']:
        db_updated_item.pop(name, None)

    assert db_updated_item == expected_doc


@pytest.mark.parametrize(
    'manager_id, blackbox_uid, post_content, expected_status, expected_error',
    [
        pytest.param(
            'department_manager1',
            DUPLICATE_UID,
            {
                'fullname': 'Guts',
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'duplicate_login',
                'email': 'department_manager_duplicate@client1',
                'phone': '+79162223332',
            },
            400,
            'A user with this login already exists',
            id='duplicate yandex login',
        ),
        pytest.param(
            'department_manager1',
            None,
            {
                'fullname': 'Guts',
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'invalid_login',
                'phone': '+79162223332',
            },
            400,
            'Unknown username (yandex_login)',
            id='invalid login',
        ),
        (
            'not_existed_id',
            BLACKBOX_UID,
            {
                'fullname': 'Guts',
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'some_login',
                'phone': '+79162223332',
            },
            404,
            'Manager not found',
        ),
    ],
)
async def test_managers_update_fail(
        taxi_corp_managers,
        mock_personal,
        blackbox_service,
        manager_id,
        blackbox_uid,
        post_content,
        expected_status,
        expected_error,
):
    if blackbox_uid is not None:
        blackbox_service.set_user_info(
            blackbox_uid, post_content['yandex_login'],
        )

    response = await taxi_corp_managers.post(
        '/v1/managers/update',
        params={'manager_id': manager_id},
        headers={'X-Remote-IP': USER_IP},
        json=post_content,
    )

    response_json = response.json()
    assert response.status == expected_status, response_json

    assert expected_error in response_json['message']
