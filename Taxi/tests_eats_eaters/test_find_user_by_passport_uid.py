import pytest


TEST_DEACTIVATED_AT = '2019-12-31T10:59:59+03:00'

TEST_UUID = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6748'
TEST_UUID2 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6749'

TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID2 = '999999999999999999999998'

TEST_EATER_TYPE = 'native'
TEST_EATER_TYPE2 = 'magnit'


async def test_200(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(uuid=TEST_UUID, passport_uid=TEST_PASSPORT_UID)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(
        uuid=TEST_UUID2,
        passport_uid=TEST_PASSPORT_UID2,
        deactivated_at=TEST_DEACTIVATED_AT,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid'], 'with_soft_deleted': True},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_404(taxi_eats_eaters, create_user, get_user):
    eater_id = create_user(deactivated_at=TEST_DEACTIVATED_AT)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': '5555', 'with_soft_deleted': True},
    )

    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    assert response.status_code == 404


async def test_with_nulls(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(
        personal_email_id=None,
        personal_phone_id=None,
        passport_uid=TEST_PASSPORT_UID,
        passport_uid_type=None,
        eater_type=None,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


@pytest.mark.parametrize(
    'existing_eater_type, request_eater_type, allow_null_type, expected_found',
    [
        pytest.param(
            TEST_EATER_TYPE,
            TEST_EATER_TYPE,
            None,
            True,
            id='same type, found',
        ),
        pytest.param(
            TEST_EATER_TYPE,
            TEST_EATER_TYPE2,
            None,
            False,
            id='another type, not found',
        ),
        pytest.param(
            TEST_EATER_TYPE, None, None, True, id='no request type, found',
        ),
        pytest.param(
            None, None, None, True, id='null db type, no request type, found',
        ),
        pytest.param(
            None, None, True, True, id='null db type, allow null type, found',
        ),
        pytest.param(
            None,
            TEST_EATER_TYPE,
            True,
            True,
            id='null db type, request type and allow null type, found',
        ),
    ],
)
async def test_with_type(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        existing_eater_type,
        request_eater_type,
        allow_null_type,
        expected_found,
):
    eater_id = create_user(eater_type=existing_eater_type)
    user = get_user(eater_id)

    data = {'passport_uid': user['passport_uid']}
    if request_eater_type is not None:
        data['type'] = request_eater_type
    if allow_null_type is not None:
        data['allow_null_type'] = allow_null_type
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid', json=data,
    )

    response_json = response.json()

    if expected_found:
        assert response.status_code == 200
        check_users_are_equal(response_json['eater'], user)
    else:
        assert response.status_code == 404
