import copy
import time

import pytest


TASK_NAME = 'communication-sender-parks'
SETTINGS_NAME = 'BLOCKLIST_COMMUNICATIONS_SETTINGS'

CURSOR_QUERY = (
    'SELECT cursors.name, cursors.value FROM'
    f' blocklist.cursors WHERE cursors.name = \'{TASK_NAME}\';'
)
PARK_ID_1 = 'park-1'
PARK_ID_2 = 'park-2'
PARK_ID_3 = 'park-3'
PARK_ID_4 = 'park-4'
PARK_ID_5 = 'park-5'

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


def _get_park_info(park_id: str):
    park_info = copy.copy(DEFAULT_PARK)
    park_info['id'] = park_id
    return park_info


@pytest.mark.experiments3(filename='exp_communications_localization.json')
async def test_communications_cursor_updating(
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
            f'{PARK_ID_4}': _get_park_info(PARK_ID_4),
            f'{PARK_ID_5}': _get_park_info(PARK_ID_5),
        },
    )

    # process 5 blocks
    await taxi_blocklist.run_task(TASK_NAME)

    # the cursor value should be increased by 5
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 5

    await taxi_blocklist.run_task(TASK_NAME)

    # the cursor value should not be increased
    cursor = pgsql['blocklist'].cursor()
    cursor.execute(CURSOR_QUERY)
    assert list(cursor)[0][1] == 5


@pytest.mark.experiments3(filename='exp_communications_localization.json')
@pytest.mark.parametrize(
    'allowed_notifications_parks, allowed_fleet_parks,'
    'messages_len, metrics_assert',
    [
        (
            [PARK_ID_1, PARK_ID_2],
            [PARK_ID_1, PARK_ID_2, PARK_ID_3, PARK_ID_4, PARK_ID_5],
            2,
            {
                'blocks_retrieved': 5,
                'common_errors': 0,
                'message_errors': 3,
                'sent': 2,
            },
        ),
        (
            [PARK_ID_1, PARK_ID_2, PARK_ID_3, PARK_ID_4, PARK_ID_5],
            [PARK_ID_1, PARK_ID_2, PARK_ID_3, PARK_ID_4, PARK_ID_5],
            5,
            {
                'blocks_retrieved': 5,
                'common_errors': 0,
                'message_errors': 0,
                'sent': 5,
            },
        ),
        (
            [PARK_ID_1, PARK_ID_2, PARK_ID_3, PARK_ID_4, PARK_ID_5],
            [PARK_ID_1, PARK_ID_2, PARK_ID_3, PARK_ID_4],
            0,
            {
                'blocks_retrieved': 5,
                'common_errors': 1,
                'message_errors': 0,
                'sent': 0,
            },
        ),
    ],
    ids=['just_two_allowed_parks', 'all_allowed', 'with_fetching_exception'],
)
async def test_communications_metrics(
        taxi_blocklist,
        fleet_notifications_with_exceptions,
        fleet_parks_with_exceptions,
        taxi_blocklist_monitor,
        allowed_notifications_parks,
        allowed_fleet_parks,
        messages_len,
        metrics_assert,
):
    # throw exception if park is not in fleet_parks
    # and increase common_errors metrics
    fleet_parks_with_exceptions.set_parks(
        {
            f'{park_id}': _get_park_info(park_id)
            for park_id in allowed_fleet_parks
        },
    )
    # throw exception while sending messages
    # if park is not in fleet_notifications
    # and increase message_errors metrics
    fleet_notifications_with_exceptions.set_parks(allowed_notifications_parks)

    await taxi_blocklist.tests_control(reset_metrics=True)
    await taxi_blocklist.run_task(TASK_NAME)

    metrics = (await taxi_blocklist_monitor.get_metrics())[
        'communications_parks_stats'
    ]
    assert metrics == metrics_assert

    actual_messages = fleet_notifications_with_exceptions.get_messages()

    assert len(actual_messages) == messages_len


@pytest.mark.experiments3(filename='exp_communications_localization.json')
@pytest.mark.parametrize(
    'threads_num, sending_sleep_ms, min_ms',
    [(2, 500, 1000), (1, 500, 2500), (5, 1000, 1000), (6, 1000, 0)],
)
async def test_communications_sending_batching(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        personal,
        taxi_config,
        threads_num,
        sending_sleep_ms,
        min_ms,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
            f'{PARK_ID_4}': _get_park_info(PARK_ID_4),
            f'{PARK_ID_5}': _get_park_info(PARK_ID_5),
        },
    )

    new_config = taxi_config.get(SETTINGS_NAME)

    new_config['communication-sender-parks'][
        'sending_threads_num'
    ] = threads_num
    new_config['communication-sender-parks'][
        'sending_sleep_ms'
    ] = sending_sleep_ms

    taxi_config.set_values({SETTINGS_NAME: new_config})
    await taxi_blocklist.invalidate_caches()

    start = time.time()
    await taxi_blocklist.run_task(TASK_NAME)
    end = time.time()
    elapsed = end - start

    work_time_ms = 300
    min_s = min_ms / 1000
    assert elapsed > min_s
    assert elapsed < (min_s + work_time_ms)

    assert len(fleet_notifications.get_messages()) == 5


@pytest.mark.experiments3(filename='exp_communications_localization.json')
@pytest.mark.parametrize(
    'limit, block_numbers_array', [(2, [2, 4, 5, 5]), (3, [3, 5, 5, 5])],
)
async def test_communications_retrieving_limit(
        taxi_blocklist,
        fleet_notifications,
        fleet_parks,
        personal,
        taxi_config,
        limit,
        block_numbers_array,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': _get_park_info(PARK_ID_1),
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
            f'{PARK_ID_4}': _get_park_info(PARK_ID_4),
            f'{PARK_ID_5}': _get_park_info(PARK_ID_5),
        },
    )

    new_config = taxi_config.get(SETTINGS_NAME)

    new_config['communication-sender-parks']['retrieve_limit'] = limit

    taxi_config.set_values({SETTINGS_NAME: new_config})
    await taxi_blocklist.invalidate_caches()

    for block_number in block_numbers_array:
        # retrieve only limit every time
        await taxi_blocklist.run_task(TASK_NAME)
        assert len(fleet_notifications.get_messages()) == block_number
