import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'experiment_body',
    [
        pytest.param(
            experiment.generate(name=EXPERIMENT_NAME), id='create_by_default',
        ),
        pytest.param(
            experiment.generate(name=EXPERIMENT_NAME, is_technical=True),
            id='is_technical_true',
        ),
        pytest.param(
            experiment.generate(name=EXPERIMENT_NAME, is_technical=False),
            id='is_technical_false',
        ),
        pytest.param(
            experiment.generate(name=EXPERIMENT_NAME, financial=None),
            id='financial_null',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_experiment(taxi_exp_client, experiment_body):
    response_body = await helpers.success_init_exp_by_draft(
        taxi_exp_client, experiment_body,
    )

    assert response_body['name'] == EXPERIMENT_NAME
    assert 'is_technical' not in response_body
    assert response_body['financial'] is True
