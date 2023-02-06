import pytest


TEST_UUID = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6748'
TEST_UUID2 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6749'
TEST_UUID3 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6750'
TEST_UUID4 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6751'

TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID2 = '999999999999999999999998'
TEST_PASSPORT_UID3 = '999999999999999999999997'
TEST_PASSPORT_UID4 = '999999999999999999999996'

TEST_EMAIL_ID = 'emailid1'

TEST_EATER_TYPE = 'native'
TEST_EATER_TYPE2 = 'magnit'


@pytest.mark.parametrize(
    'users,',
    [
        pytest.param([]),
        pytest.param(
            [
                {
                    'personal_email_id': TEST_EMAIL_ID,
                    'uuid': TEST_UUID,
                    'passport_uid': TEST_PASSPORT_UID,
                },
            ],
        ),
        pytest.param(
            [
                {
                    'personal_email_id': TEST_EMAIL_ID,
                    'uuid': TEST_UUID,
                    'passport_uid': TEST_PASSPORT_UID,
                },
                {
                    'personal_email_id': TEST_EMAIL_ID,
                    'uuid': TEST_UUID2,
                    'passport_uid': TEST_PASSPORT_UID2,
                },
            ],
        ),
    ],
)
async def test_200(taxi_eats_eaters, create_user, users):
    for _, user in enumerate(users):
        create_user(
            personal_email_id=user['personal_email_id'],
            uuid=user['uuid'],
            passport_uid=user['passport_uid'],
        )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': TEST_EMAIL_ID},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == len(users)


async def test_with_nulls(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID,
        personal_phone_id=None,
        passport_uid=None,
        passport_uid_type=None,
        eater_type=None,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': user['personal_email_id']},
    )

    response_json = response.json()

    assert response.status_code == 200
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)


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

    data = {'personal_email_id': user['personal_email_id']}
    if request_eater_type is not None:
        data['type'] = request_eater_type
    if allow_null_type is not None:
        data['allow_null_type'] = allow_null_type
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id', json=data,
    )

    response_json = response.json()
    assert response.status_code == 200

    if expected_found:
        assert len(response_json['eaters']) == 1
        check_users_are_equal(response_json['eaters'][0], user)
    else:
        assert not response_json['eaters']


async def test_sort(taxi_eats_eaters, create_user):
    # eater_id0 should be last in the sorted response list (last_login is NULL)
    eater_id0 = create_user(
        personal_email_id=TEST_EMAIL_ID,
        uuid=TEST_UUID,
        passport_uid=TEST_PASSPORT_UID,
    )

    # eater_id1 should be second in the sorted response list
    eater_id1 = create_user(
        personal_email_id=TEST_EMAIL_ID,
        uuid=TEST_UUID2,
        passport_uid=TEST_PASSPORT_UID2,
        last_login='2021-12-31T02:00:00+03:00',
    )

    # eater_id2 should not be first in the sorted response list
    # ('other_email_id' != TEST_PHONE_ID)
    # eater_id2 =
    create_user(
        personal_email_id='other_email_id',
        uuid=TEST_UUID4,
        passport_uid=TEST_PASSPORT_UID4,
        last_login='2021-12-31T04:00:00+03:00',
    )

    # eater_id3 should be first in the sorted response list
    eater_id3 = create_user(
        personal_email_id=TEST_EMAIL_ID,
        uuid=TEST_UUID3,
        passport_uid=TEST_PASSPORT_UID3,
        last_login='2021-12-31T03:00:00+01:00',
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': TEST_EMAIL_ID},
    )
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json['eaters']) == 3

    assert response_json['eaters'][0]['id'] == str(eater_id3)
    assert response_json['eaters'][1]['id'] == str(eater_id1)
    assert response_json['eaters'][2]['id'] == str(eater_id0)
