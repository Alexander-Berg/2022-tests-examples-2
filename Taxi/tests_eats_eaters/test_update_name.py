import pytest


async def test_204(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(eater_name='Василий Пупкин')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-name',
        json={'eater_id': str(eater_id), 'name': 'Иванов Иван'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    response_json = response.json()
    user['name'] = 'Иванов Иван'

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)


async def test_404(taxi_eats_eaters):

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-name',
        json={'eater_id': '1', 'name': 'Иванов Иван'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'path, requests',
    [
        pytest.param(
            '/v1/eaters/update-name',
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {
                        'admin_id': '3',
                        'name': 'Иван Федорович Крузенштерн',
                    },
                },  # with user_id and admin_id
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'name': 'name_2'},
                },  # with user_id only
                {
                    'json': {'admin_id': '3', 'name': 'name_3'},
                },  # with admin_id only
                {
                    'json': {'name': 'name_4'},
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
            '/v1/eaters/update-name',
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {
                        'admin_id': '3',
                        'name': 'Иван Федорович Крузенштерн',
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
            [
                {
                    'json': {
                        'admin_id': '3',
                        'name': 'Иван Федорович Крузенштерн',
                    },
                },
            ],
            {'eater_name': 'Иван Федорович Крузенштерн'},
            '/v1/eaters/update-name',
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
        '/v1/eaters/update-name',
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
