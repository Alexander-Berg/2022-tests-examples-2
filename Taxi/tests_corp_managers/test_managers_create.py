import datetime

import pytest

BLACKBOX_UID = '101'
USER_IP = '1.2.3.4'
LONG_FULLNAME = 'a' * 257

DUPLICATE_LOGIN = 'duplicate_login'
DUPLICATE_UID = '777'


@pytest.mark.parametrize(
    'post_content, expected_doc',
    [
        (
            {
                'client_id': 'client_id_1',
                'department_id': 'd1',
                'email': ' MR_anderson@matrix.corp ',
                'phone': '+79161237700',
                'fullname': 'Mr. Anderson',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
            },
            {
                'department_id': 'd1',
                'client_id': 'client_id_1',
                'email': 'mr_anderson@matrix.corp',
                'email_id': 'mr_anderson@matrix.corp_id',
                'phone': '+79161237700',
                'phone_id': '+79161237700_id',
                'fullname': 'Mr. Anderson',
                'role': 'department_manager',
                'yandex_login': 'mr_anderson',
                'yandex_login_id': 'mr_anderson_id',
                'yandex_uid': BLACKBOX_UID,
            },
        ),
        (
            {
                'client_id': 'client_id_2',
                'fullname': 'Mr. Anderson',
                'department_id': 'd2',
                'role': 'department_secretary',
                'yandex_login': 'mr_anderson',
            },
            {
                'fullname': 'Mr. Anderson',
                'client_id': 'client_id_2',
                'department_id': 'd2',
                'role': 'department_secretary',
                'yandex_login': 'mr_anderson',
                'yandex_login_id': 'mr_anderson_id',
                'yandex_uid': BLACKBOX_UID,
            },
        ),
        (
            {
                'client_id': 'client_id_2',
                'fullname': 'Mr. Anderson',
                'role': 'manager',
                'yandex_login': 'mr_anderson',
            },
            {
                'fullname': 'Mr. Anderson',
                'client_id': 'client_id_2',
                'role': 'manager',
                'yandex_login': 'mr_anderson',
                'yandex_login_id': 'mr_anderson_id',
                'yandex_uid': BLACKBOX_UID,
            },
        ),
        (
            {
                'client_id': 'client_id_3',
                'role': 'client',
                'yandex_login': 'client_id_3_login',
            },
            {
                'client_id': 'client_id_3',
                'role': 'client',
                'yandex_login': 'client_id_3_login',
                'yandex_login_id': 'client_id_3_login_id',
                'yandex_uid': BLACKBOX_UID,
            },
        ),
    ],
)
async def test_managers_create(
        taxi_corp_managers,
        mock_personal,
        blackbox_service,
        mongodb,
        post_content,
        expected_doc,
):
    blackbox_service.set_user_info(BLACKBOX_UID, post_content['yandex_login'])

    response = await taxi_corp_managers.post(
        '/v1/managers/create',
        headers={'X-Remote-IP': USER_IP},
        json=post_content,
    )

    response_json = response.json()
    assert response.status == 200, response_json
    assert list(response_json) == ['id']

    db_item = mongodb.corp_managers.find_one({'_id': response_json['id']})

    assert isinstance(db_item.get('created'), datetime.datetime)
    assert isinstance(db_item.get('updated'), datetime.datetime)
    assert db_item['updated'] >= db_item['created']

    for name in ['_id', 'created', 'updated']:
        del db_item[name]

    assert db_item == expected_doc


@pytest.mark.parametrize(
    'post_content, expected_status, expected_error',
    [
        pytest.param(
            {
                'client_id': 'client1',
                'fullname': 'Guts',
                'role': 'manager',
                'yandex_login': 'guts',
                'phone': 'bad_phone',
            },
            400,
            '(bad_phone) doesn\'t match',
            id='bad email format',
        ),
        pytest.param(
            {
                'client_id': 'client1',
                'fullname': LONG_FULLNAME,
                'department_id': 'd1',
                'role': 'department_manager',
                'yandex_login': 'guts',
                'email': 'mr_anderson@matrix.corp',
                'phone': '+79161237700',
            },
            400,
            '\'fullname\': incorrect size, must be 256',
            id='max indexed len',
        ),
        pytest.param(
            {
                'client_id': 'client1',
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
    ],
)
async def test_managers_create_fail(
        taxi_corp_managers,
        mock_personal,
        blackbox_service,
        post_content,
        expected_status,
        expected_error,
):
    if post_content['yandex_login'] == DUPLICATE_LOGIN:
        blackbox_service.set_user_info(
            DUPLICATE_UID, post_content['yandex_login'],
        )
    else:
        blackbox_service.set_user_info(
            BLACKBOX_UID, post_content['yandex_login'],
        )

    response = await taxi_corp_managers.post(
        '/v1/managers/create',
        headers={'X-Remote-IP': USER_IP},
        json=post_content,
    )

    response_json = response.json()
    assert response.status == expected_status, response_json

    assert expected_error in response_json['message']
