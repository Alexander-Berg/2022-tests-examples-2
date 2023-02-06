import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'experiment_without_owners'


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={
                    'enabled': False,
                    'reaction_level': 'full',
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={
                    'enabled': True,
                    'reaction_level': 'full',
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={'enabled': True, 'reaction_level': 'log'},
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_update_experiment_with_owners(taxi_exp_client):
    exp_body = experiment.generate(
        name=EXPERIMENT_NAME, owners=['first', 'second'],
    )
    response = await helpers.init_exp(taxi_exp_client, exp_body)

    exp_body.pop('owners')
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={
            'name': EXPERIMENT_NAME,
            'last_modified_at': response['last_modified_at'],
        },
        json=exp_body,
    )

    assert response.status == 200, await response.text()
