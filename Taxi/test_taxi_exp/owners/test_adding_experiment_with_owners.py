import logging

import pytest

from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'experiment_with_owners'
ERROR_MESSAGE = f'Owners for {EXPERIMENT_NAME} not found'


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
            200,
            {},
            False,
            marks=pytest.mark.config(
                EXP_OWNERS_SETTINGS={
                    'enabled': True,
                    'reaction_level': 'full',
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_adding_experiment_with_owners(
        taxi_exp_client, expected_code, expected_response, check_log, caplog,
):
    caplog.set_level(logging.WARNING)
    exp_body = experiment.generate_default()

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
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
