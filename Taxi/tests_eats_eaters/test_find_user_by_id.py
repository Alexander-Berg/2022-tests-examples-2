async def test_200(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
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

    eater_id = create_user(
        uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6749',
        passport_uid='999999999999999999999998',
        deactivated_at='2019-12-31T10:59:59+03:00',
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': True},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_404(taxi_eats_eaters, create_user):

    eater_id = create_user(deactivated_at='2019-12-31T10:59:59+03:00')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': '5555', 'with_soft_deleted': True},
    )

    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert response.status_code == 404


async def test_with_nulls(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(
        personal_email_id=None,
        personal_phone_id=None,
        passport_uid=None,
        passport_uid_type=None,
        eater_type=None,
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_400(taxi_eats_eaters):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id', json={'id': '', 'with_soft_deleted': False},
    )
    assert response.status_code == 400
