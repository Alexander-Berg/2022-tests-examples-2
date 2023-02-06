import pytest

from tests_eats_place_subscriptions import utils


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
@pytest.mark.parametrize(
    'place_ids, expected_response, ' 'expected_errors_metrics',
    [
        (
            [123, 125],
            {
                'subscriptions': [
                    {
                        'activated_at': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': False,
                        'next_is_trial': False,
                        'place_id': 123,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '2020-04-30T21:00:00+00:00',
                    },
                    {
                        'activated_at': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': True,
                        'is_trial': False,
                        'next_is_trial': False,
                        'place_id': 125,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'valid_until': '2020-05-01T03:00:00+00:00',
                    },
                ],
            },
            {'not_found_in_db': 0},
        ),
        (
            [123, 100, 101, 102, 103],
            {
                'subscriptions': [
                    {
                        'activated_at': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': False,
                        'next_is_trial': False,
                        'place_id': 123,
                        'tariff_info': {
                            'additional_commission': 1.44,
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '2020-04-30T21:00:00+00:00',
                    },
                ],
            },
            {'not_found_in_db': 4},
        ),
        ([], {'subscriptions': []}, {'not_found_in_db': 0}),
    ],
    ids=['green_flow', 'not_exist_places', 'empty_place_ids'],
)
async def test_get_subscriptions(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        place_ids,
        expected_response,
        expected_errors_metrics,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/admin/place-subscriptions/v1/subscriptions/get',
        json={'place_ids': place_ids},
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert (
        metrics[utils.SUBSCRIPTION_ERRORS_METRICS] == expected_errors_metrics
    )


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
async def test_get_subscriptions_no_tariff(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/admin/place-subscriptions/v1/subscriptions/get',
        json={'place_ids': [123]},
    )
    assert response.status_code == 500

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}
