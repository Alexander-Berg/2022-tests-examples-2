import time


import pytest


PARK_ID_1 = '7ad36bc7560449998acbe2c57a75c293'
DRIVER_ID_1 = '984d71c903f29b01e2a167fe86ce0f26'

DEFAULT_PROFILE = {
    'taximeter_version': '9.82 (6912)',
    'taximeter_version_type': 'beta',
    'taximeter_platform': 'android',
}
SETTINGS_NAME = 'QC_CPP_COMMUNICATIONS_WORKERS_SETTINGS'
TASK_NAME = 'communication-sender-drivers'


@pytest.mark.experiments3(filename='exp_qc_communication_resolution.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
@pytest.mark.parametrize(
    'threads_num, sending_sleep_ms, min_ms',
    [(2, 500, 1000), (1, 500, 2500), (5, 1000, 1000), (6, 1000, 0)],
)
async def test_communications_sending_batching(
        taxi_quality_control_cpp,
        driver_profiles,
        quality_control,
        driver_protocol,
        load_json,
        taxi_config,
        threads_num,
        sending_sleep_ms,
        min_ms,
):
    passes_list = load_json('mock_responses/api_v1_pass_list_batching.json')
    quality_control.set_pass_list_data(passes_list)

    driver_profiles.set_drivers_app_profile(
        {f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_PROFILE},
    )

    new_config = taxi_config.get(SETTINGS_NAME)

    new_config['communication-sender-drivers'][
        'sending_threads_num'
    ] = threads_num
    new_config['communication-sender-drivers'][
        'sending_sleep_ms'
    ] = sending_sleep_ms

    taxi_config.set_values({SETTINGS_NAME: new_config})
    await taxi_quality_control_cpp.invalidate_caches()

    start = time.time()
    await taxi_quality_control_cpp.run_task(TASK_NAME)
    end = time.time()
    elapsed = end - start

    work_time_ms = 300
    min_s = min_ms / 1000
    assert elapsed > min_s
    assert elapsed < (min_s + work_time_ms)

    assert len(driver_protocol.get_messages()) == 5


@pytest.mark.experiments3(filename='exp_qc_communication_resolution.json')
@pytest.mark.now('2021-06-28T12:00:00+00:00')
async def test_communications_sending_switcher(
        taxi_quality_control_cpp,
        driver_profiles,
        quality_control,
        driver_protocol,
        load_json,
        mongodb,
        taxi_quality_control_cpp_monitor,
):
    await taxi_quality_control_cpp.tests_control(reset_metrics=True)

    passes_list = load_json('mock_responses/api_v1_pass_list_switcher.json')
    quality_control.set_pass_list_data(passes_list)

    driver_profiles.set_drivers_app_profile(
        {f'{PARK_ID_1}_{DRIVER_ID_1}': DEFAULT_PROFILE},
    )

    await taxi_quality_control_cpp.run_task(TASK_NAME)

    assert len(driver_protocol.get_messages()) == 1

    reqs = quality_control.get_pass_list_reqs()
    assert reqs == [
        {'modified_from': '2021-06-27T12:00:00+00:00', 'limit': '5'},
    ]

    cursor = mongodb.qc_jobs_data.find_one({'job': TASK_NAME})
    assert cursor['cursor'] == str(3)

    metrics = (await taxi_quality_control_cpp_monitor.get_metrics())[
        'communications_drivers_stats'
    ]
    assert metrics == {
        'common_errors': 0,
        'filtered': 3,
        'input': 3,
        'not_sent': 2,
        'sent': 1,
    }
