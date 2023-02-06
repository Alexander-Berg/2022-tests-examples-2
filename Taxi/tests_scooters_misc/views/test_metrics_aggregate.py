# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

URL = '/scooters-misc/v1/metrics-aggregate'


@pytest.mark.experiments3(filename='exp3_scooters_city_by_position.json')
@pytest.mark.parametrize(
    'send_position',
    [
        pytest.param(True, id='send position'),
        pytest.param(False, id='do not send position'),
    ],
)
@pytest.mark.parametrize(
    'sensor, metrics_item, expected_metrics',
    [
        pytest.param(
            'scooters_misc_tag_evolve_metrics',
            {
                'status_code': 200,
                'meta': {
                    'endpoint': 'tag/evolve',
                    'tag': 'old_state_reservation',
                    'evolution_mode': 'ignore_telematic',
                    'dry_run': True,
                    'bluetooth_flow_enabled': True,
                    'bluetooth_flow_enabled_forced': True,
                    'ble_flow_is_used': True,
                },
            },
            [
                metrics_helpers.Metric(
                    labels={
                        'evolution_mode': 'ignore_telematic',
                        'sensor': 'scooters_misc_tag_evolve_metrics',
                        'status_code': '200',
                        'error_code': '',
                        'tag': 'old_state_reservation',
                        'city': 'undefined',
                        'dry_run': '1',
                        'bluetooth_flow_enabled': '1',
                        'bluetooth_flow_enabled_forced': '1',
                        'ble_flow_is_used': '1',
                    },
                    value=1,
                ),
            ],
            id='tag/evolve',
        ),
        pytest.param(
            'scooters_misc_car_control_metrics',
            {
                'status_code': 200,
                'meta': {
                    'endpoint': 'car/control',
                    'action': 'blink-n-horn',
                    'bluetooth_flow_enabled': True,
                    'bluetooth_flow_enabled_forced': True,
                },
            },
            [
                metrics_helpers.Metric(
                    labels={
                        'sensor': 'scooters_misc_car_control_metrics',
                        'status_code': '200',
                        'city': 'undefined',
                        'action': 'blink-n-horn',
                        'bluetooth_flow_enabled': '1',
                        'bluetooth_flow_enabled_forced': '1',
                    },
                    value=1,
                ),
            ],
            id='car/control',
        ),
    ],
)
async def test_common(
        taxi_scooters_misc,
        taxi_scooters_misc_monitor,
        get_metrics_by_label_values,
        sensor,
        metrics_item,
        expected_metrics,
        send_position,
):
    await taxi_scooters_misc.tests_control(reset_metrics=True)

    if send_position:
        metrics_item['position'] = [39.0, 45.0]
    payload = {'metrics_item': metrics_item}
    response = await taxi_scooters_misc.post(URL, json=payload)
    assert response.status == 200

    metrics = await get_metrics_by_label_values(
        taxi_scooters_misc_monitor, sensor=sensor, labels={'sensor': sensor},
    )
    if send_position:
        for i in expected_metrics:
            i.labels['city'] = 'Moscow'
    assert metrics == expected_metrics
