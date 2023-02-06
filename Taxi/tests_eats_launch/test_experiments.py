import pytest

LAUNCH_URL_CONFIGS = '/eats/v1/launch/v1/configs'
LAUNCH_URL_EXPERIMENTS = '/eats/v1/launch/v1/experiments'

TAXI_CONFIG = {'allow_unknown_platforms': True, 'translate_platform': []}

EXP3_CONFIGS = pytest.mark.experiments3(
    is_config=True,
    name='launch_config',
    consumers=['eda_ab_service'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[{'predicate': {'type': 'true'}, 'value': {'my_param1': 67890}}],
)

EXP3_EXPERIMENTS = pytest.mark.experiments3(
    name='launch_experiment',
    consumers=['eda_ab_service'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[{'predicate': {'type': 'true'}, 'value': {'my_param1': 12345}}],
)

CONFIG_RESPONSE = {
    'version': 1,
    'items': [{'name': 'launch_config', 'value': {'my_param1': 67890}}],
}

CONFIG_RESPONSE_TAXI_PHONE = {
    'version': 1,
    'items': [{'name': 'launch_config', 'value': {'res': True}}],
}

EXPERIMENT_RESPONSE = {
    'version': 1,
    'items': [{'name': 'launch_experiment', 'value': {'my_param1': 12345}}],
}


def build_headers(common_values):
    return {'X-Ya-Service-Ticket': common_values['mock_service_ticket']}


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=TAXI_CONFIG)
@pytest.mark.parametrize(
    ['param_launch_url'],
    [
        pytest.param(LAUNCH_URL_CONFIGS, id='configs'),
        pytest.param(LAUNCH_URL_EXPERIMENTS, id='experiments'),
    ],
)
async def test_exp_unknown_consumer(
        taxi_eats_launch, common_values, param_launch_url,
):
    data = {'consumer': 'valid_consumer', 'args': []}
    response = await taxi_eats_launch.post(
        param_launch_url, headers=build_headers(common_values), json=data,
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['code'] == 'consumer_not_found'


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=TAXI_CONFIG)
@pytest.mark.parametrize(
    ['param_launch_url', 'param_expected_response'],
    [
        pytest.param(
            LAUNCH_URL_CONFIGS,
            CONFIG_RESPONSE,
            marks=[EXP3_CONFIGS],
            id='configs',
        ),
        pytest.param(
            LAUNCH_URL_EXPERIMENTS,
            EXPERIMENT_RESPONSE,
            marks=[EXP3_EXPERIMENTS],
            id='experiments',
        ),
    ],
)
async def test_exp_ok(
        taxi_eats_launch,
        common_values,
        param_launch_url,
        param_expected_response,
):
    data = {'consumer': 'eda_ab_service', 'args': []}
    response = await taxi_eats_launch.post(
        param_launch_url, headers=build_headers(common_values), json=data,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == param_expected_response


@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=TAXI_CONFIG)
@pytest.mark.parametrize(
    ['param_launch_url', 'param_expected_response'],
    [
        pytest.param(
            LAUNCH_URL_CONFIGS,
            CONFIG_RESPONSE,
            marks=[EXP3_CONFIGS],
            id='configs',
        ),
        pytest.param(
            LAUNCH_URL_EXPERIMENTS,
            EXPERIMENT_RESPONSE,
            marks=[EXP3_EXPERIMENTS],
            id='experiments',
        ),
    ],
)
async def test_exp_ok_no_args(
        taxi_eats_launch,
        common_values,
        param_launch_url,
        param_expected_response,
):
    data = {'consumer': 'eda_ab_service'}
    response = await taxi_eats_launch.post(
        param_launch_url, headers=build_headers(common_values), json=data,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == param_expected_response


@pytest.mark.experiments3(
    is_config=True,
    name='launch_config',
    consumers=['eda_ab_service'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'personal_phone_id',
                    'arg_type': 'string',
                    'value': '5',
                },
            },
            'value': {'res': True},
        },
        {'predicate': {'type': 'true'}, 'value': {'res': False}},
    ],
)
@pytest.mark.config(EATS_LAUNCH_AB_PLATFORMS=TAXI_CONFIG)
async def test_exp_phone_id(taxi_eats_launch, common_values):
    data = {'consumer': 'eda_ab_service'}
    headers = build_headers(common_values)
    headers[
        'X-Eats-User'
    ] = 'user_id=1,personal_phone_id=2,personal_email_id=3,partner_user_id=4'
    headers['X-YaTaxi-User'] = (
        'personal_phone_id=5,personal_email_id=6,'
        + 'eats_user_id=7,eats_partner_user_id=8'
    )
    response = await taxi_eats_launch.post(
        LAUNCH_URL_CONFIGS, headers=headers, json=data,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == CONFIG_RESPONSE_TAXI_PHONE
