import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'expected_segmentation_method',
    [
        pytest.param(
            [],
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_save_salts': False}},
                },
            ),
        ),
        pytest.param(
            ['mod_sha1_with_salt'],
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_save_salts': True}},
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'url_part, doc_part',
    [('experiments', 'experiment'), ('configs', 'config')],
)
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.INIT_QUERY], files=('existed_experiment.sql',),
)
async def test_update(
        taxi_exp_client, url_part, doc_part, expected_segmentation_method,
):
    experiment_body = experiment.generate(
        clauses=[
            experiment.make_clause(
                'title',
                predicate=experiment.mod_sha1_predicate(salt='abbbbb'),
            ),
        ],
        default_value={},
    )
    name = f'existed_{doc_part}'
    params = {'name': name, 'last_modified_at': 1}

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

    apply_request = body['data']
    response = await taxi_exp_client.put(
        f'/v1/{url_part}/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=apply_request,
    )
    assert response.status == 200

    response = await db.get_salts(taxi_exp_client.app)
    assert [
        item['segmentation_method'] for item in response
    ] == expected_segmentation_method
