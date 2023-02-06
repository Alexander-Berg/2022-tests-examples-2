TEST_UUID = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6748'
TEST_UUID2 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6749'
TEST_UUID3 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6750'
TEST_UUID4 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6751'

TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID2 = '999999999999999999999998'
TEST_PASSPORT_UID3 = '999999999999999999999997'
TEST_PASSPORT_UID4 = '999999999999999999999996'

TEST_EMAIL_ID4 = 'emailid4'


async def test_cache_passport_after_id(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        testpoint,
):
    @testpoint('USER_CACHE_MISS')
    def user_cache_miss(data):
        pass

    @testpoint('USER_ID_CACHE_MISS')
    def user_id_cache_miss(data):
        pass

    eater_id = create_user(uuid=TEST_UUID, passport_uid=TEST_PASSPORT_UID)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert user_cache_miss.times_called == 1
    assert user_id_cache_miss.times_called == 0

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(uuid=TEST_UUID2, passport_uid=TEST_PASSPORT_UID2)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': True},
    )

    assert user_cache_miss.times_called == 2
    assert user_id_cache_miss.times_called == 0

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': True},
    )

    assert user_cache_miss.times_called == 2
    assert user_id_cache_miss.times_called == 0

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid'], 'with_soft_deleted': True},
    )

    assert user_cache_miss.times_called == 2
    assert user_id_cache_miss.times_called == 0

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_cache_id_after_passport(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        testpoint,
):
    @testpoint('USER_CACHE_MISS')
    def user_cache_miss(data):
        pass

    @testpoint('USER_ID_CACHE_MISS')
    def user_id_cache_miss(data):
        pass

    eater_id = create_user(uuid=TEST_UUID3, passport_uid=TEST_PASSPORT_UID3)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid'], 'with_soft_deleted': True},
    )

    assert user_cache_miss.times_called == 0
    assert user_id_cache_miss.times_called == 1

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert user_cache_miss.times_called == 0
    assert user_id_cache_miss.times_called == 1

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_cache_id_and_all_id(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        testpoint,
):
    @testpoint('USER_CACHE_MISS')
    def user_cache_miss(data):
        pass

    @testpoint('USER_ID_CACHE_MISS')
    def user_id_cache_miss(data):
        pass

    eater_id = create_user(uuid=TEST_UUID4, passport_uid=TEST_PASSPORT_UID4)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid'], 'with_soft_deleted': True},
    )

    assert user_cache_miss.times_called == 0
    assert user_id_cache_miss.times_called == 1

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': user['uuid']},
    )

    assert user_cache_miss.times_called == 0
    assert user_id_cache_miss.times_called == 1

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert user_cache_miss.times_called == 0
    assert user_id_cache_miss.times_called == 1

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_not_found_dont_cache(taxi_eats_eaters, testpoint):
    @testpoint('USER_CACHE_MISS')
    def user_cache_miss(data):
        pass

    @testpoint('USER_ID_CACHE_MISS')
    def user_id_cache_miss(data):
        pass

    test_eater_id = '1'
    test_uuid = TEST_UUID4
    test_passport_uid = TEST_PASSPORT_UID4

    user_cache_miss_counter = 0
    user_id_cache_miss_counter = 0

    for _ in range(3):
        response = await taxi_eats_eaters.post(
            '/v1/eaters/find-by-id',
            json={'id': test_eater_id, 'with_soft_deleted': False},
        )
        user_cache_miss_counter += 1
        assert user_cache_miss.times_called == user_cache_miss_counter
        assert user_id_cache_miss.times_called == user_id_cache_miss_counter
        assert response.status_code == 404

        requests = [
            {'url': '/v1/eaters/find-by-uuid', 'json': {'uuid': test_uuid}},
            {
                'url': '/v1/eaters/find-by-passport-uid',
                'json': {'passport_uid': test_passport_uid},
            },
        ]
        for request in requests:
            response = await taxi_eats_eaters.post(
                request['url'], json=request['json'],
            )
            user_id_cache_miss_counter += 1
            assert user_cache_miss.times_called == user_cache_miss_counter
            assert (
                user_id_cache_miss.times_called == user_id_cache_miss_counter
            )
            assert response.status_code == 404
