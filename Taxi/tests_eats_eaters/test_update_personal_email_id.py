import pytest


async def test_204_exist_email_id(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(personal_email_id='emailid1')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert (
        response_json['eater']['personal_email_id']
        == user['personal_email_id']
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-personal-email-id',
        json={'eater_id': str(eater_id), 'personal_email_id': 'new_emailid1'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    response_json = response.json()
    user['personal_email_id'] = 'new_emailid1'

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_204_find_by_email_id(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(personal_email_id='emailid1')
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={
            'personal_email_id': user['personal_email_id'],
            'with_soft_deleted': False,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)
    assert (
        response_json['eaters'][0]['personal_email_id']
        == user['personal_email_id']
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-personal-email-id',
        json={'eater_id': str(eater_id), 'personal_email_id': 'new_emailid1'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={
            'personal_email_id': user['personal_email_id'],
            'with_soft_deleted': False,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['eaters']

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-email-id',
        json={'personal_email_id': 'new_emailid1', 'with_soft_deleted': False},
    )

    response_json = response.json()
    user['personal_email_id'] = 'new_emailid1'

    assert response.status_code == 200
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)


async def test_204_no_email_id(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(personal_email_id=None)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert 'personal_email_id' not in response_json['eater'].keys()

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-personal-email-id',
        json={'eater_id': str(eater_id), 'personal_email_id': 'new_emailid1'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()
    user['personal_email_id'] = 'new_emailid1'

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_404(taxi_eats_eaters):

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-personal-email-id',
        json={'eater_id': '1', 'personal_email_id': 'new_emailid1'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'path, requests',
    [
        pytest.param(
            '/v1/eaters/update-personal-email-id',
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {
                        'admin_id': '3',
                        'personal_email_id': 'new_email_id_1',
                    },
                },  # with user_id and admin_id
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'personal_email_id': 'new_email_id_2'},
                },  # with user_id only
                {
                    'json': {
                        'admin_id': '3',
                        'personal_email_id': 'new_email_id_3',
                    },
                },  # with admin_id only
                {
                    'json': {'personal_email_id': 'new_email_id_4'},
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
            '/v1/eaters/update-personal-email-id',
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {
                        'admin_id': '3',
                        'personal_email_id': 'new_email_id_1',
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
            [{'json': {'admin_id': '3', 'personal_email_id': 'email_id_1'}}],
            {'personal_email_id': 'email_id_1'},
            '/v1/eaters/update-personal-email-id',
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
        '/v1/eaters/update-personal-email-id',
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
