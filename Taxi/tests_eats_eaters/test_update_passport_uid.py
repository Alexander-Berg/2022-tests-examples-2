import pytest


async def test_204(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(passport_uid='passportuid1')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': str(eater_id), 'passport_uid': 'new_passportuid1'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    response_json = response.json()
    user['passport_uid'] = 'new_passportuid1'

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_204_find_by_passport_uid(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(passport_uid='passportuid1')
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={
            'passport_uid': user['passport_uid'],
            'with_soft_deleted': False,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': str(eater_id), 'passport_uid': 'new_passportuid1'},
    )
    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={
            'passport_uid': user['passport_uid'],
            'with_soft_deleted': False,
        },
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'new_passportuid1', 'with_soft_deleted': False},
    )
    assert response.status_code == 200
    response_json = response.json()
    user['passport_uid'] = 'new_passportuid1'
    check_users_are_equal(response_json['eater'], user)


async def test_204_with_null(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(passport_uid='passportuid1')
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={
            'passport_uid': user['passport_uid'],
            'with_soft_deleted': False,
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': str(eater_id), 'passport_uid': None},
    )
    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={
            'passport_uid': user['passport_uid'],
            'with_soft_deleted': False,
        },
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )
    assert response.status_code == 200
    response_json = response.json()
    user['passport_uid'] = None
    check_users_are_equal(response_json['eater'], user)


async def test_409(taxi_eats_eaters, create_user):
    create_user(passport_uid='passportuid1')
    eater_id = create_user(
        passport_uid='passportuid2',
        uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6749',
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': str(eater_id), 'passport_uid': 'passportuid1'},
    )

    assert response.status_code == 409


async def test_404(taxi_eats_eaters):
    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': '999', 'passport_uid': 'new_passportuid1'},
    )

    assert response.status_code == 404


async def test_cache(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    create_user(passport_uid='passportuid1')
    eater_id = create_user(
        passport_uid='passportuid2',
        uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6749',
    )
    user = get_user(eater_id)
    user1 = get_user(1)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id', json={'id': '2', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid2', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid1', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user1)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid3', 'with_soft_deleted': True},
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-passport-uid',
        json={'eater_id': '2', 'passport_uid': 'passportuid3'},
    )
    assert response.status_code == 204
    user['passport_uid'] = 'passportuid3'

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id', json={'id': '2', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid2', 'with_soft_deleted': True},
    )
    assert response.status_code == 404

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid1', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user1)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-passport-uid',
        json={'passport_uid': 'passportuid3', 'with_soft_deleted': True},
    )
    response_json = response.json()
    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


@pytest.mark.parametrize(
    'path, requests',
    [
        pytest.param(
            '/v1/eaters/update-passport-uid',
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {
                        'admin_id': '3',
                        'passport_uid': 'new_passport_uid_1',
                    },
                },  # with user_id and admin_id
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'passport_uid': 'new_passport_uid_2'},
                },  # with user_id only
                {
                    'json': {
                        'admin_id': '3',
                        'passport_uid': 'new_passport_uid_3',
                    },
                },  # with admin_id only
                {
                    'json': {'passport_uid': 'new_passport_uid_4'},
                },  # without initiator info (system)
            ],
        ),
    ],
)
async def test_history_after_update(path, requests, update_and_check_history):
    await update_and_check_history(
        path, requests, init_user_data=None, save_history=True,
    )


@pytest.mark.parametrize(
    'path, requests',
    [
        pytest.param(
            '/v1/eaters/update-passport-uid',
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {
                        'admin_id': '3',
                        'passport_uid': 'new_passport_uid_1',
                    },
                },
            ],
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
            [{'json': {'admin_id': '3', 'passport_uid': 'passport_uid_1'}}],
            {'passport_uid': 'passport_uid_1'},
            '/v1/eaters/update-passport-uid',
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
        '/v1/eaters/update-passport-uid',
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
