import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'body,expected_default_value',
    [
        pytest.param(
            experiment.generate(name='test', default_value={}),
            {},
            id='with_filled_default_value',
        ),
        pytest.param(
            experiment.generate(name='test', default_value=None),
            None,
            id='with_None_default_value',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(taxi_exp_client, body, expected_default_value):
    await helpers.init_exp(taxi_exp_client, body)

    result = await helpers.get_updates(taxi_exp_client, newer_than=0)
    assert len(result['experiments']) == 1
    assert result['experiments'][0]['default_value'] == expected_default_value
