import pytest

from testsuite.utils import matching

from fleet_drivers_scoring.stq import checks
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils


@pytest.mark.pgsql('fleet_drivers_scoring', files=['state.sql'])
@pytest.mark.parametrize(
    'passenger_tags_yt, passenger_tags_stored',
    [
        ('passenger_tags_ok.json', 'passenger_tags_ok_stored.json'),
        (
            'passenger_tags_low_significance.json',
            'passenger_tags_low_significance_stored.json',
        ),
    ],
)
async def test_ok(
        stq3_context,
        pgsql,
        _mock_driver_profiles,
        _mock_unique_drivers,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
        mock_yt,
        load_json,
        passenger_tags_yt,
        passenger_tags_stored,
):
    mocks_setup.setup_mocks(
        _mock_driver_profiles,
        _mock_unique_drivers,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/'
        'passenger_tags/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename=passenger_tags_yt,
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': 'req_1',
            'idempotency_token': 'req_1',
            'license_pd_id': 'license_pd_id',
            'park_id': 'park1',
            'status': 'done',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': True,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': True,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': True,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': True,
            'passenger_tags_id': matching.uuid_string,
            'is_passenger_tags_calculated': True,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': True,
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]

    high_speed_driving = global_utils.fetch_check_part(
        pgsql, all_checks[0]['passenger_tags_id'],
    )
    high_speed_driving.pop('created_at')
    assert high_speed_driving.pop('id') == all_checks[0]['passenger_tags_id']
    assert global_utils.date_parsed(
        high_speed_driving,
    ) == global_utils.date_parsed(load_json(passenger_tags_stored))
