import pytest

from taxi_exp.lib import trait_tags
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'biz_analytical'
SCHEMA = """additionalProperties: false
properties:
   enabled:
      type: boolean
"""
INIT_BODY = experiment.generate(
    clauses=[],
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    schema=SCHEMA,
)
NEW_BODY = experiment.generate(
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    clauses=[
        experiment.make_clause(
            'title', predicate=experiment.mod_sha1_predicate(), value={},
        ),
    ],
    schema=SCHEMA,
)
TWO_CLAUSES = experiment.generate(
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    clauses=[
        experiment.make_clause(
            'title', predicate=experiment.mod_sha1_predicate(), value={},
        ),
        experiment.make_clause(
            'title_2', predicate=experiment.mod_sha1_predicate(), value={},
        ),
    ],
    schema=SCHEMA,
)


async def _check_analytical_exists(taxi_exp_client, is_found, is_config=False):
    url = '/v1/experiments/' if not is_config else '/v1/configs/'
    response = await taxi_exp_client.get(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert ('analytical' in body['trait_tags']) == is_found

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'limit': 1, 'revision': body['last_modified_at']},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert ('analytical' in body['body']['trait_tags']) == is_found


@pytest.mark.parametrize('is_config', [True, False])
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'check_biz_revision': True,
                'enable_uplift_experiment': True,
                'remove_analytical': True,
            },
        },
    },
    EXP_EXTENDED_DRAFTS=[
        {'DRAFT_NAME': 'update_experiment', 'NEED_CHECKING_BODY': True},
    ],
)
async def test(taxi_exp_client, is_config):
    url = '/v1/experiments/' if not is_config else '/v1/configs/'

    # creation of experiment with stealing analytical tag
    response = await taxi_exp_client.post(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=INIT_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_analytical_exists(taxi_exp_client, False, is_config)

    # update of experiment with stealing analytical tag
    response = await taxi_exp_client.put(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=NEW_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_analytical_exists(taxi_exp_client, False, is_config)

    # update of experiment without stealing analytical tag
    response = await taxi_exp_client.put(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 2},
        json=TWO_CLAUSES,
    )
    assert response.status == 200, await response.text()
    await _check_analytical_exists(taxi_exp_client, True, is_config)

    # checking update draft of experiment with stealing analytical tag
    response = await taxi_exp_client.put(
        url + 'drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 3},
        json=NEW_BODY,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    exp_body_key = 'config' if is_config else 'experiment'
    assert body['data']['status_analytical_removing'] == 'were_removed'
    assert 'analytical' not in body['data'][exp_body_key]['trait_tags']
