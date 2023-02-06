import pytest

HANDLER = '/driver/v1/profile-view/v1/income-order-sounds'
HANDLER_SAVE = '/driver/v1/profile-view/v1/income-order-sounds/save'
INTERNAL_HANDLER = '/internal/v1/income-order-sounds'

HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'parkid',
    'X-YaTaxi-Driver-Profile-Id': 'driverid',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.60 (1234)',
}


ALLOWED_SOUNDS = [
    {'sound_id': 'all_i_want', 'sound_name': 'Все что я хочу на Рождество'},
    {'sound_id': 'snowman', 'sound_name': 'Снеговик'},
    {'sound_id': '3whorses', 'sound_name': 'Три белых коня'},
]


DEFAULT_SOUND = {'sound_id': 'new_order', 'sound_name': 'Новый заказ'}


def fetch_sound_from_db(pgsql, park_id, driver_profile_id):
    cursor = pgsql['driver_profile_view'].cursor()
    cursor.execute(
        'SELECT sound_id '
        'FROM sounds '
        'WHERE park_driver_profile_id = \'{}\''.format(
            park_id + '_' + driver_profile_id,
        ),
    )
    result = [row for row in cursor]
    cursor.close()
    return result


def exp_allowed_order_sounds(force_use_default):
    clauses = [
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'allowed_sounds': [
                    {
                        'sound_id': 'all_i_want',
                        'sound_name': 'all_i_want_for_christmas',
                    },
                    {'sound_id': 'snowman', 'sound_name': 'snowman'},
                    {
                        'sound_id': '3whorses',
                        'sound_name': 'three_white_horses',
                    },
                ],
                'default_sound': {
                    'sound_id': 'new_order',
                    'sound_name': 'new_order_sound_default',
                },
                'force_use_default': force_use_default,
            },
        },
    ]

    return pytest.mark.experiments3(
        is_config=True,
        name='allowed_order_sounds',
        consumers=['driver_profile_view'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
    )


@exp_allowed_order_sounds(False)
async def test_service_sounds_get_default(taxi_driver_profile_view):
    response = await taxi_driver_profile_view.get(HANDLER, headers=HEADERS)
    expected_json = {
        'allowed_sounds': ALLOWED_SOUNDS,
        'chosen_sound': DEFAULT_SOUND,
    }
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'force_use_default',
    [
        pytest.param(False, marks=exp_allowed_order_sounds(False)),
        pytest.param(True, marks=exp_allowed_order_sounds(True)),
    ],
)
@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO sounds
        (park_driver_profile_id, sound_id)
        VALUES ('parkid_driverid', 'all_i_want')
        """,
    ],
)
async def test_service_sounds_get(
        taxi_driver_profile_view, pgsql, force_use_default,
):
    saved_sound = DEFAULT_SOUND if force_use_default else ALLOWED_SOUNDS[0]
    response = await taxi_driver_profile_view.get(HANDLER, headers=HEADERS)
    expected_json = {
        'allowed_sounds': ALLOWED_SOUNDS,
        'chosen_sound': saved_sound,
    }
    assert (
        fetch_sound_from_db(pgsql, 'parkid', 'driverid')[0][0]
        == saved_sound['sound_id']
    )
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO sounds
        (park_driver_profile_id, sound_id)
        VALUES ('parkid_driverid', 'nonexistent_sound')
        """,
    ],
)
@exp_allowed_order_sounds(False)
async def test_service_sounds_get_with_nonexistent_sound(
        taxi_driver_profile_view, pgsql,
):
    response = await taxi_driver_profile_view.get(HANDLER, headers=HEADERS)
    expected_json = {
        'allowed_sounds': ALLOWED_SOUNDS,
        'chosen_sound': DEFAULT_SOUND,
    }
    assert (
        fetch_sound_from_db(pgsql, 'parkid', 'driverid')[0][0]
        == DEFAULT_SOUND['sound_id']
    )
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'sound_id, expected_code', [('3whorses', 200), ('christmastree', 400)],
)
@exp_allowed_order_sounds(False)
async def test_service_sounds_post(
        taxi_driver_profile_view, pgsql, sound_id, expected_code,
):
    response = await taxi_driver_profile_view.post(
        HANDLER_SAVE, headers=HEADERS, json={'sound_id': sound_id},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert (
            fetch_sound_from_db(pgsql, 'parkid', 'driverid')[0][0] == sound_id
        )


@exp_allowed_order_sounds(False)
async def test_service_sounds_post_and_get(taxi_driver_profile_view, pgsql):
    sound_id = 'snowman'
    post_response = await taxi_driver_profile_view.post(
        HANDLER_SAVE, headers=HEADERS, json={'sound_id': sound_id},
    )

    assert post_response.status_code == 200
    assert fetch_sound_from_db(pgsql, 'parkid', 'driverid')[0][0] == sound_id

    get_response = await taxi_driver_profile_view.get(HANDLER, headers=HEADERS)
    expected_json = {
        'allowed_sounds': ALLOWED_SOUNDS,
        'chosen_sound': ALLOWED_SOUNDS[1],
    }
    assert get_response.status_code == 200
    assert get_response.json() == expected_json


@pytest.mark.parametrize(
    'driver_id, enabled, sound_id',
    [
        ('driverid1', True, 'all_i_want.wav'),
        ('driverid1', False, None),
        ('driverid2', True, None),
        ('driverid2', False, None),
    ],
)
@pytest.mark.pgsql(
    'driver_profile_view',
    queries=[
        """
        INSERT INTO sounds
        (park_driver_profile_id, sound_id)
        VALUES
        ('parkid_driverid1', 'all_i_want')
        """,
    ],
)
async def test_return_new_year_sound(
        taxi_driver_profile_view, taxi_config, driver_id, enabled, sound_id,
):
    config = {
        'NEW_YEAR_ORDER_SOUNDS': enabled,
        'NEW_YEAR_SOUNDS_PUSH_EXTENSION': {'extension': 'wav'},
    }
    taxi_config.set_values(config)

    response = await taxi_driver_profile_view.post(
        INTERNAL_HANDLER,
        headers={'Accept-Language': 'ru'},
        json={'park_id': 'parkid', 'driver_profile_id': driver_id},
    )
    assert response.status_code == 200
    if sound_id is None:
        assert not response.json()
    else:
        assert response.json()['sound_id'] == sound_id
