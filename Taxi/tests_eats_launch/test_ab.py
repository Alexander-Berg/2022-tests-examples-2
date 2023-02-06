import pytest

LAUNCH_URL = '/eats/v1/launch/v1/ab'

CONFIG = {
    'allow_unknown_platforms': False,
    'translate_platform': [
        {'platform': 'android_app', 'application': 'eda_android_app'},
    ],
}

EXPERIMENTS = pytest.mark.experiments3(
    name='launch_experiment',
    consumers=['eda_ab_service'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[{'predicate': {'type': 'true'}, 'value': {'value': 'str1'}}],
)

EXPERIMENT_RESPONSE = {
    'payload': {
        'enabledTests': [
            {
                'id': 0,
                'slug': 'launch_experiment',
                'variant': {'id': 0, 'slug': 'str1'},
            },
        ],
    },
}

EXPERIMENTS_UNEXPECTED_VALUE = pytest.mark.experiments3(
    name='launch_experiment',
    consumers=['eda_ab_service'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[{'predicate': {'type': 'true'}, 'value': {'enabled': 'true'}}],
)


def build_headers_valid_platform(common_values):
    return {
        'X-Ya-Service-Ticket': common_values['mock_service_ticket'],
        'x-app-version': '1.1.1',
        'x-device-id': 'device1',
        'x-platform': 'android_app',
    }


def build_headers_invalid_platform(common_values):
    return {
        'X-Ya-Service-Ticket': common_values['mock_service_ticket'],
        'x-app-version': '1.1.1',
        'x-device-id': 'device1',
        'x-platform': 'invalid_platform',
    }


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=CONFIG)
async def test_ab_unknown_platform(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.get(
        LAUNCH_URL, headers=build_headers_invalid_platform(common_values),
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['code'] == 'invalid_platform'


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=CONFIG)
@EXPERIMENTS_UNEXPECTED_VALUE
async def test_ab_unexpected_value(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.get(
        LAUNCH_URL, headers=build_headers_valid_platform(common_values),
    )
    assert response.status_code == 200


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=CONFIG)
@EXPERIMENTS
async def test_ab_ok(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.get(
        LAUNCH_URL, headers=build_headers_valid_platform(common_values),
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == EXPERIMENT_RESPONSE


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=CONFIG)
@EXPERIMENTS
async def test_ab_parse_coordinates(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.get(
        LAUNCH_URL,
        params={'latitude': 12.345, 'longitude': 67.89},
        headers=build_headers_valid_platform(common_values),
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == EXPERIMENT_RESPONSE
