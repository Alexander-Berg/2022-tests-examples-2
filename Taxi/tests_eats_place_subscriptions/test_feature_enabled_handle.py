import pytest

from tests_eats_place_subscriptions import utils


@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.experiments3(filename='start_feat_flag.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.parametrize(
    'place_ids, response_places, expected_errors_metrics',
    [
        (
            [123, 125, 127, 128],
            {
                'with_enabled_feature': [128],
                'with_disabled_feature': [123, 125, 127],
            },
            {'not_found_in_db': 0},
        ),
        (
            [100, 101, 102, 103],
            {'with_enabled_feature': [], 'with_disabled_feature': []},
            {'not_found_in_db': 4},
        ),
        (
            [128, 128, 128],
            {'with_enabled_feature': [128], 'with_disabled_feature': []},
            {'not_found_in_db': 0},
        ),
        (
            [],
            {'with_enabled_feature': [], 'with_disabled_feature': []},
            {'not_found_in_db': 0},
        ),
    ],
    ids=['green_flow', 'not_exist_places', 'duplicates', 'empty_places'],
)
async def test_feature_enabled_handle(
        place_ids,
        response_places,
        expected_errors_metrics,
        taxi_eats_place_subscriptions,
        taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/internal/eats-place-subscriptions/v1/feature/enabled-for-places',
        json={'feature': 'personal_manager', 'place_ids': place_ids},
    )
    assert response.status_code == 200
    assert response.json() == {
        'feature': 'personal_manager',
        'places': response_places,
    }

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert (
        metrics[utils.SUBSCRIPTION_ERRORS_METRICS] == expected_errors_metrics
    )


@utils.set_tariffs_experiment({'tariffs': [{'type': 'free', 'features': []}]})
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='start_feat_flag.json')
async def test_feature_enabled_handle_with_empty_list(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/internal/eats-place-subscriptions/v1/feature/enabled-for-places',
        json={
            'feature': 'personal_manager',
            'place_ids': [123, 125, 127, 128],
        },
    )
    assert response.status_code == 500

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 1}


@pytest.mark.experiments3(filename='tariffs.json')
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
# turned off
# @pytest.mark.experiments3(filename='start_feat_flag.json')
async def test_feature_enabled_handle_turn_off(
        taxi_eats_place_subscriptions, taxi_eats_place_subscriptions_monitor,
):
    await taxi_eats_place_subscriptions.tests_control(reset_metrics=True)

    response = await taxi_eats_place_subscriptions.post(
        '/internal/eats-place-subscriptions/v1/feature/enabled-for-places',
        json={
            'feature': 'personal_manager',
            'place_ids': [123, 125, 127, 128],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'feature': 'personal_manager',
        'places': {'with_enabled_feature': [], 'with_disabled_feature': []},
    }

    metrics = await taxi_eats_place_subscriptions_monitor.get_metrics()
    assert metrics[utils.TARIFF_ERRORS_METRICS] == {'not_found_in_config': 0}
