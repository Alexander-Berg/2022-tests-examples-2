import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'url_part, doc_part',
    [('experiments', 'experiment'), ('configs', 'config')],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_save_salts': True,
                'enable_write_segmentation_for_new_salts': True,
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_update(taxi_exp_client, taxi_config, url_part, doc_part):
    name = f'existed_{doc_part}'
    experiment_body = experiment.generate(
        clauses=[
            experiment.make_clause(
                'title',
                predicate=experiment.mod_sha1_predicate(salt='abbbbb'),
            ),
        ],
        default_value={},
        name=name,
    )
    if url_part == 'experiments':
        last_body = await helpers.init_exp(taxi_exp_client, experiment_body)
    else:
        last_body = await helpers.init_config(taxi_exp_client, experiment_body)
    taxi_config.set_values(
        {
            'EXP3_ADMIN_CONFIG': {
                'features': {
                    'common': {
                        'enable_save_salts': True,
                        'enable_write_segmentation_for_new_salts': True,
                        'enable_segmentation_for_front': True,
                    },
                },
            },
        },
    )
    await taxi_exp_client.app.config.refresh_cache()
    params = {'name': name, 'last_modified_at': last_body['last_modified_at']}

    response = await taxi_exp_client.put(
        f'/v1/{url_part}/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['change_doc_id'] == f'update_{doc_part}_{name}'
    assert 'diff' in body
    assert body['diff']['new']['clauses'] == body['diff']['current']['clauses']
