import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'init_func,verb_init_func,update_func',
    [
        pytest.param(
            helpers.success_init_exp_by_draft,
            helpers.verbose_init_exp_by_draft,
            helpers.update_exp_by_draft,
            id='create_update_exp_with_namespace_by_draft',
        ),
        pytest.param(
            helpers.init_exp,
            None,
            helpers.update_exp,
            id='create_update_exp_with_namespace_direct',
        ),
    ],
)
@pytest.mark.parametrize(
    'shutdown_mode,time_step,percentage_step,error',
    [
        pytest.param('gradual_shutdown', 30000, 10, None, id='valid_fields'),
        pytest.param(
            'gradual_shutdown',
            1,
            101,
            {
                'code': 'BAD_GRADUAL_SHUTDOWN_MODE_FIELDS',
                'message': (
                    'gradual_shutdown_percentage_step field must represent a '
                    'percentage for gradual_shutdown'
                ),
            },
            id='percentage_step_too_big',
        ),
        pytest.param(
            'gradual_shutdown',
            -1,
            10,
            {
                'code': 'BAD_GRADUAL_SHUTDOWN_MODE_FIELDS',
                'message': (
                    'gradual_shutdown_time_step field must be '
                    'positive for gradual_shutdown'
                ),
            },
            id='time_step_negative',
        ),
        pytest.param(
            'gradual_shutdown',
            10,
            -1,
            {
                'code': 'BAD_GRADUAL_SHUTDOWN_MODE_FIELDS',
                'message': (
                    'gradual_shutdown_percentage_step field must represent a '
                    'percentage for gradual_shutdown'
                ),
            },
            id='percentage_step_negative',
        ),
        pytest.param(
            'instant_shutdown',
            10000,
            10,
            {
                'code': 'BAD_GRADUAL_SHUTDOWN_MODE_FIELDS',
                'message': (
                    'gradual_shutdown_and_step and '
                    'gradual_shutdown_percentage_step cannot be filled '
                    'for any shutdown_mode other than gradual_shutdown'
                ),
            },
            id='non_empty_fields_with_different_shutdown_mode',
        ),
    ],
)
@pytest.mark.now('2022-02-22T22:22:22')
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.config(EXP_BLOCK_SAVING_ENABLED_EXPERIMENT={})
async def test_create_update_exp_with_gradual_shutdown(
        taxi_exp_client,
        init_func,
        verb_init_func,
        update_func,
        shutdown_mode,
        time_step,
        percentage_step,
        error,
):
    # init exp with gradual_shutdown
    experiment_body = experiment.generate(
        name=EXPERIMENT_NAME,
        last_modified_at=1,
        action_time={
            'from': '2022-02-20T22:22:22+03:00',
            'to': '2022-02-21T22:22:22+03:00',
        },
        shutdown_mode=shutdown_mode,
        gradual_shutdown_time_step=time_step,
        gradual_shutdown_percentage_step=percentage_step,
    )
    if error:
        if verb_init_func:
            response_body = await verb_init_func(
                taxi_exp_client, experiment_body,
            )
        else:
            response = await init_func(
                taxi_exp_client, experiment_body, raw_answer=True,
            )
            response_body = await response.json()
    else:
        response_body = await init_func(taxi_exp_client, experiment_body)
    # check errors
    if error:
        assert response_body == error
        return

    # check shutdown_mode and disable_percentage
    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['shutdown_mode'] == shutdown_mode
    assert response_body['match']['disable_percentage'] == 40.0
    assert (
        response_body['match']['fully_disabled_at']
        == '2022-02-25T01:22:22+03:00'
    )
    # check correct values in get_updates
    response_body = await helpers.get_updates(taxi_exp_client)
    assert (
        response_body['experiments'][0]['match']['disable_percentage'] == 40.0
    )
    assert (
        response_body['experiments'][0]['match']['fully_disabled_at']
        == '2022-02-25T01:22:22+03:00'
    )
    # check correct values in get
    response_body = await helpers.get_experiment(
        taxi_exp_client, name=EXPERIMENT_NAME,
    )
    assert response_body['match']['disable_percentage'] == 40.0
    assert response_body['gradual_shutdown_settings']['time_step'] == time_step
    assert (
        response_body['gradual_shutdown_settings']['percentage_step']
        == percentage_step
    )
    assert (
        response_body['match']['fully_disabled_at']
        == '2022-02-25T01:22:22+03:00'
    )

    experiment_body['description'] = 'it just works'

    # check update and correct values afterwards
    response_body = await update_func(taxi_exp_client, body=experiment_body)

    assert response_body['description'] == 'it just works'
    assert response_body['match']['disable_percentage'] == 40.0
    assert response_body['gradual_shutdown_settings']['time_step'] == time_step
    assert (
        response_body['gradual_shutdown_settings']['percentage_step']
        == percentage_step
    )

    await helpers.restore_experiment(
        taxi_exp_client, EXPERIMENT_NAME, last_modified_at=2, revision=1,
    )

    response_body = await helpers.get_experiment(
        taxi_exp_client, name=EXPERIMENT_NAME,
    )
    assert response_body['match']['disable_percentage'] == 40.0
    assert response_body['gradual_shutdown_settings']['time_step'] == time_step
    assert (
        response_body['gradual_shutdown_settings']['percentage_step']
        == percentage_step
    )
