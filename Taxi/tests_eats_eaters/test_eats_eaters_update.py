import pytest


TEST_EATER_ID = '1200373'
TEST_CONFLICT_EATER_ID = '1200383'
TEST_DATE_TIME = '2020-02-01T01:00:00Z'
TEST_DATE_TIME_BEFORE = '2020-02-01T00:00:00Z'
TEST_DATE_TIME_AFTER = '2020-02-01T02:00:00Z'
TEST_USER_NAME = 'STQ User'
TEST_PASS_UID = 'pass_uid'
TEST_UUID1 = '5a30b72e-b5e7-4af5-50b7-7da5cadb6748'
TEST_UUID2 = '5a30b72e-b5e7-4af5-50b7-7da5cadb6749'

TEST_CORE_USER = {
    'id': TEST_EATER_ID,
    'uuid': TEST_UUID1,
    'created_at': TEST_DATE_TIME,
    'updated_at': TEST_DATE_TIME,
    'client_type': 'common',
    'type': 'native',
    'passport_uid': TEST_PASS_UID,
    'passport_uid_type': 'portal',
    'personal_email_id': 'email_id',
    'personal_phone_id': 'phone_id',
    'name': TEST_USER_NAME,
}


async def test_eater_create_ok(mockserver, stq_runner, get_user):
    @mockserver.json_handler('/eats-core-eater-service/service-find-by-id')
    def _mock_core(request):
        assert request.json == {'id': TEST_EATER_ID}
        return mockserver.make_response(
            json={'eater': TEST_CORE_USER}, status=200,
        )

    user = get_user(TEST_EATER_ID)
    assert not user

    await stq_runner.eats_eaters_updates.call(
        task_id=TEST_EATER_ID, args=[{'$date': TEST_DATE_TIME}],
    )

    user = get_user(TEST_EATER_ID)
    assert user['id'] == int(TEST_EATER_ID)
    assert user['name'] == TEST_USER_NAME


@pytest.mark.parametrize(
    (
        'updated_at,is_core_outdated,'
        'initial_deactivated_at,expected_deactivated_at'
    ),
    [
        pytest.param(TEST_DATE_TIME_BEFORE, False, None, None),
        pytest.param(TEST_DATE_TIME_BEFORE, False, None, TEST_DATE_TIME_AFTER),
        pytest.param(TEST_DATE_TIME, False, TEST_DATE_TIME_AFTER, None),
        pytest.param(
            TEST_DATE_TIME, False, TEST_DATE_TIME_AFTER, TEST_DATE_TIME_AFTER,
        ),
        pytest.param(TEST_DATE_TIME_AFTER, False, None, None),
    ],
)
async def test_eater_update(
        mockserver,
        stq_runner,
        create_user,
        format_datetime,
        get_user,
        updated_at,
        is_core_outdated,
        initial_deactivated_at,
        expected_deactivated_at,
):
    @mockserver.json_handler('/eats-core-eater-service/service-find-by-id')
    def _mock_core(request):
        _user = TEST_CORE_USER
        _user['id'] = request.json['id']
        _user['deactivated_at'] = expected_deactivated_at

        return mockserver.make_response(json={'eater': _user}, status=200)

    eater_id = create_user(
        updated_at=updated_at, deactivated_at=initial_deactivated_at,
    )

    user = get_user(eater_id)
    assert user['id'] == eater_id
    assert user['name'] != TEST_USER_NAME

    await stq_runner.eats_eaters_updates.call(
        task_id=str(eater_id), args=[{'$date': TEST_DATE_TIME}],
    )

    user = get_user(eater_id)
    assert user['id'] == eater_id

    if is_core_outdated:
        assert user['name'] != TEST_USER_NAME
        assert (not initial_deactivated_at and not user['deactivated_at']) or (
            initial_deactivated_at
            and format_datetime(user['deactivated_at'], 'UTC')[:19]
            == initial_deactivated_at[:19]
        )
    else:
        assert user['name'] == TEST_USER_NAME
        assert (
            (not expected_deactivated_at and not user['deactivated_at'])
            or (
                expected_deactivated_at
                and format_datetime(user['deactivated_at'], 'UTC')[:19]
                == expected_deactivated_at[:19]
            )
        )


@pytest.mark.parametrize(
    'status_code,body,headers,',
    [
        pytest.param(
            404,
            {'message': 'eater not found', 'code': 'eater_not_found'},
            {'X-YaTaxi-Error-Code': 'eater_not_found'},
        ),
        pytest.param(500, {}, {}),
    ],
)
async def test_eater_not_found(
        mockserver, stq_runner, status_code, body, headers,
):
    @mockserver.json_handler('/eats-core-eater-service/service-find-by-id')
    def _mock_core(request):
        assert request.json == {'id': TEST_EATER_ID}
        return mockserver.make_response(
            json=body, status=status_code, headers=headers,
        )

    await stq_runner.eats_eaters_updates.call(
        task_id=TEST_EATER_ID,
        args=[{'$date': TEST_DATE_TIME}],
        expect_fail=(status_code == 500),
    )


@pytest.mark.parametrize(
    'is_update,', [pytest.param(False), pytest.param(True)],
)
async def test_eater_passport_uid_duplicate(
        mockserver, stq_runner, create_user_with_id, get_user, is_update,
):
    @mockserver.json_handler('/eats-core-eater-service/service-find-by-id')
    def _mock_core(request):
        eater = TEST_CORE_USER
        eater['id'] = request.json['id']
        if TEST_CONFLICT_EATER_ID == request.json['id']:
            eater['uuid'] = TEST_UUID2
            eater['passport_uid'] = None
        else:
            eater['uuid'] = TEST_UUID1
            eater['passport_uid'] = TEST_PASS_UID

        return mockserver.make_response(json={'eater': eater}, status=200)

    conflict_eater_id = create_user_with_id(
        TEST_CONFLICT_EATER_ID, uuid=TEST_UUID2, passport_uid=TEST_PASS_UID,
    )
    print('Conflict eater id', conflict_eater_id)
    eater_with_passport = get_user(conflict_eater_id)
    assert eater_with_passport['id'] == conflict_eater_id
    assert eater_with_passport['uuid'] == TEST_UUID2
    assert eater_with_passport['passport_uid'] == TEST_PASS_UID

    # data preparation
    eater_id = TEST_EATER_ID
    if is_update:
        eater_id = create_user_with_id(
            TEST_EATER_ID, uuid=TEST_UUID1, passport_uid='',
        )

    eater_to_update = get_user(eater_id)
    if is_update:
        assert eater_to_update['id'] == eater_id
    else:
        assert not eater_to_update

    await stq_runner.eats_eaters_updates.call(
        task_id=str(eater_id), args=[{'$date': TEST_DATE_TIME}],
    )

    # data check
    eater_to_update = get_user(eater_id)
    assert eater_to_update['passport_uid'] == TEST_PASS_UID

    eater_with_passport = get_user(conflict_eater_id)
    assert not eater_with_passport['passport_uid']
