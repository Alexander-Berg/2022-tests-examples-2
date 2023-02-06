import copy
import datetime

import pytest

PARK_ID_1 = '11136bc7560449998acbe2c57a75c293'
PARK_ID_2 = '22236bc7560449998acbe2c57a75c222'
PARK_ID_3 = '33336bc7560449998acbe2c57a75c333'
DRIVER_ID_1 = '984d71c903f29b01e2a167fe86ce0f26'
DRIVER_ID_2 = 'c6c595239fdc59f9c161ef73917217d6'
DRIVER_ID_3 = '0076d68f2f2d728d080d4522623218b3'
CAR_ID_1 = 'f728e8d99ac2c7d4cc025293b154a859'
CAR_ID_2 = '2228e8d99ac2c7d4cc025293b154a222'

TASK_NAME = 'communication-sender-parks'

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


def _unordered(value):
    return sorted(
        value,
        key=lambda x: (x['park_id'][0]['park_id'], x['message'], x['title']),
    )


def _get_park_info(park_id: str):
    park_info = copy.copy(DEFAULT_PARK)
    park_info['id'] = park_id
    return park_info


# pylint: disable=too-many-arguments
@pytest.mark.experiments3(filename='exp_qc_communication_resolution.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
@pytest.mark.parametrize(
    'cursor,passes,passes_assert,notifications_assert,metrics_assert',
    [
        (
            None,
            'mock_responses/api_v1_pass_list_full.json',
            [
                {'limit': '5', 'modified_from': '2021-06-27T12:00:00+00:00'},
                {'limit': '5', 'cursor': '7'},
                {'limit': '5', 'cursor': '12'},
            ],
            'reference/notifications_full.json',
            {
                'common_errors': 1,
                'filtered': 11,
                'input': 14,
                'not_sent': 1,
                'sent': 10,
            },
        ),
        (
            dict(
                cursor='7',
                last_modified=datetime.datetime(2020, 6, 27, 11, 00, 00),
            ),
            'mock_responses/api_v1_pass_list_full.json',
            [
                {'limit': '5', 'modified_from': '2021-06-27T12:00:00+00:00'},
                {'limit': '5', 'cursor': '7'},
                {'limit': '5', 'cursor': '12'},
            ],
            'reference/notifications_full.json',
            {
                'common_errors': 1,
                'filtered': 11,
                'input': 14,
                'not_sent': 1,
                'sent': 10,
            },
        ),
        (
            dict(
                cursor='7',
                last_modified=datetime.datetime(2021, 6, 28, 11, 00, 00),
            ),
            'mock_responses/api_v1_pass_list_full.json',
            [{'limit': '5', 'cursor': '7'}, {'limit': '5', 'cursor': '12'}],
            'reference/notifications_cursor.json',
            {
                'common_errors': 0,
                'filtered': 8,
                'input': 9,
                'not_sent': 1,
                'sent': 7,
            },
        ),
    ],
    ids=['full', 'expired_cursor', 'cursor'],
)
async def test_communications_full(
        taxi_quality_control_cpp,
        fleet_parks,
        quality_control,
        fleet_notifications,
        mongodb,
        load_json,
        taxi_quality_control_cpp_monitor,
        cursor,
        passes,
        passes_assert,
        notifications_assert,
        metrics_assert,
):
    await taxi_quality_control_cpp.tests_control(reset_metrics=True)

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    park_2 = _get_park_info(PARK_ID_2)
    park_2['locale'] = 'en'

    park_3 = _get_park_info(PARK_ID_3)
    park_3['locale'] = 'ru-GOP'

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': DEFAULT_PARK,
            f'{PARK_ID_2}': park_2,
            f'{PARK_ID_3}': park_3,
        },
    )

    if cursor:
        mongodb.qc_jobs_data.insert_one(dict(job=TASK_NAME, **cursor))

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(fleet_notifications.get_messages())
    expect_messages = _unordered(load_json(notifications_assert))
    assert actual_messages == expect_messages

    reqs = quality_control.get_pass_list_reqs()
    assert reqs == passes_assert

    cursor = mongodb.qc_jobs_data.find_one({'job': TASK_NAME})
    assert cursor['cursor'] == str(len(passes_list))

    metrics = (await taxi_quality_control_cpp_monitor.get_metrics())[
        'communications_drivers_stats'
    ]
    assert metrics == metrics_assert


@pytest.mark.experiments3(filename='exp_qc_communication_resolution.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
@pytest.mark.parametrize(
    'passes,notifications',
    [
        (
            'mock_responses/api_v1_pass_list_check_drivers.json',
            'reference/notifications_check_drivers.json',
        ),
    ],
)
async def test_communications_fetch_drivers(
        taxi_quality_control_cpp,
        fleet_parks,
        quality_control,
        fleet_notifications,
        load_json,
        passes,
        notifications,
):
    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': DEFAULT_PARK,
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(fleet_notifications.get_messages())
    expect_messages = _unordered(load_json(notifications))
    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_qc_communication_resolution.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
@pytest.mark.parametrize(
    'passes,notifications',
    [
        (
            'mock_responses/api_v1_pass_list_check_cars.json',
            'reference/notifications_check_cars.json',
        ),
    ],
)
async def test_communications_fetch_cars(
        taxi_quality_control_cpp,
        fleet_parks,
        quality_control,
        fleet_notifications,
        load_json,
        passes,
        notifications,
):
    park_2 = _get_park_info(DEFAULT_PARK)
    park_2['id'] = PARK_ID_2

    park_3 = _get_park_info(DEFAULT_PARK)
    park_3['id'] = PARK_ID_3

    fleet_parks.set_parks(
        {
            f'{PARK_ID_1}': DEFAULT_PARK,
            f'{PARK_ID_2}': _get_park_info(PARK_ID_2),
            f'{PARK_ID_3}': _get_park_info(PARK_ID_3),
        },
    )

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(fleet_notifications.get_messages())
    expect_messages = _unordered(load_json(notifications))
    assert actual_messages == expect_messages


@pytest.mark.experiments3(filename='exp_qc_communication_substitutions.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
@pytest.mark.parametrize(
    'passes,notifications',
    [
        (
            'mock_responses/api_v1_pass_list_substitutions.json',
            'reference/notifications_substitutions.json',
        ),
    ],
)
async def test_communications_substitutions(
        taxi_quality_control_cpp,
        fleet_parks,
        quality_control,
        fleet_notifications,
        load_json,
        passes,
        notifications,
):
    fleet_parks.set_parks({f'{PARK_ID_1}': DEFAULT_PARK})

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(fleet_notifications.get_messages())
    expect_messages = _unordered(load_json(notifications))
    assert actual_messages == expect_messages
