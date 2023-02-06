import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,verb_init_func,update_func',
    [
        pytest.param(
            experiment.generate,
            helpers.success_init_exp_by_draft,
            helpers.verbose_init_exp_by_draft,
            helpers.update_exp_by_draft,
            id='exp_by_draft',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.success_init_config_by_draft,
            helpers.verbose_init_config_by_draft,
            helpers.update_config_by_draft,
            id='config_by_draft',
        ),
    ],
)
@pytest.mark.parametrize(
    'create_department,fail_create,update_department,fail_update,error_body',
    [
        pytest.param(
            '',
            True,
            None,
            None,
            {
                'code': 'EMPTY_DEPARTMENT',
                'message': (
                    'Empty department is no longer acceptable, either add '
                    'a valid department or use "common"'
                ),
            },
            id='create_with_empty_department',
        ),
        pytest.param(
            'commando',
            False,
            '',
            True,
            {
                'code': 'EMPTY_DEPARTMENT',
                'message': (
                    'Empty department is no longer acceptable, either add '
                    'a valid department or use "common"'
                ),
            },
            id='update_with_empty_department',
        ),
        pytest.param(
            'common',
            False,
            'rare',
            True,
            {
                'code': 'BAD_DEPARTMENT',
                'message': (
                    'Department rare not registered in EXP3_ADMIN_CONFIG'
                ),
            },
            id='update_with_unregistered_department',
        ),
        pytest.param(
            'common',
            False,
            'commando',
            False,
            None,
            id='create_and_update_with_valid_deparments',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {
                'departments': {
                    'common': {'map_to_namespace': 'market'},
                    'commando': {'map_to_namespace': 'taxi'},
                },
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_create_update_exp_with_department(
        taxi_exp_client,
        gen_func,
        init_func,
        verb_init_func,
        update_func,
        create_department,
        update_department,
        fail_update,
        fail_create,
        error_body,
):
    # create
    experiment_body = gen_func(
        name=EXPERIMENT_NAME, department=create_department, last_modified_at=1,
    )
    if fail_create:
        response_body = await verb_init_func(
            taxi_exp_client, experiment_body, namespace=None,
        )
        assert response_body == error_body
        return

    response_body = await init_func(
        taxi_exp_client, experiment_body, namespace=None,
    )

    assert response_body['name'] == EXPERIMENT_NAME
    assert response_body['department'] == create_department

    # update
    experiment_body['department'] = update_department

    response = await update_func(
        taxi_exp_client, experiment_body, raw_answer=True, namespace=None,
    )

    if fail_update:
        assert response.status == 400
        assert (await response.json()) == error_body
        return

    assert response.status == 200
    response_body = await response.json()
    assert response_body['data']['department'] == 'common'
    assert response_body['tplatform_namespace'] == 'market'

    response_body = await update_func(
        taxi_exp_client, experiment_body, namespace=None,
    )

    assert response_body['department'] == 'commando'
