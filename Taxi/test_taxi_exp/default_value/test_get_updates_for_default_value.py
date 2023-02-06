import pytest

from test_taxi_exp import helpers


@pytest.mark.parametrize(
    'check_expressions',
    [
        pytest.param(
            [
                (
                    lambda result: len(result['experiments']) == 1,
                    'experiment must be one',
                ),
                (
                    lambda result: (
                        result['experiments'][0]['default_value'] is None
                    ),
                    'default value must be None',
                ),
            ],
            marks=pytest.mark.pgsql(
                'taxi_exp',
                files=['create_experiment_with_empty_default_value.sql'],
            ),
            id='empty_default_value',
        ),
        pytest.param(
            [
                (
                    lambda result: len(result['experiments']) == 1,
                    'experiment must be one',
                ),
                (
                    lambda result: (
                        result['experiments'][0]['default_value'] == {}
                    ),
                    'default value must be {}',
                ),
            ],
            marks=pytest.mark.pgsql(
                'taxi_exp',
                files=['create_experiment_with_nonempty_default_value.sql'],
            ),
            id='nonempty_default_value',
        ),
    ],
)
async def test(taxi_exp_client, check_expressions):

    result = await helpers.get_updates(taxi_exp_client, newer_than=0)
    for check, text in check_expressions:
        assert check(result), text
