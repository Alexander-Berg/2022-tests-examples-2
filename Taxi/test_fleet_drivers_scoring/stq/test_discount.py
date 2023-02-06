import pytest

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


@pytest.mark.config(
    **FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED,
    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
        {
            'begin_at': '1900-01-01',
            'checks_with_discounted_price': 1,
            'checks_with_normal_price': 1,
            'countries': {'rus': {'amount': '1', 'currency': 'RUB'}},
            'clids': {},
        },
    ],
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['discount.sql'])
@pytest.mark.now('2020-07-25T11:00:00+00')
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
    assert len(all_checks) == 2
    new_check = next(x for x in all_checks if x['check_id'] == 'check_id')
    new_check.pop('created_at')
    new_check.pop('updated_at')
    assert new_check == {
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
            'price': {'amount': '1', 'currency': 'RUB'},
        },
        'requested_by': None,
        'billing_doc_id': 100500,
        'discount_type': 'buy_x_get_y',
    }


@pytest.mark.config(
    **FLEET_DRIVERS_SCORING_CHECK_PARTS_DISABLED,
    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
        {
            'begin_at': '1900-01-01',
            'checks_with_discounted_price': 1,
            'checks_with_normal_price': 1,
            'countries': {'rus': {'amount': '15', 'currency': 'RUB'}},
            'clids': {},
        },
    ],
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['discount_no_recalc.sql'])
@pytest.mark.now('2020-07-25T11:00:00+00')
async def test_no_recalc(
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
    new_check = next(x for x in all_checks if x['check_id'] == 'check_id')
    new_check.pop('created_at')
    new_check.pop('updated_at')
    assert new_check == {
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
            'price': {'amount': '499', 'currency': 'RUB'},
        },
        'requested_by': None,
        'billing_doc_id': 100500,
        'discount_type': 'basic_price',
    }

    assert _mock_billing_orders.billing_orders.times_called == 1
    billing_orders = _mock_billing_orders.billing_orders.next_call()[
        'request'
    ].json

    assert (
        billing_orders['orders'][0]['data']['payments'][0]['payload'][
            'amount_details'
        ]['base_amount']
        == '499'
    )
    assert (
        billing_orders['orders'][0]['data']['payments'][0]['amount'] == '499'
    )
