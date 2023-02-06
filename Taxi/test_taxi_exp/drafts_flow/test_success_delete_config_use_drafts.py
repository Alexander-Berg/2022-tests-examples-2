import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_config_removing': True}},
        'settings': {
            'common': {
                'departments': {'market': {'map_to_namespace': 'market'}},
            },
        },
    },
)
@pytest.mark.parametrize(
    'name,last_modified_at,',
    [
        ('single_config', 1),
        ('object_with_duplicated_name', 3),
        ('enabled_config', 4),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['configs_to_remove.sql'])
async def test_delete_config_use_draft(
        taxi_exp_client, name, last_modified_at,
):
    # check count
    count_obj = await db.count(taxi_exp_client.app)

    response = await helpers.delete_config_by_draft(
        taxi_exp_client,
        name=name,
        last_modified_at=last_modified_at,
        raw_answer=True,
    )
    assert response.status == 200
    body = await response.json()
    assert body['change_doc_id'] == f'delete_config_{name}'
    assert body['tplatform_namespace'] == 'market'
    assert body['data']['department'] == 'market'
    assert body['data']['config']['name'] == name

    await helpers.delete_config_by_draft(
        taxi_exp_client, name=name, last_modified_at=last_modified_at,
    )

    # check
    assert await db.count(taxi_exp_client.app) == (count_obj - 1)
