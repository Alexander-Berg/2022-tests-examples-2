import pytest

from test_taxi_exp.helpers import db

EXPERIMENT_NAME = 'experiment_to_uplift'
MODIFICATION = 'close'


@pytest.mark.parametrize(
    'default_value,response_status,response_message,expected_db_count',
    [
        pytest.param({'type': 'type'}, 200, '', 2, id='correct_default_value'),
        pytest.param(
            {'value': 10},
            400,
            'VALUE_VALIDATION_ERROR',
            1,
            id='wrong_default_value',
        ),
        pytest.param(
            {},
            400,
            'VALUE_VALIDATION_ERROR',
            1,
            id='empty_default_value_with_disabled_additional_properties',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['experiment_to_uplift.sql'])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
async def test_uplift_experiment_with_null_default_value(
        taxi_exp_client,
        default_value,
        response_status,
        response_message,
        expected_db_count,
):
    # check count
    assert await db.count(taxi_exp_client.app) == 1

    # uplift experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json={
            'experiment_name': EXPERIMENT_NAME,
            'last_updated_at': 1,
            'modification': MODIFICATION,
            'default_value': default_value,
        },
    )
    assert response.status == response_status
    body = await response.json()
    if response.status != 200:
        assert body['code'] == response_message

    # check
    assert await db.count(taxi_exp_client.app) == expected_db_count
