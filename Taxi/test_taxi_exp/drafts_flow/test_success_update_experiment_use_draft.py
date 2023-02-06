import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'existed_experiment'


@pytest.mark.parametrize(
    'experiment_body',
    [
        pytest.param(
            experiment.generate(name=EXPERIMENT_NAME, last_modified_at=1),
            id='create_by_default',
        ),
        pytest.param(
            experiment.generate(
                name=EXPERIMENT_NAME, is_technical=True, last_modified_at=1,
            ),
            id='is_technical_true',
        ),
        pytest.param(
            experiment.generate(
                name=EXPERIMENT_NAME, is_technical=False, last_modified_at=1,
            ),
            id='is_technical_false',
        ),
        pytest.param(
            experiment.generate(
                name=EXPERIMENT_NAME, financial=None, last_modified_at=1,
            ),
            id='is_technical_false',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'existed_experiment.sql'))
async def test_update_experiment(taxi_exp_client, experiment_body):
    response_body = await helpers.update_exp_by_draft(
        taxi_exp_client, experiment_body,
    )

    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['last_modified_at'] == 2
    assert 'is_technical' not in response_body
    assert response_body['financial'] is True
