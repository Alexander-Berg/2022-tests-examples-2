import pytest

TEST_DEFAULT_LIMIT = 50
TEST_DEACTIVATED_AT = '2019-12-31T10:59:59+03:00'

TEST_USERS_COUNT = 10
TEST_ACTIVE_USERS_COUNT = 9
TEST_HALF_USERS_COUNT = 5
TEST_DEACTIVATED_EATER_ID = 6
TEST_AFTER = '5'


async def test_200(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        check_response_pagination,
):
    eater_id = create_user()

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids', json={'ids': [str(eater_id)]},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_response_pagination(response_json['pagination'])
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(
        uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6749',
        passport_uid='999999999999999999999998',
        deactivated_at=TEST_DEACTIVATED_AT,
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids',
        json={'ids': [str(eater_id)], 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_response_pagination(response_json['pagination'])
    check_users_are_equal(response_json['eaters'][0], user)


async def test_not_found(
        taxi_eats_eaters, create_user, check_response_pagination,
):
    eater_id = create_user(deactivated_at=TEST_DEACTIVATED_AT)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids',
        json={'ids': ['5555'], 'with_soft_deleted': True},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_response_pagination(response_json['pagination'])
    assert not response_json['eaters']

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids', json={'ids': [str(eater_id)]},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_response_pagination(response_json['pagination'])
    assert not response_json['eaters']


async def test_with_nulls(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        check_response_pagination,
):
    eater_id = create_user(
        personal_email_id=None,
        personal_phone_id=None,
        passport_uid=None,
        passport_uid_type=None,
        eater_type=None,
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids', json={'ids': [str(eater_id)]},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_response_pagination(response_json['pagination'])
    check_users_are_equal(response_json['eaters'][0], user)


@pytest.mark.pgsql('eats_eaters', files=['init_users.sql'])
@pytest.mark.parametrize(
    'with_soft_deleted, request_pagination, expected_eaters_count, '
    'expected_has_more, expected_limit, expected_after',
    [
        pytest.param(
            True,
            None,
            TEST_USERS_COUNT,
            False,
            TEST_DEFAULT_LIMIT,
            None,
            id='no pagination, with soft deleted',
        ),
        pytest.param(
            False,
            None,
            TEST_ACTIVE_USERS_COUNT,
            False,
            TEST_DEFAULT_LIMIT,
            None,
            id='no pagination, no soft deleted',
        ),
        pytest.param(
            True,
            {'limit': TEST_ACTIVE_USERS_COUNT},
            TEST_ACTIVE_USERS_COUNT,
            True,
            TEST_ACTIVE_USERS_COUNT,
            None,
            id='limit, no after, with soft deleted',
        ),
        pytest.param(
            False,
            {'limit': TEST_ACTIVE_USERS_COUNT},
            TEST_ACTIVE_USERS_COUNT,
            False,
            TEST_ACTIVE_USERS_COUNT,
            None,
            id='limit, no after, no soft deleted',
        ),
        pytest.param(
            True,
            {'limit': TEST_HALF_USERS_COUNT, 'after': TEST_AFTER},
            TEST_HALF_USERS_COUNT,
            False,
            TEST_HALF_USERS_COUNT,
            TEST_AFTER,
            id='second half, with soft deleted',
        ),
        pytest.param(
            False,
            {'limit': TEST_HALF_USERS_COUNT, 'after': TEST_AFTER},
            TEST_HALF_USERS_COUNT - 1,
            False,
            TEST_HALF_USERS_COUNT,
            TEST_AFTER,
            id='second half, no soft deleted',
        ),
        pytest.param(
            True,
            {'limit': TEST_HALF_USERS_COUNT - 1, 'after': TEST_AFTER},
            TEST_HALF_USERS_COUNT - 1,
            True,
            TEST_HALF_USERS_COUNT - 1,
            TEST_AFTER,
            id='has more, with soft deleted',
        ),
        pytest.param(
            False,
            {'limit': TEST_HALF_USERS_COUNT - 1, 'after': TEST_AFTER},
            TEST_HALF_USERS_COUNT - 1,
            False,
            TEST_HALF_USERS_COUNT - 1,
            TEST_AFTER,
            id='no has more, no soft deleted',
        ),
    ],
)
async def test_pagination(
        taxi_eats_eaters,
        get_user,
        check_users_are_equal,
        check_response_pagination,
        with_soft_deleted,
        request_pagination,
        expected_eaters_count,
        expected_has_more,
        expected_limit,
        expected_after,
):
    eater_ids = range(1, TEST_USERS_COUNT + 1)
    str_eater_ids = [str(eater_id) for eater_id in eater_ids]

    users = {eater_id: get_user(eater_id) for eater_id in eater_ids}

    data = {'ids': str_eater_ids, 'with_soft_deleted': with_soft_deleted}
    if request_pagination is not None:
        data['pagination'] = request_pagination
    response = await taxi_eats_eaters.post('/v1/eaters/find-by-ids', json=data)

    response_json = response.json()
    response_eaters = {}
    for eater in response_json['eaters']:
        eater_id = int(eater['id'])
        response_eaters[eater_id] = eater

    assert response.status_code == 200
    check_response_pagination(
        response_pagination=response_json['pagination'],
        expected_has_more=expected_has_more,
        expected_limit=expected_limit,
        expected_after=expected_after,
    )
    assert len(response_eaters) == expected_eaters_count

    eater_id_from = 1
    if expected_after:
        eater_id_from = int(expected_after) + 1
    eater_id_to = eater_id_from + expected_eaters_count
    for eater_id in range(eater_id_from, eater_id_to):
        if not with_soft_deleted and eater_id == TEST_DEACTIVATED_EATER_ID:
            assert users[eater_id]
            assert eater_id not in response_eaters
        else:
            check_users_are_equal(response_eaters[eater_id], users[eater_id])
