import pytest

TASK_NAME = 'communication-sender-drivers'
SETTINGS_NAME = 'BLOCKLIST_COMMUNICATIONS_SETTINGS'

CURSOR_QUERY = (
    'SELECT cursors.name, cursors.value FROM'
    f' blocklist.cursors WHERE cursors.name = \'{TASK_NAME}\';'
)

CAR_ID_1 = 'car_id_1'
CAR_ID_2 = 'car_id_2'
CAR_ID_3 = 'car_id_3'
CAR_ID_4 = 'car_id_4'
PARK_ID_1 = 'park_1'
PARK_ID_2 = 'park_2'
PARK_ID_3 = 'park_3'
PARK_ID_4 = 'park_4'
CAR_NUMBER_1 = 'САR_1'
CAR_NUMBER_2 = 'САR_2'
CAR_NUMBER_3 = 'САR_3'
LICENSE_ID_1 = 'license_1'
LICENSE_ID_2 = 'license_2'
DRIVER_ID_1 = 'driver_1'
DRIVER_ID_2 = 'driver_2'
DRIVER_ID_3 = 'driver_3'
DRIVER_ID_4 = 'driver_4'
DRIVER_ID_5 = 'driver_5'
DRIVER_ID_6 = 'driver_6'
DEFAULT_APP_PROFILE = {
    'taximeter_version': '9.82 (6912)',
    'taximeter_version_type': 'beta',
    'taximeter_platform': 'android',
}


def _unordered(value):
    return sorted(tuple(sorted(x.items())) for x in value)


@pytest.mark.experiments3(filename='exp_communications_localization.json')
async def test_communications_localization(
        taxi_blocklist, driver_profiles, driver_protocol,
):

    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}': [
                f'{PARK_ID_1}_{DRIVER_ID_1}',
                f'{PARK_ID_1}_{DRIVER_ID_2}',
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': {
                'locale': 'en',
                'taximeter_version': '9.82 (6912)',
                'taximeter_version_type': 'beta',
                'taximeter_platform': 'android',
            },
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())

    assert len(actual_messages) == 2

    # driver_profile_id
    driver_profile_id = actual_messages[0][1][1]
    if str(driver_profile_id).find(DRIVER_ID_1) != -1:
        message_rus = actual_messages[0]
        message_eng = actual_messages[1]
    else:
        message_rus = actual_messages[1]
        message_eng = actual_messages[0]

    # check message
    assert (
        message_eng[2][1] == 'You are blocked! Block id: 1488, unmatched_key'
    )
    assert (
        message_rus[2][1]
        == 'Вы заблокированы! Номер блока: 1488, unmatched_key'
    )

    # check source
    assert message_eng[4][1] == 'Blocklist service'
    assert message_rus[4][1] == 'Сервис блоклистов'


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_park_id.json'],
    ids=['park_id'],
)
async def test_communications_predicates_park_id(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        load_json,
        notifications_assert,
):
    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}': [
                f'{PARK_ID_1}_{DRIVER_ID_1}',
                f'{PARK_ID_1}_{DRIVER_ID_2}',
            ],
            f'{PARK_ID_2}': [f'{PARK_ID_2}_{DRIVER_ID_3}'],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_3}': DEFAULT_APP_PROFILE,
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_license_id.json'],
    ids=['license_id'],
)
async def test_communications_predicates_license_id(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        load_json,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_4}'},
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_5}'},
            ],
            f'{LICENSE_ID_2}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_6}'},
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_4}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_5}': DEFAULT_APP_PROFILE,
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_park_license_id.json'],
    ids=['license_id_park_id'],
)
async def test_communications_predicates_license_id_park_id(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        load_json,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {
                    'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_3}',
                    'park_id': PARK_ID_4,
                },
                {
                    'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_1}',
                    'park_id': PARK_ID_4,
                },
            ],
            f'{LICENSE_ID_2}': [
                {
                    'driver_profile_id': f'{PARK_ID_4}_{DRIVER_ID_5}',
                    'park_id': PARK_ID_4,
                },
                {
                    'driver_profile_id': f'{PARK_ID_4}_{DRIVER_ID_6}',
                    'park_id': PARK_ID_4,
                },
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_4}_{DRIVER_ID_5}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_4}_{DRIVER_ID_6}': DEFAULT_APP_PROFILE,
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_car_number.json'],
    ids=['car_number'],
)
async def test_communications_predicates_car_number(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        fleet_vehicles,
        load_json,
        notifications_assert,
):

    driver_profiles.set_park_id_car_ids_drivers(
        {
            f'{PARK_ID_1}_{CAR_ID_1}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_1}'},
            ],
            f'{PARK_ID_2}_{CAR_ID_2}': [
                {'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_2}'},
            ],
            f'{PARK_ID_3}_{CAR_ID_3}': [
                {'driver_profile_id': f'{PARK_ID_3}_{DRIVER_ID_3}'},
            ],
            f'{PARK_ID_4}_{CAR_ID_4}': [
                {'driver_profile_id': f'{PARK_ID_4}_{DRIVER_ID_4}'},
            ],
        },
    )

    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_2}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_3}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_4}_{DRIVER_ID_4}': DEFAULT_APP_PROFILE,
        },
    )
    fleet_vehicles.set_park_cars(
        {
            f'{CAR_NUMBER_1}': [
                {'park_id_car_id': f'{PARK_ID_1}_{CAR_ID_1}'},
                {'park_id_car_id': f'{PARK_ID_2}_{CAR_ID_2}'},
            ],
            f'{CAR_NUMBER_2}': [{'park_id_car_id': f'{PARK_ID_3}_{CAR_ID_3}'}],
            f'{CAR_NUMBER_3}': [{'park_id_car_id': f'{PARK_ID_4}_{CAR_ID_4}'}],
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_car_number_park_id.json'],
    ids=['car_number_park_id'],
)
async def test_communications_predicates_car_number_park_id(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        fleet_vehicles,
        load_json,
        notifications_assert,
):
    driver_profiles.set_park_id_car_ids_drivers(
        {
            f'{PARK_ID_1}_{CAR_ID_1}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_1}'},
            ],
            f'{PARK_ID_2}_{CAR_ID_2}': [
                {'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_2}'},
            ],
            f'{PARK_ID_1}_{CAR_ID_2}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_3}'},
            ],
            f'{PARK_ID_2}_{CAR_ID_3}': [
                {'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_4}'},
            ],
            f'{PARK_ID_2}_{CAR_ID_4}': [
                {'driver_profile_id': f'{PARK_ID_2}_{DRIVER_ID_5}'},
            ],
        },
    )

    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_2}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_3}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_4}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_5}': DEFAULT_APP_PROFILE,
        },
    )
    fleet_vehicles.set_park_cars(
        {
            f'{CAR_NUMBER_1}': [
                {
                    'park_id_car_id': f'{PARK_ID_1}_{CAR_ID_1}',
                    'park_id': f'{PARK_ID_1}',
                },
                {
                    'park_id_car_id': f'{PARK_ID_1}_{CAR_ID_2}',
                    'park_id': f'{PARK_ID_1}',
                },
                {
                    'park_id_car_id': f'{PARK_ID_2}_{CAR_ID_2}',
                    'park_id': f'{PARK_ID_2}',
                },
            ],
            f'{CAR_NUMBER_2}': [
                {
                    'park_id_car_id': f'{PARK_ID_2}_{CAR_ID_3}',
                    'park_id': f'{PARK_ID_2}',
                },
            ],
            f'{CAR_NUMBER_3}': [
                {
                    'park_id_car_id': f'{PARK_ID_2}_{CAR_ID_4}',
                    'park_id': f'{PARK_ID_2}',
                },
            ],
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='blocklist_communications',
    consumers=['blocklist_communications'],
    clauses=[],
    default_value={
        'channel': 'driver_chat_add',
        'switcher': 'dry-run',
        'message_key': 'blocklist.communications.default',
        'dry_run': True,
    },
    is_config=True,
)
async def test_communications_dry_run(
        taxi_blocklist, driver_profiles, driver_protocol, pgsql,
):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 0

    # process one block
    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}': [
                f'{PARK_ID_1}_{DRIVER_ID_1}',
                f'{PARK_ID_1}_{DRIVER_ID_2}',
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': {
                'locale': 'en',
                'taximeter_version': '9.82 (6912)',
                'taximeter_version_type': 'beta',
                'taximeter_platform': 'android',
            },
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 1

    actual_messages = _unordered(driver_protocol.get_messages())

    assert actual_messages == []


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='blocklist_communications',
    consumers=['blocklist_communications'],
    clauses=[],
    default_value={
        'channel': 'driver_chat_add',
        'switcher': 'off',
        'message_key': 'blocklist.communications.default',
    },
    is_config=True,
)
async def test_communications_enabled(
        taxi_blocklist, driver_profiles, driver_protocol, pgsql,
):
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 0

    # process one block
    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}': [
                f'{PARK_ID_1}_{DRIVER_ID_1}',
                f'{PARK_ID_1}_{DRIVER_ID_2}',
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': {
                'locale': 'en',
                'taximeter_version': '9.82 (6912)',
                'taximeter_version_type': 'beta',
                'taximeter_platform': 'android',
            },
        },
    )

    await taxi_blocklist.run_task(TASK_NAME)

    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 1

    actual_messages = _unordered(driver_protocol.get_messages())

    assert actual_messages == []


@pytest.mark.experiments3(filename='exp_communications_substitution.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_substitution.json'],
    ids=['substitution'],
)
async def test_communications_substitution(
        personal,
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        load_json,
        taxi_config,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_4}'},
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_5}'},
            ],
            f'{LICENSE_ID_2}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_6}'},
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_4}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_5}': DEFAULT_APP_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_6}': DEFAULT_APP_PROFILE,
        },
    )

    personal.set_data({'driver_licenses': {'license_2': 'raw_license_id_2'}})
    # change config to
    # replace license_id with raw license
    new_config = taxi_config.get(SETTINGS_NAME)
    new_config['communication-sender-drivers']['kwargs_to_replace_with_pd'] = [
        'license_id',
    ]
    taxi_config.set_values({SETTINGS_NAME: new_config})
    await taxi_blocklist.invalidate_caches()

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_communications_predicates.json')
@pytest.mark.parametrize(
    'notifications_assert',
    ['reference/notifications_few_blocks.json'],
    ids=['two_blocks'],
)
async def test_communications_few_blocks(
        taxi_blocklist,
        driver_profiles,
        driver_protocol,
        load_json,
        notifications_assert,
):
    driver_profiles.set_licenses_drivers(
        {
            f'{LICENSE_ID_1}': [
                {'driver_profile_id': f'{PARK_ID_1}_{DRIVER_ID_1}'},
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_APP_PROFILE},
    )

    await taxi_blocklist.run_task(TASK_NAME)

    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))

    assert actual_messages == expect_messages
