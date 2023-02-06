import pytest


@pytest.mark.now('2020-12-16T12:00:00+00:00')
async def test_204_ban(
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

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-banned-at',
        json={'eater_id': str(eater_id), 'ban_reason': 'нехороший человек'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)
    assert response_json['eater']['banned_at'] == '2020-12-16T12:00:00+00:00'


@pytest.mark.now('2020-12-16T12:00:00+00:00')
async def test_204_double_ban(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):
    eater_id = create_user(banned_at='2019-11-15T12:00:00+00:00')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert response_json['eater']['banned_at'] == '2019-11-15T12:00:00+00:00'

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-banned-at',
        json={'eater_id': str(eater_id), 'ban_reason': 'нехороший человек'},
    )

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    assert response.status_code == 200
    response_json = response.json()
    check_users_are_equal(response_json['eater'], user)
    assert response_json['eater']['banned_at'] == '2020-12-16T12:00:00+00:00'


async def test_404(taxi_eats_eaters):

    response = await taxi_eats_eaters.post(
        '/v1/eaters/update-banned-at', json={'eater_id': '1'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'path, requests',
    [
        pytest.param(
            '/v1/eaters/update-banned-at',
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'admin_id': '3', 'ban_reason': 'хулиган'},
                },  # with user_id and admin_id
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'ban_reason': 'плохой человек'},
                },  # with user_id only
                {
                    'json': {'admin_id': '3', 'ban_reason': 'редиска'},
                },  # with admin_id only
                {
                    'json': {'ban_reason': 'ban_reason'},
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
            '/v1/eaters/update-banned-at',
            [
                {
                    'header': {
                        'X-Eats-User': 'user_id=1',
                        'X-YaTaxi-User': 'eats_user_id=2',
                    },
                    'json': {'admin_id': '3', 'ban_reason': 'хулиган'},
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
                        'ban_reason': 'плохой человек',
                        'banned_at': '2020-12-16T12:00:00+00:00',
                    },
                },
            ],
            {
                'banned_at': '2020-12-16T12:00:00+00:00',
                'ban_reason': 'плохой человек',
            },
            '/v1/eaters/update-banned-at',
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
        '/v1/eaters/update-banned-at',
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
