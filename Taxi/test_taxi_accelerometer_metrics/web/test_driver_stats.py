import pytest

LOG_FIELDS = [
    'tskv',
    'tskv_format',
    'meta_order_id',
    'meta_driver_id',
    '_link',
    'meta_db',
    'timestamp',
    'item',
    'total',
    'acc_max_ax',
    'acc_max_ay',
    'acc_mean_ax',
    'acc_mean_ay',
    'acc_min_ax',
    'acc_min_ay',
    'acc_q_10_ax',
    'acc_q_10_ay',
    'acc_q_5_ax',
    'acc_q_5_ay',
    'acc_q_90_ax',
    'acc_q_90_ay',
    'acc_q_95_ax',
    'acc_q_95_ay',
    'acc_std_ax',
    'acc_std_ay',
    'acc_sum_ax',
    'acc_sum_ay',
    'bearing_max_diff',
    'bearing_start_end_diff',
    'bearing_std',
    'maneuver_time_diff',
    'gap_max_ax',
    'gap_max_ay',
    'gap_mean_ax',
    'gap_mean_ay',
    'gap_min_ax',
    'gap_min_ay',
    'gap_std_ax',
    'gap_std_ay',
    'gap_sum_ax',
    'gap_sum_ay',
    'normalized_sigma_mean',
    'normalized_sigma_min',
    'orientation_w',
    'orientation_x',
    'orientation_y',
    'orientation_z',
    'position_accuracy',
    'position_altitude',
    'position_is_bad',
    'position_is_fake',
    'position_lat',
    'position_lon',
    'position_provider',
    'position_real_time',
    'position_speed_mps',
    'position_time',
    'speed_end',
    'speed_max',
    'speed_mean',
    'speed_min',
    'speed_start',
    'speed_std',
    'maneuver_start_time',
    'gap_time_diff',
    'type',
]


@pytest.mark.config(ACCELEROMETER_METRICS_DRIVERSTATS_ENABLED=True)
async def test_driver_stats(
        web_event_logs, web_app_client, web_context, load_json,
):
    response = await web_app_client.post(
        'v1/driver/stats',
        headers={
            'X-Request-Application-Version': '9.05',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
            'X-YaTaxi-Park-Id': 'db',
            'User-Agent': 'Taximeter 9.05',
        },
        json=load_json('accelerometer_metrics.json'),
    )

    assert response.status == 200
    assert len(web_event_logs) == 3
    for log in web_event_logs:
        keys = [x.split('=')[0] for x in log.split('\t')]
        assert sorted(keys) == sorted(LOG_FIELDS)
