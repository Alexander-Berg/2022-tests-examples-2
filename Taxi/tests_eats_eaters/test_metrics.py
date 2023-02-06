TEST_UUID = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6748'
TEST_UUID2 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6749'
TEST_UUID3 = '5a30b72e-b7e7-4ac5-90b7-7da5cedb6750'

TEST_PASSPORT_UID = '999999999999999999999999'
TEST_PASSPORT_UID2 = '999999999999999999999998'
TEST_PASSPORT_UID3 = '999999999999999999999997'

TEST_PHONE_ID = 'phoneid1'
TEST_PHONE_ID2 = 'phoneid2'
TEST_PHONE_ID3 = 'phoneid3'

TEST_EMAIL_ID = 'emailid1'
TEST_EMAIL_ID2 = 'emailid2'
TEST_EMAIL_ID3 = 'emailid3'


async def test_metric_find_by_id(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user()

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(uuid=TEST_UUID2, passport_uid=TEST_PASSPORT_UID2)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(uuid=TEST_UUID3, passport_uid=TEST_PASSPORT_UID3)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-id',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_ids(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user()

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids',
        json={'ids': [str(eater_id)], 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(uuid=TEST_UUID2, passport_uid=TEST_PASSPORT_UID2)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids',
        json={'ids': [str(eater_id)], 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(uuid=TEST_UUID3, passport_uid=TEST_PASSPORT_UID3)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-ids',
        json={'ids': [str(eater_id)], 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-ids',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_passport_uid(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user()
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(uuid=TEST_UUID2, passport_uid=TEST_PASSPORT_UID2)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(uuid=TEST_UUID3, passport_uid=TEST_PASSPORT_UID3)

    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': user['passport_uid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-passport-uid',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_passport_uids(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user()
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uids',
        json={'passport_uids': [user['passport_uid']]},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(uuid=TEST_UUID2, passport_uid=TEST_PASSPORT_UID2)
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uids',
        json={'passport_uids': [user['passport_uid']]},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(uuid=TEST_UUID3, passport_uid=TEST_PASSPORT_UID3)

    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uids',
        json={'passport_uids': [user['passport_uid']]},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eaters'][0], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-passport-uids',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_phone_id(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user(
        personal_phone_id=TEST_PHONE_ID,
        uuid=TEST_UUID,
        passport_uid=TEST_PASSPORT_UID,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={'personal_phone_id': user['personal_phone_id']},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(
        personal_phone_id=TEST_PHONE_ID2,
        uuid=TEST_UUID2,
        passport_uid=TEST_PASSPORT_UID2,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={'personal_phone_id': user['personal_phone_id']},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)

    eater_id = create_user(
        personal_phone_id=TEST_PHONE_ID3,
        uuid=TEST_UUID3,
        passport_uid=TEST_PASSPORT_UID3,
    )

    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={'personal_phone_id': user['personal_phone_id']},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-personal-phone-id',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_email_id(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID,
        uuid=TEST_UUID,
        passport_uid=TEST_PASSPORT_UID,
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

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID2,
        uuid=TEST_UUID2,
        passport_uid=TEST_PASSPORT_UID2,
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

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID3,
        uuid=TEST_UUID3,
        passport_uid=TEST_PASSPORT_UID3,
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

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-personal-email-id',
    )

    assert metric['timings']['p100'] > 0


async def test_metric_find_by_uuid(
        taxi_eats_eaters,
        create_user,
        get_user,
        check_users_are_equal,
        taxi_eats_eaters_monitor,
):

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID,
        uuid=TEST_UUID,
        passport_uid=TEST_PASSPORT_UID,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': user['uuid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID2,
        uuid=TEST_UUID2,
        passport_uid=TEST_PASSPORT_UID2,
    )
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': user['uuid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    eater_id = create_user(
        personal_email_id=TEST_EMAIL_ID3,
        uuid=TEST_UUID3,
        passport_uid=TEST_PASSPORT_UID3,
    )

    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-uuid', json={'uuid': user['uuid']},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    metric = await taxi_eats_eaters_monitor.get_metric(
        'pgsql-eats-eaters-find-by-uuid',
    )

    assert metric['timings']['p100'] > 0
