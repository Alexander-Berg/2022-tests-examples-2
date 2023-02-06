import pytest

from tests_eats_place_subscriptions import utils


@utils.set_tariffs_experiment(
    {
        'tariffs': [
            {
                'type': 'business',
                'features': ['sorry', 'boss_bot'],  # disabled daily_billing
                'additional_commission': 1.44,
            },
            {
                'type': 'business_plus',
                'features': [
                    'daily_billing',
                    'sorry',
                    'boss_bot',
                    'personal_manager',
                ],
                'additional_commission': 1.44,
                'trial_additional_commission': 0.1,
                'fix_cost': 1299.0,
            },
            {'type': 'free', 'features': []},
        ],
    },
)
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='start_feat_flag.json')
@pytest.mark.parametrize(
    'place_id, expected_response',
    [
        (124, {'daily_billing_enabled': True, 'additional_commission': 1.44}),
        (123, {'daily_billing_enabled': False, 'additional_commission': 1.44}),
        (126, {'daily_billing_enabled': False}),
        (128, {'daily_billing_enabled': True, 'additional_commission': 0.1}),
    ],
    ids=[
        'green_flow',
        'disabled_daily_billing',
        'disabled_with_zero_commission',
        'trial_commission',
    ],
)
async def test_subscription_commission_handle(
        place_id, expected_response, taxi_eats_place_subscriptions,
):
    response = await taxi_eats_place_subscriptions.get(
        '/internal/eats-place-subscriptions/v1/get-subscription-commission',
        params={'place_id': place_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='start_feat_flag.json')
async def test_subscription_commission_no_subscription(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.get(
        '/internal/eats-place-subscriptions/v1/get-subscription-commission',
        params={'place_id': 100},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found_data',
        'message': 'Not found one subscription for place',
    }

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.SUBSCRIPTION_ERRORS_METRICS] == {'not_found_in_db': 1}


@utils.set_tariffs_experiment({'tariffs': [{'type': 'free', 'features': []}]})
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='start_feat_flag.json')
async def test_subscription_commission_no_tariff(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.get(
        '/internal/eats-place-subscriptions/v1/get-subscription-commission',
        params={'place_id': 123},
    )
    assert response.status_code == 500

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}


@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_subscription_commission_handle_turn_off(
        taxi_eats_place_subscriptions,
):
    response = await taxi_eats_place_subscriptions.get(
        '/internal/eats-place-subscriptions/v1/get-subscription-commission',
        params={'place_id': 124},
    )
    assert response.status_code == 200
    assert response.json() == {'daily_billing_enabled': False}


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.experiments3(filename='start_feat_flag.json')
@pytest.mark.parametrize(
    'place_id, expected_response',
    [
        (126, {'daily_billing_enabled': False}),
        (130, {'daily_billing_enabled': True}),
        (131, {'daily_billing_enabled': True}),
        (132, {'daily_billing_enabled': True}),
    ],
    ids=[
        'with default config',
        'place_id in clause',
        'country_code in clause',
        'region_id in clause',
    ],
)
async def test_subscription_commission_handle_different_clauses(
        place_id, expected_response, taxi_eats_place_subscriptions,
):
    response = await taxi_eats_place_subscriptions.get(
        '/internal/eats-place-subscriptions/v1/get-subscription-commission',
        params={'place_id': place_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_response
