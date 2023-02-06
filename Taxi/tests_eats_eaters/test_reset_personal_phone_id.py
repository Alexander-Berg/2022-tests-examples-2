import pytest


async def test_204_id(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(personal_phone_id='phoneid1')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert (
        response_json['eater']['personal_phone_id']
        == user['personal_phone_id']
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/reset-personal-phone-id', json={'eater_id': str(eater_id)},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()
    user['personal_phone_id'] = None

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_204_phone_id(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(personal_phone_id='phoneid1')
    user = get_user(eater_id)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={
            'personal_phone_id': user['personal_phone_id'],
            'with_soft_deleted': False,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['eaters']) == 1
    check_users_are_equal(response_json['eaters'][0], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/reset-personal-phone-id', json={'eater_id': str(eater_id)},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-personal-phone-id',
        json={
            'personal_phone_id': user['personal_phone_id'],
            'with_soft_deleted': False,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['eaters']


async def test_404(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):

    response = await taxi_eats_eaters.post(
        '/v1/eaters/reset-personal-phone-id', json={'eater_id': '1'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'path, init_data, requests',
    [
        pytest.param(
            '/v1/eaters/reset-personal-phone-id',
            {'personal_phone_id': 'phone_id'},
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'admin_id': '3'},
                },
            ],
            id='with user_id and admin_id',
        ),
        pytest.param(
            '/v1/eaters/reset-personal-phone-id',
            {'personal_phone_id': 'phone_id'},
            [{'header': {'X-Eats-User': 'user_id=1'}, 'json': {}}],
            id='with user_id only',
        ),
        pytest.param(
            '/v1/eaters/reset-personal-phone-id',
            {'personal_phone_id': 'phone_id'},
            [{'json': {'admin_id': '3'}}],
            id='with admin_id only',
        ),
        pytest.param(
            '/v1/eaters/reset-personal-phone-id',
            {'personal_phone_id': 'phone_id'},
            [{'json': {}}],
            id='without initiator info (system)',
        ),
    ],
)
async def test_history_after_update(
        path, init_data, requests, update_and_check_history,
):
    await update_and_check_history(
        path=path,
        requests=requests,
        init_user_data=init_data,
        save_history=True,
    )


@pytest.mark.parametrize(
    'path, init_data, requests',
    [
        pytest.param(
            '/v1/eaters/reset-personal-phone-id',
            {'personal_phone_id': 'phone_id'},
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {'admin_id': '3'},
                },
            ],
            id='with user_id and admin_id',
        ),
    ],
)
async def test_update_without_save_history(
        path, init_data, requests, update_and_check_history,
):
    await update_and_check_history(
        path, requests, init_user_data=init_data, save_history=False,
    )


@pytest.mark.parametrize(
    'requests, init_data, path',
    [
        pytest.param(
            [{'json': {'admin_id': '3'}}],
            {},
            '/v1/eaters/reset-personal-phone-id',
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
        '/v1/eaters/reset-personal-phone-id',
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
