import pytest

DISTLOCK_NAME = 'scooters-misc-metrics-collector'


@pytest.mark.config(
    SCOOTERS_MISC_METRICS_COLLECTOR_SETTINGS={
        'sleep_time_seconds': 1,
        'enabled': True,
        'tags_blacklist': [],
    },
)
@pytest.mark.now('2021-06-23T19:00:00+0000')
@pytest.mark.parametrize(
    'sensor, labels',
    [
        pytest.param(
            'scooters_misc_compiled_rides_metrics',
            {
                'sensor': 'scooters_misc_compiled_rides_metrics',
                'compiled_rides': 'today',
            },
            id='compiled_rides',
        ),
        pytest.param(
            'scooters_misc_car_tags_metrics',
            {
                'sensor': 'scooters_misc_car_tags_metrics',
                'scooter_tag': 'old_state_reservation',
                'city_tag': 'scooter_krasnodar',
            },
            id='car_tags',
        ),
        pytest.param(
            'scooters_misc_payment_methods_metrics',
            {
                'sensor': 'scooters_misc_payment_methods_metrics',
                'payment_methods': 'apple_pay',
                'status': 'cleared',
            },
            id='payment_methods',
        ),
    ],
)
async def test_simple(
        taxi_scooters_misc,
        taxi_scooters_misc_monitor,
        get_single_metric_by_label_values,
        sensor,
        labels,
):

    await taxi_scooters_misc.tests_control(reset_metrics=True)
    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    compiled_rides_metric = await get_single_metric_by_label_values(
        taxi_scooters_misc_monitor, sensor=sensor, labels=labels,
    )
    assert compiled_rides_metric.value == 1
    assert compiled_rides_metric.labels == labels
