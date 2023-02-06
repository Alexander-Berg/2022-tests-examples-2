import datetime

import pytest
import pytz

TEST_EATER_ID = '1'
TEST_EATER_TYPE = 'magnit'
TEST_NAME = 'Иван Иванов'
TEST_UUID = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6748'
TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID_TYPE = 'phonish'
TEST_PHONE_ID = 'phoneid1'
TEST_EMAIL_ID = 'emailid1'
TEST_CLIENT_TYPE = 'corporate'
TEST_CREATED_AT = '2019-12-31T10:59:59+03:00'
TEST_DEACTIVATED_AT = '2019-12-31T10:59:59+03:00'
TEST_BANNED_AT = '2019-12-31T10:59:59+03:00'
TEST_BAN_REASON = 'ban reason'
TEST_ADMIN_ID = '1'

DEFAULT_USER_DATA = {
    'uuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
    'created_at': '2018-01-01T10:59:59+03:00',
    'client_type': 'common',
}


@pytest.mark.pgsql('eats_eaters', files=['init_users.sql'])
@pytest.mark.parametrize(
    'request_data',
    [
        pytest.param(
            {
                'eater_id': TEST_EATER_ID,
                'type': TEST_EATER_TYPE,
                'name': TEST_NAME,
                'passport_uid': TEST_PASSPORT_UID,
                'passport_uid_type': TEST_PASSPORT_UID_TYPE,
                'personal_phone_id': TEST_PHONE_ID,
                'personal_email_id': TEST_EMAIL_ID,
                'client_type': TEST_CLIENT_TYPE,
                'created_at': TEST_CREATED_AT,
                'deactivated_at': TEST_DEACTIVATED_AT,
                'banned_at': TEST_BANNED_AT,
                'ban_reason': TEST_BAN_REASON,
            },
            id='all fields',
        ),
        pytest.param({'eater_id': TEST_EATER_ID}, id='only eater id'),
        pytest.param(
            {'eater_id': TEST_EATER_ID, 'type': 'burger_king'},
            id='eater id and type',
        ),
    ],
)
async def test_204(
        taxi_eats_eaters,
        taxi_config,
        get_user,
        check_user_data,
        check_users_are_equal,
        request_data,
        check_history_stq,
        stq,
):
    taxi_config.set_values(
        {'EATS_EATERS_FEATURE_FLAGS': {'save_history': True}},
    )
    eater_id = int(request_data['eater_id'])
    old_user_data = get_user(eater_id)

    datetime_before = datetime.datetime.now(tz=pytz.utc)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update', json=request_data,
    )
    assert response.status_code == 204

    datetime_after = datetime.datetime.now(tz=pytz.utc)

    user = get_user(eater_id)
    check_user_data(user, {**DEFAULT_USER_DATA, **request_data})

    assert stq.eater_change_history.times_called == 1
    check_history_stq(
        stq.eater_change_history.next_call(),
        old_user_data,
        user,
        datetime_before,
        datetime_after,
    )

    find_data = {'id': str(eater_id), 'with_soft_deleted': False}
    if 'deactivated_at' in request_data:
        find_data['with_soft_deleted'] = True
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id', json=find_data,
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


@pytest.mark.pgsql('eats_eaters', files=['init_users.sql'])
async def test_cache(
        taxi_eats_eaters, get_user, check_user_data, check_users_are_equal,
):
    eater_id = int(TEST_EATER_ID)
    new_phone_id = TEST_PHONE_ID

    # requests before update
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )
    assert response.status_code == 200
    response_json = response.json()
    old_user = get_user(response_json['eater']['id'])
    check_users_are_equal(response_json['eater'], old_user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': old_user['uuid']},
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], old_user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': old_user['passport_uid']},
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], old_user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': old_user['personal_email_id']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], old_user)

    # update user:
    # change passport_uid and uuid,
    # set personal_phone_id and reset personal_email_id
    request_data = {
        'eater_id': str(eater_id),
        'type': old_user['type'],
        'name': old_user['name'],
        'passport_uid': TEST_PASSPORT_UID,
        'passport_uid_type': old_user['passport_uid_type'],
        'uuid': TEST_UUID,
        'personal_phone_id': new_phone_id,
    }
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update', json=request_data,
    )
    assert response.status_code == 204
    user = get_user(eater_id)
    check_user_data(user, {**DEFAULT_USER_DATA, **request_data})

    # requests after update
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': old_user['uuid']},
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': request_data['uuid']},
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': old_user['passport_uid']},
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': request_data['passport_uid']},
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': old_user['personal_email_id']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['eaters']

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={'personal_phone_id': new_phone_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)


@pytest.mark.pgsql('eats_eaters', files=['init_users.sql'])
async def test_400(taxi_eats_eaters):
    eater_type = 'too_long_eater_type'
    request_data = {
        'eater_id': TEST_EATER_ID,
        'type': eater_type,
        'passport_uid': TEST_PASSPORT_UID,
    }
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update', json=request_data,
    )
    assert response.status_code == 400

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': request_data['passport_uid']},
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_eaters', files=['init_users.sql'])
async def test_409(taxi_eats_eaters, create_user, get_user):
    eater_id = int(TEST_EATER_ID)
    second_eater_id = create_user(
        uuid=TEST_UUID, passport_uid=TEST_PASSPORT_UID,
    )
    second_old_user = get_user(second_eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update',
        json={
            'eater_id': str(eater_id),
            'passport_uid': second_old_user['passport_uid'],
        },
    )
    assert response.status_code == 409

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update',
        json={'eater_id': str(eater_id), 'uuid': second_old_user['uuid']},
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    'requests, path',
    [
        pytest.param(
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {
                        'admin_id': '3',
                        'type': TEST_EATER_TYPE,
                        'name': TEST_NAME,
                    },
                },  # with user_id and admin_id
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {
                        'personal_email_id': TEST_EMAIL_ID,
                        'client_type': TEST_CLIENT_TYPE,
                        'created_at': TEST_CREATED_AT,
                    },
                },  # with user_id only
                {
                    'json': {
                        'admin_id': '3',
                        'passport_uid': TEST_PASSPORT_UID,
                        'passport_uid_type': TEST_PASSPORT_UID_TYPE,
                        'personal_phone_id': TEST_PHONE_ID,
                    },
                },  # with admin_id only
                {
                    'json': {
                        'deactivated_at': TEST_DEACTIVATED_AT,
                        'banned_at': TEST_BANNED_AT,
                        'ban_reason': TEST_BAN_REASON,
                    },
                },  # without initiator info (system)
            ],
            '/v1/eaters/update',
        ),
    ],
)
async def test_history_after_update(requests, path, update_and_check_history):
    await update_and_check_history(
        path, requests, init_user_data=None, save_history=True,
    )


@pytest.mark.parametrize(
    'requests, path',
    [
        pytest.param(
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {
                        'admin_id': '3',
                        'type': TEST_EATER_TYPE,
                        'name': TEST_NAME,
                    },
                },
            ],
            '/v1/eaters/update',
        ),
    ],
)
async def test_update_without_save_history(
        path, requests, update_and_check_history,
):
    await update_and_check_history(
        path, requests, init_user_data=None, save_history=False,
    )


@pytest.mark.parametrize(
    'requests, init_data, path',
    [
        pytest.param(
            [{'json': {'admin_id': '3', 'name': 'Иван Сусанин'}}],
            {
                'eater_name': 'Иван Сусанин',
                'personal_email_id': None,
                'personal_phone_id': None,
                'deactivated_at': None,
                'banned_at': None,
                'ban_reason': None,
                'passport_uid': None,
                'passport_uid_type': None,
                'eater_type': None,
            },
            '/v1/eaters/update',
        ),
    ],
)
async def test_history_after_update_without_change(
        requests, init_data, path, update_and_check_history,
):
    await update_and_check_history(
        path, requests, init_user_data=init_data, save_history=True,
    )


async def test_authorized_empty_user_id(taxi_eats_eaters, create_user):
    eater_id = create_user(eater_name='kara')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update',
        headers={
            'X-Eats-User': (
                'personal_phone_id=4303f195c2fb4aff997ca66063980a16,'
                'partner_user_id=176998645,'
                'phone_id=5e8b12137984b5db624bfbb2'
            ),
            'X-YaTaxi-Session': 'eats:228934',
            'X-Yandex-UID': '000000000',
        },
        json={'eater_id': str(eater_id), 'name': 'karakatitsa'},
    )

    assert response.status_code == 400


async def test_user_not_found(taxi_eats_eaters, create_user):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update', json={'eater_id': '228', 'name': 'karakatitsa'},
    )

    assert response.status_code == 404


async def test_update_last_login(
        taxi_eats_eaters, get_user, format_datetime, create_user,
):
    eater_id = create_user()
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update',
        json={
            'eater_id': str(eater_id),
            'last_login': '2021-12-31T10:59:59+03:00',
        },
    )

    user = get_user(eater_id)

    assert response.status_code == 204
    assert format_datetime(user['last_login']) == '2021-12-31T10:59:59+03:00'

    # Try to update eater without last_login field. The update function
    # should complete successfully, but the last_login value should not change
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update',
        json={'eater_id': str(eater_id), 'last_login': None},
    )

    user = get_user(eater_id)
    assert response.status_code == 204
    assert format_datetime(user['last_login']) == '2021-12-31T10:59:59+03:00'
