import pytest

from testsuite.utils import ordered_object

from fleet_drivers_scoring.stq import checks
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils

FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED = {
    'FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED': {
        'check_parts_to_disable': [
            'ratings_history',
            'orders_statistics',
            'quality_metrics',
            'high_speed_driving',
            'driving_style',
            'passenger_tags',
        ],
    },
}


# disable all check to test only new flow
@pytest.mark.config(**FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_with_offer.sql'])
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
        load_json,
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

    await checks.task(
        stq3_context, park_id='park1', check_id='check_id', log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': 'check_id',
            'idempotency_token': '100000000',
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
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': True,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': True,
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '100', 'currency': 'RUB'},
            },
            'requested_by': None,
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]


@pytest.mark.config(
    **FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED,
    FLEET_DRIVERS_SCORING_PRICES_2={
        'countries': {
            'rus': {
                'main_amount': '200',
                'simple_version_amount': '20',
                'basic_version_amount': '2',
                'currency': 'RUB',
            },
        },
        'clids': {},
    },
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_with_offer.sql'])
async def test_price_mismatch(
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
        load_json,
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

    await checks.task(
        stq3_context, park_id='park1', check_id='check_id', log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': 'check_id',
            'idempotency_token': '100000000',
            'license_pd_id': 'license_pd_id',
            'park_id': 'park1',
            'status': 'failed',
            'status_meta_info': {'reason': 'price_changed'},
            'ratings_history_id': None,
            'is_ratings_history_calculated': True,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': True,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': True,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': True,
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': True,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': True,
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '100', 'currency': 'RUB'},
            },
            'requested_by': None,
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]

    assert _mock_billing_orders.billing_orders.times_called == 0


@pytest.mark.config(**FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['has_recent_check.sql'])
async def test_nothing_changed(
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
        load_json,
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

    await checks.task(
        stq3_context, park_id='park1', check_id='check_id', log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 2
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    all_checks[1].pop('created_at')
    all_checks[1].pop('updated_at')
    ordered_object.assert_eq(
        all_checks,
        [
            {
                'check_id': 'check_id_prev',
                'idempotency_token': '100',
                'license_pd_id': 'license_pd_id',
                'park_id': 'park1',
                'status': 'pending',
                'status_meta_info': None,
                'ratings_history_id': None,
                'is_ratings_history_calculated': False,
                'orders_statistics_id': None,
                'is_orders_statistics_calculated': True,
                'quality_metrics_id': None,
                'is_quality_metrics_calculated': True,
                'high_speed_driving_id': None,
                'is_high_speed_driving_calculated': True,
                'driving_style_id': None,
                'is_driving_style_calculated': True,
                'passenger_tags_id': None,
                'is_passenger_tags_calculated': True,
                'car_orders_history_id': None,
                'is_car_orders_history_calculated': True,
                'offer': None,
                'requested_by': None,
                'billing_doc_id': None,
                'discount_type': None,
            },
            {
                'check_id': 'check_id',
                'idempotency_token': '100000000',
                'license_pd_id': 'license_pd_id',
                'park_id': 'park1',
                'status': 'failed',
                'status_meta_info': {'reason': 'nothing_changed'},
                'ratings_history_id': None,
                'is_ratings_history_calculated': False,
                'orders_statistics_id': None,
                'is_orders_statistics_calculated': True,
                'quality_metrics_id': None,
                'is_quality_metrics_calculated': True,
                'high_speed_driving_id': None,
                'is_high_speed_driving_calculated': True,
                'driving_style_id': None,
                'is_driving_style_calculated': True,
                'passenger_tags_id': None,
                'is_passenger_tags_calculated': True,
                'car_orders_history_id': None,
                'is_car_orders_history_calculated': True,
                'offer': {
                    'decision': {'can_buy': True},
                    'price': {'amount': '100', 'currency': 'RUB'},
                },
                'requested_by': None,
                'billing_doc_id': None,
                'discount_type': None,
            },
        ],
        paths=[''],
    )

    assert _mock_billing_orders.billing_orders.times_called == 0
