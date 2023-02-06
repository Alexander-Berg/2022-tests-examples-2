import datetime

import pytest
import pytz


async def test_204_id(
        taxi_eats_eaters,
        taxi_config,
        create_user,
        get_user,
        check_users_are_equal,
        check_history_stq,
        stq,
):
    taxi_config.set_values(
        {'EATS_EATERS_FEATURE_FLAGS': {'save_history': True}},
    )
    eater_id = create_user(banned_at='2020-12-01T10:11:12+00:00')

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    user = get_user(eater_id)
    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert response_json['eater']['banned_at'] == '2020-12-01T10:11:12+00:00'

    datetime_before = datetime.datetime.now(tz=pytz.utc)
    response = await taxi_eats_eaters.post(
        '/v1/eaters/reset-banned-at', json={'eater_id': str(eater_id)},
    )
    datetime_after = datetime.datetime.now(tz=pytz.utc)

    assert response.status_code == 204

    response = await taxi_eats_eaters.post(
        '/v1/eaters/find-by-id',
        json={'id': str(eater_id), 'with_soft_deleted': False},
    )

    response_json = response.json()

    assert response.status_code == 200
    check_users_are_equal(response_json['eater'], user)
    assert 'banned_at' not in response_json['eater']

    updated_user_data = get_user(eater_id)

    assert stq.eater_change_history.times_called == 1
    check_history_stq(
        stq.eater_change_history.next_call(),
        user,
        updated_user_data,
        datetime_before,
        datetime_after,
        expected_initiator_id=None,
        expected_initiator_type='system',
    )


async def test_404(
        taxi_eats_eaters, create_user, get_user, check_users_are_equal,
):

    response = await taxi_eats_eaters.post(
        '/v1/eaters/reset-banned-at', json={'eater_id': '1'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'path, init_data, requests',
    [
        pytest.param(
            '/v1/eaters/reset-banned-at',
            {'banned_at': '2020-12-01T10:11:12+00:00'},
            [
                {
                    'header': {'X-Eats-User': 'user_id=1'},
                    'json': {'admin_id': '3'},
                },
            ],
            id='with user_id and admin_id',
        ),
        pytest.param(
            '/v1/eaters/reset-banned-at',
            {'banned_at': '2020-12-01T10:11:12+00:00'},
            [{'header': {'X-Eats-User': 'user_id=1'}, 'json': {}}],
            id='with user_id only',
        ),
        pytest.param(
            '/v1/eaters/reset-banned-at',
            {'banned_at': '2020-12-01T10:11:12+00:00'},
            [{'json': {'admin_id': '3'}}],
            id='with admin_id only',
        ),
        pytest.param(
            '/v1/eaters/reset-banned-at',
            {'banned_at': '2020-12-01T10:11:12+00:00'},
            [{'json': {}}],
            id='without initiator info (system)',
        ),
    ],
)
async def test_history_after_update(
        path, init_data, requests, update_and_check_history,
):
    await update_and_check_history(
        path, requests, init_user_data=init_data, save_history=True,
    )


@pytest.mark.parametrize(
    'path, init_data, requests',
    [
        pytest.param(
            '/v1/eaters/reset-banned-at',
            {'banned_at': '2020-12-01T10:11:12+00:00'},
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
            [{'json': {'admin_id': '3'}}], {}, '/v1/eaters/reset-banned-at',
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
        '/v1/eaters/reset-banned-at',
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
