import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
        'settings': {
            'common': {
                'departments': {'market': {'map_to_namespace': 'market'}},
            },
        },
    },
)
@pytest.mark.parametrize(
    'name,last_modified_at,',
    [('single_experiment', 1), ('first_experiment', 3), ('first_config', 6)],
)
@pytest.mark.pgsql('taxi_exp', files=['experiments_to_remove.sql'])
async def test_delete_experiment_use_draft(
        taxi_exp_client, name, last_modified_at,
):
    # check count
    count_obj = await db.count(taxi_exp_client.app)

    response = await helpers.delete_exp_by_draft(
        taxi_exp_client,
        name=name,
        last_modified_at=last_modified_at,
        raw_answer=True,
    )
    assert response.status == 200
    body = await response.json()
    assert body['change_doc_id'] == f'delete_experiment_{name}'
    assert body['tplatform_namespace'] == 'market'
    assert body['data']['department'] == 'market'
    assert body['data']['experiment']['name'] == name

    await helpers.delete_exp_by_draft(
        taxi_exp_client, name=name, last_modified_at=last_modified_at,
    )

    # check
    assert await db.count(taxi_exp_client.app) == (count_obj - 1)
