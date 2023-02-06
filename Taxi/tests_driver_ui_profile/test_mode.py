# flake8: noqa IS001
import datetime
from typing import List, Tuple

import pytest


def _insert_named_entities(names: List[str], table_name: str) -> str:
    return f'INSERT INTO {table_name} (name) VALUES ' + ', '.join(
        map(lambda x: f'(\'{x}\')', names),
    )


class Driver:
    def __init__(self, identifier: int, park_id: str, driver_profile_id: str):
        self.identifier = identifier
        self.park_id = park_id
        self.driver_profile_id = driver_profile_id


def _gen_drivers(num: int) -> List[Driver]:
    return list(
        map(lambda x: Driver(x, f'park_id{x}', f'uuid{x}'), range(1, num + 1)),
    )


def _insert_drivers(drivers: List[Driver]) -> str:
    return (
        f'INSERT INTO state.drivers (id, park_id, driver_profile_id) VALUES '
        + ', '.join(
            map(
                lambda x: f'({x.identifier}, \'{x.park_id}\', '
                f'\'{x.driver_profile_id}\')',
                drivers,
            ),
        )
    )


class Profile:
    def __init__(
            self,
            driver_id: int,
            display_mode_id: int,
            display_profile_id: int,
    ):
        self.driver_id = driver_id
        self.display_mode_id = display_mode_id
        self.display_profile_id = display_profile_id


def _insert_profiles(profiles: List[Profile]) -> str:
    return (
        'INSERT INTO state.profiles '
        '(driver_id, display_mode_id, display_profile_id) VALUES '
        + ', '.join(
            map(
                lambda x: f'({x.driver_id}, {x.display_mode_id}, '
                f'{x.display_profile_id})',
                profiles,
            ),
        )
    )


def _reset_sequence(name: str) -> str:
    return f'SELECT setval(\'{name}\', 1, false);'


def _reset_all_sequences() -> List[str]:
    return [
        _reset_sequence('state.display_profiles_id_seq'),
        _reset_sequence('state.display_modes_id_seq'),
        _reset_sequence('state.drivers_id_seq'),
    ]


async def _get(taxi_driver_ui_profile, driver: Driver, concern: str):
    response = await taxi_driver_ui_profile.get(
        'v1/mode',
        params={
            'park_id': driver.park_id,
            'driver_profile_id': driver.driver_profile_id,
            'concern': concern,
        },
    )
    assert response.status_code == 200

    return response.json()


async def _post(taxi_driver_ui_profile, driver: Driver, mode: Tuple[str, str]):
    response = await taxi_driver_ui_profile.post(
        'v1/mode',
        json={
            'park_id': driver.park_id,
            'driver_profile_id': driver.driver_profile_id,
            'display_mode': mode[0],
            'display_profile': mode[1],
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    DRIVER_UI_PROFILE_DEFAULT_UI_MODE={
        'display_mode': 'orders',
        'display_profile': 'orders_profile',
    },
)
@pytest.mark.pgsql(
    'driver_ui_profile',
    queries=[
        _reset_all_sequences(),
        _insert_named_entities(['eda', 'driver_fix'], 'state.display_modes'),
        _insert_named_entities(
            ['eda_on_foot', 'eda_on_bike', 'driver_fix_1'],
            'state.display_profiles',
        ),
        _insert_drivers(_gen_drivers(5)),
        _insert_profiles(
            [Profile(1, 1, 1), Profile(2, 1, 2), Profile(3, 2, 3)],
        ),
    ],
)
@pytest.mark.parametrize(
    'driver_id, expected_modes',
    [
        (0, ('eda', 'eda_on_foot')),
        (1, ('eda', 'eda_on_bike')),
        (2, ('driver_fix', 'driver_fix_1')),
        (3, ('orders', 'orders_profile')),
        (4, ('orders', 'orders_profile')),
    ],
)
async def test_get(taxi_driver_ui_profile, driver_id, expected_modes):
    driver = _gen_drivers(6)[driver_id]

    response = await _get(taxi_driver_ui_profile, driver, 'cached')
    assert response['display_mode'] == expected_modes[0]
    assert response['display_profile'] == expected_modes[1]


def _get_display_settings(db, driver: Driver) -> Tuple[str, str]:
    cursor = db.cursor()
    cursor.execute(
        'SELECT display_modes.name, display_profiles.name from '
        'state.profiles inner join state.drivers on driver_id=drivers.id '
        'inner join state.display_modes on display_mode_id=display_modes.id '
        'inner join state.display_profiles '
        'on display_profile_id=display_profiles.id '
        f'where park_id=\'{driver.park_id}\' and '
        f'driver_profile_id=\'{driver.driver_profile_id}\'',
    )

    rows = list(row for row in cursor)
    assert len(rows) == 1
    return rows[0][0], rows[0][1]


@pytest.mark.pgsql(
    'driver_ui_profile',
    queries=[
        _reset_all_sequences(),
        _insert_named_entities(['eda'], 'state.display_modes'),
        _insert_named_entities(
            ['eda_on_foot', 'eda_on_bike'], 'state.display_profiles',
        ),
        _insert_drivers(_gen_drivers(4)),
        _insert_profiles([Profile(1, 1, 1)]),
    ],
)
@pytest.mark.parametrize(
    'driver_id, mode_to_insert',
    [
        pytest.param(
            0, ('eda', 'eda_on_bike'), id='change existing to existing',
        ),
        pytest.param(
            0,
            ('eda', 'eda_on_drone'),
            id='change existing to unknown profile',
        ),
        pytest.param(
            0,
            ('apteka', 'apteka_on_boat'),
            id='change existing to unknown mode and profile',
        ),
        pytest.param(
            1, ('not_that', 'creative'), id='new driver new mode new profile',
        ),
    ],
)
async def test_post(taxi_driver_ui_profile, driver_id, mode_to_insert, pgsql):
    driver = _gen_drivers(4)[driver_id]
    await _post(taxi_driver_ui_profile, driver, mode_to_insert)

    db = pgsql['driver_ui_profile']
    assert _get_display_settings(db, driver) == mode_to_insert


def _insert_profile(db, driver: Driver, mode: Tuple[str, str]):
    cursor = db.cursor()
    cursor.execute(
        'insert into state.display_modes (name)'
        f'values (\'{mode[0]}\') on conflict do nothing',
    )
    cursor.execute(
        'insert into state.display_profiles (name)'
        f'values (\'{mode[1]}\') on conflict do nothing',
    )
    cursor.execute(
        'insert into state.drivers (park_id, driver_profile_id)'
        f'values (\'{driver.park_id}\', '
        f'\'{driver.driver_profile_id}\')',
    )
    cursor.execute(
        'insert into state.profiles '
        '(driver_id, display_mode_id, display_profile_id)'
        'select drivers.id, display_modes.id, display_profiles.id '
        'from state.drivers, state.display_modes, state.display_profiles '
        f'where drivers.park_id=\'{driver.park_id}\' '
        f'and drivers.driver_profile_id=\'{driver.driver_profile_id}\' '
        f'and display_modes.name=\'{mode[0]}\' '
        f'and display_profiles.name=\'{mode[1]}\'',
    )


@pytest.mark.parametrize(
    'concern',
    ['cached', 'sync', 'urgent'],
    ids=['from cache', 'from slave', 'from master'],
)
async def test_get_new_entry(taxi_driver_ui_profile, concern, pgsql):
    await taxi_driver_ui_profile.invalidate_caches()
    driver = _gen_drivers(1)[0]
    display_mode = 'aba'
    display_profile = 'caba'
    mode = (display_mode, display_profile)
    db = pgsql['driver_ui_profile']

    _insert_profile(db, driver, mode)

    response = await _get(taxi_driver_ui_profile, driver, concern)

    if concern in ['sync', 'urgent']:
        assert response['display_mode'] == display_mode
        assert response['display_profile'] == display_profile
    else:
        assert (
            response['display_mode'] == response['display_profile'] == 'orders'
        )

    await taxi_driver_ui_profile.invalidate_caches(clean_update=False)

    response = await _get(taxi_driver_ui_profile, driver, concern)

    assert response['display_mode'] == display_mode
    assert response['display_profile'] == display_profile


async def test_big(taxi_driver_ui_profile):
    drivers_count = 10
    drivers = _gen_drivers(10)
    modes = [(f'mode{i}', f'profile{i}') for i in range(drivers_count)]

    for driver, mode in zip(drivers, modes):
        await _post(taxi_driver_ui_profile, driver, mode)

    await taxi_driver_ui_profile.invalidate_caches(clean_update=False)

    for driver, mode in zip(drivers, modes):
        response = await _get(taxi_driver_ui_profile, driver, 'cached')
        assert response['display_mode'] == mode[0]
        assert response['display_profile'] == mode[1]

    modes = [
        (f'mode{i}', f'profile{i}')
        for i in range(drivers_count, drivers_count * 2)
    ]

    for driver, mode in zip(drivers, modes):
        await _post(taxi_driver_ui_profile, driver, mode)

    await taxi_driver_ui_profile.invalidate_caches(clean_update=False)
    await taxi_driver_ui_profile.invalidate_caches(clean_update=False)

    for driver, mode in zip(drivers, modes):
        response = await _get(taxi_driver_ui_profile, driver, 'cached')
        assert response['display_mode'] == mode[0]
        assert response['display_profile'] == mode[1]
