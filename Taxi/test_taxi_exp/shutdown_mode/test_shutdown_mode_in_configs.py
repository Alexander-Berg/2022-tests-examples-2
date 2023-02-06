import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func',
    [
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            id='create_config_with_shutdown_mode_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            id='create_config_with_shutdown_mode_direct',
        ),
    ],
)
@pytest.mark.now('2022-02-22T22:22:22')
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_update_exp_with_gradual_shutdown(
        taxi_exp_client, gen_func, init_func,
):

    # init config with incorrect shutdown_mode
    experiment_body = gen_func(
        name=EXPERIMENT_NAME,
        last_modified_at=1,
        action_time={
            'from': '2022-02-20T22:22:22+03:00',
            'to': '2022-02-21T22:22:22+03:00',
        },
        shutdown_mode='gradual_shutdown',
    )

    response_body = await init_func(taxi_exp_client, experiment_body)
    # check that shutdown_mode is correct
    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['shutdown_mode'] == 'config_no_shutdown'
