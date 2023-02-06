import copy

import pytest


TASK_NAME = 'communication-sender-parks'
SETTINGS_NAME = 'BLOCKLIST_COMMUNICATIONS_SETTINGS'

CURSOR_QUERY = (
    'SELECT cursors.name, cursors.value FROM'
    f' blocklist.cursors WHERE cursors.name = \'{TASK_NAME}\';'
)

CAR_ID_1 = 'car_id_1'
CAR_ID_2 = 'car_id_2'
CAR_ID_3 = 'car_id_3'
CAR_ID_4 = 'car_id_4'
PARK_ID_1 = 'park-1'
PARK_ID_2 = 'park-2'
PARK_ID_3 = 'park-3'
PARK_ID_4 = 'park-4'
CAR_NUMBER_1 = 'САR_1'
CAR_NUMBER_2 = 'САR_2'
CAR_NUMBER_3 = 'САR_3'
LICENSE_ID_1 = 'license_1'
LICENSE_ID_2 = 'license_2'
DRIVER_ID_1 = 'driver_1'
DRIVER_ID_2 = 'driver_2'
DRIVER_ID_3 = 'driver_3'

DEFAULT_PARK = {
    'id': PARK_ID_1,
    'login': 'login_1',
    'name': 'name_1',
    'is_active': False,
    'city_id': 'city-id-1',
    'locale': 'ru',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'country_id': 'country-id-1',
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}


def _sort_by_park_id(value):
    return sorted(value, key=lambda x: x['park_id'][0]['park_id'])


def _get_park_info(park_id: str):
    park_info = copy.copy(DEFAULT_PARK)
    park_info['id'] = park_id
    return park_info


@pytest.mark.experiments3(filename='exp_communications_localization.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_localization.json'],
    ids=['park_id'],
)
async def test_communications_localization(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        load_json,
        notifications_assert,
):
    park_2 = _get_park_info(PARK_ID_2)
    park_2['locale'] = 'en'

    park_3 = _get_park_info(PARK_ID_3)
    park_3['locale'] = 'kz'

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': DEFAULT_PARK,
            f'{PARK_ID_2}': park_2,
            f'{PARK_ID_3}': park_3,
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_park_id.json'],
    ids=['park_id'],
)
async def test_communications_predicates_park_id(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        load_json,
        notifications_assert,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
            f'{PARK_ID_4}': _get_park_info(PARK_ID_4),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_license_id.json'],
    ids=['license_id'],
)
async def test_communications_predicates_license_id(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        driver_profiles,
        load_json,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {
                    'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_1}',
                    'park_id': PARK_ID_1,
                },
                {
                    'driver_profile_id': f'{PARK_ID_3}_{DRIVER_ID_2}',
                    'park_id': PARK_ID_3,
                },
            ],
            f'{LICENSE_ID_2}': [
                {
                    'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_3}',
                    'park_id': PARK_ID_2,
                },
            ],
        },
    )

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_park_license_id.json'],
    ids=['license_id_park_id'],
)
async def test_communications_predicates_license_id_park_id(
        taxi_blocklist,
        fleet_parks,
        fleet_notifications,
        load_json,
        notifications_assert,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_car_number.json'],
    ids=['car_number'],
)
async def test_communications_predicates_car_number(
        taxi_blocklist,
        fleet_vehicles,
        notifications_assert,
        fleet_parks,
        fleet_notifications,
        load_json,
):

    fleet_vehicles.set_park_cars(
        {
            f'{CAR_NUMBER_1}': [
                {
                    'park_id_car_id': f'{PARK_ID_1}_{CAR_ID_1}',
                    'park_id': PARK_ID_1,
                },
                {
                    'park_id_car_id': f'{PARK_ID_2}_{CAR_ID_2}',
                    'park_id': PARK_ID_2,
                },
            ],
            f'{CAR_NUMBER_2}': [
                {
                    'park_id_car_id': f'{PARK_ID_3}_{CAR_ID_3}',
                    'park_id': PARK_ID_3,
                },
            ],
            f'{CAR_NUMBER_3}': [
                {
                    'park_id_car_id': f'{PARK_ID_4}_{CAR_ID_4}',
                    'park_id': PARK_ID_4,
                },
            ],
        },
    )

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_car_number_park_id.json'],
    ids=['car_number_park_id'],
)
async def test_communications_predicates_car_number_park_id(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        load_json,
        notifications_assert,
):

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='blocklist_communications',
    consumers=['blocklist_communications'],
    clauses=[],
    default_value={
        'message_key': 'blocklist.communications.parks.default_message',
        'title': 'blocklist.communications.parks.default_title',
        'switcher': 'dry_run',
    },
    is_config=True,
)
async def test_communications_dry_run(
        taxi_blocklist, fleet_parks, fleet_notifications, pgsql,
):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 0

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 3

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())

    assert actual_messages == []


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='blocklist_communications',
    consumers=['blocklist_communications'],
    clauses=[],
    default_value={
        'message_key': 'blocklist.communications.parks.default_message',
        'switcher': 'off',
        'title': 'blocklist.communications.parks.default_title',
    },
    is_config=True,
)
async def test_communications_enabled(
        taxi_blocklist, fleet_parks, fleet_notifications, pgsql,
):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 0

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 3

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())

    assert actual_messages == []


@pytest.mark.experiments3(filename='exp_communications_substitutions.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_pd_substitution.json'],
    ids=['substitutions'],
)
async def test_communications_pd_substitution(
        personal,
        taxi_blocklist,
        fleet_parks,
        fleet_notifications,
        load_json,
        taxi_config,
        notifications_assert,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    personal.set_data(
        {
            'driver_licenses': {
                'license_1': 'raw_license_id_1',
                'license_2': 'raw_license_id_2',
            },
        },
    )
    # change config to
    # replace license_id with raw license
    new_config = taxi_config.get(SETTINGS_NAME)
    new_config['communication-sender-parks']['kwargs_to_replace_with_pd'] = [
        'license_id',
    ]
    taxi_config.set_values({SETTINGS_NAME: new_config})
    await taxi_blocklist.invalidate_caches()

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_few_blocks.json'],
    ids=['two_blocks'],
)
async def test_communications_few_blocks(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        driver_profiles,
        load_json,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {
                    'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_1}',
                    'park_id': PARK_ID_1,
                },
            ],
        },
    )

    fleet_parks.set_parks({f'{PARK_ID_1}': _get_park_info(PARK_ID_1)})

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _sort_by_park_id(fleet_notifications.get_messages())
    expect_messages = _sort_by_park_id(load_json(notifications_assert))

    assert actual_messages == expect_messages
