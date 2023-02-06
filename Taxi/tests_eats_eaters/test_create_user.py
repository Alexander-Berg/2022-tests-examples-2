import pytest


TEST_EATER_TYPE = 'native'
TEST_EATER_ID = '123'
TEST_NAME = 'Иван Иванов'
TEST_UUID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1'
TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID_TYPE = 'portal'
TEST_PHONE_ID = 'phoneid1'
TEST_EMAIL_ID = 'emailid1'
TEST_CLIENT_TYPE = 'common'
TEST_CREATED_AT = '2019-12-31T10:59:59+03:00'
TEST_DEACTIVATED_AT = '2019-12-31T10:59:59+03:00'
TEST_BANNED_AT = '2019-12-31T10:59:59+03:00'
TEST_BAN_REASON = 'ban reason'
TEST_LAST_LOGIN = '2019-12-31T10:59:59+03:00'


@pytest.mark.parametrize(
    'request_data',
    [
        pytest.param(
            {
                'type': TEST_EATER_TYPE,
                'name': TEST_NAME,
                'passport_uid': TEST_PASSPORT_UID,
                'passport_uid_type': TEST_PASSPORT_UID_TYPE,
                'personal_phone_id': TEST_PHONE_ID,
                'uuid': TEST_UUID,
                'personal_email_id': TEST_EMAIL_ID,
                'client_type': TEST_CLIENT_TYPE,
                'created_at': TEST_CREATED_AT,
                'deactivated_at': TEST_DEACTIVATED_AT,
                'banned_at': TEST_BANNED_AT,
                'ban_reason': TEST_BAN_REASON,
                'last_login': TEST_LAST_LOGIN,
            },
        ),
        pytest.param({'eater_id': TEST_EATER_ID, 'type': TEST_EATER_TYPE}),
        pytest.param({'type': TEST_EATER_TYPE}),
        pytest.param({'type': 'burger_king'}),
    ],
)
async def test_200(
        taxi_eats_eaters,
        get_user,
        check_user_data,
        check_users_are_equal,
        request_data,
        format_datetime,
):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )

    response_json = response.json()

    assert response.status_code == 200

    eater_id = response_json['eater']['id']
    user = get_user(eater_id)
    check_user_data(user, request_data)
    check_users_are_equal(response_json['eater'], user)

    if 'last_login' in request_data:
        assert format_datetime(user['last_login']) == TEST_LAST_LOGIN

    find_data = {'id': str(eater_id), 'with_soft_deleted': False}
    if 'deactivated_at' in request_data:
        find_data['with_soft_deleted'] = True
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id', json=find_data,
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_cache(
        taxi_eats_eaters, get_user, check_user_data, check_users_are_equal,
):
    new_eater_id = 1

    # requests before creation
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(new_eater_id), 'with_soft_deleted': False},
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': TEST_PASSPORT_UID},
    )
    assert response.status_code == 404

    # create user
    request_data = {'type': TEST_EATER_TYPE, 'passport_uid': TEST_PASSPORT_UID}
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    response_json = response.json()
    assert response.status_code == 200
    user = get_user(response_json['eater']['id'])
    assert user['id'] == new_eater_id
    check_user_data(user, request_data)
    check_users_are_equal(response_json['eater'], user)

    # requests after creation
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(new_eater_id), 'with_soft_deleted': False},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': TEST_PASSPORT_UID},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_400(taxi_eats_eaters):
    eater_type = 'too_long_eater_type'
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create',
        json={'type': eater_type, 'passport_uid': TEST_PASSPORT_UID},
    )
    assert response.status_code == 400

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': TEST_PASSPORT_UID},
    )
    assert response.status_code == 404


async def test_409(
        taxi_eats_eaters, get_user, check_user_data, check_users_are_equal,
):
    eater_id = '1'

    request_data = {'eater_id': eater_id, 'type': TEST_EATER_TYPE}
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    response_json = response.json()
    assert response.status_code == 200
    user = get_user(response_json['eater']['id'])
    check_user_data(user, request_data)
    check_users_are_equal(response_json['eater'], user)

    # first time we catch conflict, but autoincrement increased
    request_data = {'type': TEST_EATER_TYPE, 'passport_uid': TEST_PASSPORT_UID}
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    assert response.status_code == 409

    # second time everything is ok
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    response_json = response.json()
    assert response.status_code == 200
    user = get_user(response_json['eater']['id'])
    assert user['id'] == int(eater_id) + 1
    check_user_data(user, request_data)
    check_users_are_equal(response_json['eater'], user)

    # third time we again catch conflict - now because of passport_uid
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    assert response.status_code == 409

    # again catch conflict - now because of uuid
    request_data = {'type': TEST_EATER_TYPE, 'uuid': user['uuid']}
    response = await taxi_eats_eaters.post(
        '/v1/eaters/create', json=request_data,
    )
    assert response.status_code == 409
