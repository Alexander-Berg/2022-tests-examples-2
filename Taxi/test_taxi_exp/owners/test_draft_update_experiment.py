import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'experiment_without_owners'
ERROR_MESSAGE = (
    f'Need to specify owners for experiment/config {EXPERIMENT_NAME}'
)


@pytest.mark.parametrize(
    'expected_code, expected_response, check_log',
    [
        pytest.param(
            200,
            {},
            False,
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={
                    'enabled': False,
                    'reaction_level': 'full',
                },
            ),
        ),
        pytest.param(
            400,
            {'code': 'NOT_FILLED_OWNERS', 'message': ERROR_MESSAGE},
            True,
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={
                    'enabled': True,
                    'reaction_level': 'full',
                },
            ),
        ),
        pytest.param(
            200,
            {},
            True,
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={'enabled': True, 'reaction_level': 'log'},
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_update_experiment_with_owners(
        taxi_exp_client, expected_code, expected_response, check_log, caplog,
):
    exp_body = experiment.generate(
        name=EXPERIMENT_NAME, owners=['first', 'second'],
    )
    response = await helpers.init_exp(taxi_exp_client, exp_body)

    exp_body.pop('owners')
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={
            'name': EXPERIMENT_NAME,
            'last_modified_at': response['last_modified_at'],
        },
        json=exp_body,
    )

    if check_log:
        for record in caplog.records:
            if record.message == ERROR_MESSAGE:
                break
        else:
            assert False, 'Not found message in log'

    assert response.status == expected_code
    if expected_code > 200:
        assert await response.json() == expected_response
