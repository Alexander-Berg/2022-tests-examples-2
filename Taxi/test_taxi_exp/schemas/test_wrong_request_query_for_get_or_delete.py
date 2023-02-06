import pytest

from test_taxi_exp import helpers

EXPERIMENT_NAME = 'experiment'
EMPTY_NAME = ''


@pytest.mark.parametrize(
    'test_func',
    [
        pytest.param(helpers.get_schema_draft),
        pytest.param(helpers.delete_schema_draft),
    ],
)
@pytest.mark.parametrize(
    'exp_name,expected_error',
    [
        pytest.param(
            EXPERIMENT_NAME,
            {
                'code': 'BOTH_CONFIG_AND_EXP_NAME',
                'message': (
                    'Experiment name and config name cannot both be filled'
                ),
            },
        ),
        pytest.param(
            EMPTY_NAME,
            {
                'code': 'NEITHER_CONFIG_NOR_EXP_NAME',
                'message': (
                    'Either experiment name or config name must be filled'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_wrong_request_params(
        taxi_exp_client, test_func, exp_name, expected_error,
):
    response = await test_func(taxi_exp_client, name=exp_name, copy_name=True)
    # check error
    assert response.status == 400
    response_body = await response.json()
    assert response_body == expected_error
