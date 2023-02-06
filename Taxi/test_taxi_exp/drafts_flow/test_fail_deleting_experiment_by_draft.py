import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'existed_experiment'


@pytest.mark.parametrize(
    'experiment_body,expected_error_status,expected_error_body',
    [
        pytest.param(
            experiment.generate(
                name=EXPERIMENT_NAME + '_NOT', last_modified_at=1,
            ),
            404,
            {
                'message': (
                    'Experiment existed_experiment in tariff-editor '
                    'namespace with rev 1 not found'
                ),
                'code': 'EXPERIMENT_NOT_FOUND',
            },
            id='delete_non_existent_experiment',
        ),
        pytest.param(
            experiment.generate(
                name=EXPERIMENT_NAME, last_modified_at=1, enabled=True,
            ),
            400,
            {
                'message': (
                    'Experiment existed_experiment in tariff-editor namespace '
                    'is currently enabled. '
                    'Please disable experiment before deleting.'
                ),
                'code': 'DELETE_ENABLED_EXPERIMENT',
            },
            id='delete_disabled_experiment',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_fail_deleting_experiment(
        taxi_exp_client,
        experiment_body,
        expected_error_status,
        expected_error_body,
):
    await helpers.init_exp(taxi_exp_client, experiment_body)

    response = await helpers.delete_exp_by_draft(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=1,
        raw_answer=True,
    )
    assert response.status == expected_error_status
    response_body = await response.json()
    assert response_body == expected_error_body
