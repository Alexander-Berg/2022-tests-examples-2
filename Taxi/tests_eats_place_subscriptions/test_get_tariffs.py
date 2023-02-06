import pytest

from tests_eats_place_subscriptions import utils


@pytest.mark.experiments3(filename='tariffs.json')
async def test_get_tariffs(taxi_eats_place_subscriptions):
    response = await taxi_eats_place_subscriptions.get(
        '/4.0/restapp-front/v1/place-subscriptions/v1/get-tariffs',
        headers={'X-YaEda-PartnerId': '1234'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'tariffs': [
            {
                'type': 'business',
                'features': ['daily_billing', 'sorry', 'boss_bot'],
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
                'fix_cost_rules': {
                    'bundle_size': 3,
                    'bundle_cost': 1299.0,
                    'extra_cost': 500.0,
                },
                'additional_commission': 1.44,
                'currency': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
            },
            {'type': 'free', 'features': ['weekly_billing']},
        ],
    }


@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
@pytest.mark.parametrize(
    'place_id, expected_tariffs',
    [
        (
            123,
            [
                {
                    'type': 'business',
                    'features': ['daily_billing', 'sorry', 'boss_bot'],
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
                    'fix_cost_rules': {
                        'bundle_size': 3,
                        'bundle_cost': 1299.0,
                        'extra_cost': 500.0,
                    },
                    'additional_commission': 1.44,
                    'currency': {
                        'code': 'RUB',
                        'sign': '₽',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'text': 'руб.',
                    },
                },
                {'type': 'free', 'features': ['weekly_billing']},
            ],
        ),
        (124, [{'type': 'free', 'features': ['weekly_billing']}]),
    ],
    ids=['rest', 'not_rest'],
)
async def test_admin_get_tariffs(
        taxi_eats_place_subscriptions, place_id, expected_tariffs, mockserver,
):

    response = await taxi_eats_place_subscriptions.get(
        '/admin/place-subscriptions/v1/tariffs/list',
        params={'place_id': place_id},
    )
    assert response.status_code == 200
    assert response.json() == {'tariffs': expected_tariffs}


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_admin_get_tariffs_no_tariff(
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
        mockserver,
):
    @mockserver.json_handler(utils.CATALOG_STORAGE_URL)
    def mock_catalog(request):
        return mockserver.make_response(json={}, status=200)

    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    place_id = 123
    response = await taxi_eats_place_subscriptions.get(
        '/admin/place-subscriptions/v1/tariffs/list',
        params={'place_id': place_id},
    )
    assert not mock_catalog.has_calls
    assert response.status_code == 500

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}
