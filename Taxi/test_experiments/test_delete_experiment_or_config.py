import pytest

from test_taxi_exp.helpers import db


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_config_removing': True,
                'enable_experiment_removing': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'name,remove_by,last_modified_at,',
    [
        ('single_experiment', 'experiments', 1),
        ('single_config', 'configs', 2),
        ('first_experiment', 'experiments', 3),
        ('first_experiment', 'configs', 4),
        ('first_config', 'configs', 5),
        ('first_config', 'experiments', 6),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['experiments_to_remove.sql'])
async def test_delete_experiment_or_config(
        taxi_exp_client, name, remove_by, last_modified_at,
):
    # check count
    count_obj = await db.count(taxi_exp_client.app)

    response = await taxi_exp_client.delete(
        f'/v1/{remove_by}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name, 'last_modified_at': last_modified_at},
    )
    assert response.status == 200

    # check
    assert await db.count(taxi_exp_client.app) == (count_obj - 1)
