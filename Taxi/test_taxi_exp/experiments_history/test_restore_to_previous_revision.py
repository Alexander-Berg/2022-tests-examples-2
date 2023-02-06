import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize(
    'gen_func,init_func,update_func,get_func,restore_func',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.update_exp,
            helpers.get_experiment,
            helpers.restore_experiment,
            id='restore_exp',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.update_config,
            helpers.get_config,
            helpers.restore_config,
            id='restore_config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_restore_to_previous_revision(
        taxi_exp_client,
        gen_func,
        init_func,
        update_func,
        get_func,
        restore_func,
):
    # init exp
    experiment_body = gen_func(name=EXPERIMENT_NAME, description='version 1')

    await init_func(taxi_exp_client, experiment_body)

    # try to restore with no previous versions
    response = await restore_func(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=1,
        restore_to_previous=True,
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'RESTORE_ERROR',
        'message': (
            'Only one user-created revision found, '
            'cannot restore to previous. '
            'If you wish to revert non-user-made changes, please do so '
            'manually from the revisions tab.'
        ),
    }
    # update exp and change revision type to prestable
    experiment_body['description'] = 'version 2'
    experiment_body['last_modified_at'] = 1
    await update_func(taxi_exp_client, experiment_body)
    await db.set_change_type_in_rev(
        taxi_exp_client.app, rev=2, change_type='prestable',
    )

    response = await restore_func(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=2,
        restore_to_previous=True,
    )
    assert response.status == 400
    assert (await response.json()) == {
        'code': 'RESTORE_ERROR',
        'message': (
            'Only one user-created revision found, '
            'cannot restore to previous. '
            'If you wish to revert non-user-made changes, please do so '
            'manually from the revisions tab.'
        ),
    }

    # update exp twice more to have enough revisions
    for rev_num in range(2, 4):
        experiment_body['description'] = f'version {rev_num + 1}'
        experiment_body['last_modified_at'] = rev_num
        await update_func(taxi_exp_client, experiment_body)

    # set different change_type for rev=4 to check finding the right revision
    await db.set_change_type_in_rev(
        taxi_exp_client.app, rev=4, change_type='prestable',
    )

    # check correctly restoring to previous revision
    # starting from non-user-made version
    response = await restore_func(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=4,
        restore_to_previous=True,
    )
    assert response.status == 200
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['last_modified_at'] == 5
    assert response_body['description'] == 'version 1'

    # check correctly restoring to previous revision
    # starting from user-made version
    response = await restore_func(
        taxi_exp_client,
        name=EXPERIMENT_NAME,
        last_modified_at=5,
        restore_to_previous=True,
    )
    assert response.status == 200
    response_body = await get_func(taxi_exp_client, EXPERIMENT_NAME)
    assert response_body['last_modified_at'] == 6
    assert response_body['description'] == 'version 3'
