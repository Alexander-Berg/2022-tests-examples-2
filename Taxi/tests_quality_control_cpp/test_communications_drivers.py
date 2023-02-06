import datetime

import pytest

PARK_ID_1 = '7ad36bc7560449998acbe2c57a75c293'
PARK_ID_2 = '22236bc7560449998acbe2c57a75c222'
PARK_ID_3 = '33336bc7560449998acbe2c57a75c333'
DRIVER_ID_1 = '984d71c903f29b01e2a167fe86ce0f26'
DRIVER_ID_2 = 'c6c595239fdc59f9c161ef73917217d6'
DRIVER_ID_3 = '0076d68f2f2d728d080d4522623218b3'
CAR_ID_1 = 'f728e8d99ac2c7d4cc025293b154a859'
CAR_ID_2 = '2228e8d99ac2c7d4cc025293b154a222'

TASK_NAME = 'communication-sender-drivers'

DEFAULT_PROFILE = {
    'taximeter_version': '9.82 (6912)',
    'taximeter_version_type': 'beta',
    'taximeter_platform': 'android',
}


def _unordered(value):
    return sorted(tuple(sorted(x.items())) for x in value)


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
                'not_sent': 2,
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
                'not_sent': 2,
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
                'not_sent': 2,
                'sent': 7,
            },
        ),
    ],
    ids=['full', 'expired_cursor', 'cursor'],
)
async def test_communications_full(
        taxi_quality_control_cpp,
        driver_profiles,
        quality_control,
        driver_protocol,
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
    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}_{CAR_ID_1}': [
                f'{PARK_ID_1}_{DRIVER_ID_1}',
                f'{PARK_ID_1}_{DRIVER_ID_2}',
            ],
        },
    )
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_2}_{DRIVER_ID_3}': DEFAULT_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': {
                'locale': 'en',
                'taximeter_platform': '',
                'taximeter_version': '',
                'taximeter_version_type': '',
            },
            f'{PARK_ID_1}_{DRIVER_ID_3}': {
                'locale': 'ru-GOP',
                'taximeter_platform': 'colibri',
                'taximeter_version': 'i-am-pure-evil',
                'taximeter_version_type': 'pwned',
            },
        },
    )

    if cursor:
        mongodb.qc_jobs_data.insert_one(dict(job=TASK_NAME, **cursor))

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(driver_protocol.get_messages())
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
        driver_profiles,
        quality_control,
        driver_protocol,
        load_json,
        passes,
        notifications,
):
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_1}_{DRIVER_ID_2}': DEFAULT_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_2}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_2}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_3}': DEFAULT_PROFILE,
        },
    )

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(driver_protocol.get_messages())
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
        driver_profiles,
        quality_control,
        driver_protocol,
        load_json,
        passes,
        notifications,
):
    driver_profiles.set_drivers_app_profile(
        {
            f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_2}_{DRIVER_ID_2}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_1}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_2}': DEFAULT_PROFILE,
            f'{PARK_ID_3}_{DRIVER_ID_3}': DEFAULT_PROFILE,
        },
    )

    driver_profiles.set_cars_drivers(
        {
            f'{PARK_ID_1}_{CAR_ID_1}': [f'{PARK_ID_1}_{DRIVER_ID_1}'],
            f'{PARK_ID_2}_{CAR_ID_1}': [
                f'{PARK_ID_2}_{DRIVER_ID_1}',
                f'{PARK_ID_2}_{DRIVER_ID_2}',
            ],
            f'{PARK_ID_2}_{CAR_ID_2}': [f'{PARK_ID_2}_{DRIVER_ID_1}'],
            f'{PARK_ID_3}_{CAR_ID_2}': [
                f'{PARK_ID_3}_{DRIVER_ID_1}',
                f'{PARK_ID_3}_{DRIVER_ID_2}',
                f'{PARK_ID_3}_{DRIVER_ID_3}',
            ],
        },
    )

    passes_list = load_json(passes)
    quality_control.set_pass_list_data(passes_list)

    await taxi_quality_control_cpp.run_task(TASK_NAME)
    actual_messages = _unordered(driver_protocol.get_messages())
    expect_messages = _unordered(load_json(notifications))
    assert actual_messages == expect_messages
