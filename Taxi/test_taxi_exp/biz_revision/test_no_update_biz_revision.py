import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

ALWAYS_BIZ_REVISION = 1

EXPERIMENT_NAME = 'biz'
INIT_BODY = experiment.generate(
    clauses=[],
    trait_tags=[],
    default_value={},
    schema="""additionalProperties: false
properties:
   enabled:
      type: boolean
""",
)
NEW_BODY = experiment.generate(
    trait_tags=[], clauses=[experiment.make_clause('title')],
)
EXP_BODY_FOR_DRAFT = experiment.generate(
    trait_tags=[],
    clauses=[experiment.make_clause('draft_title')],
    default_value={'enabled': False},
)
CLOSED_BODY = experiment.generate(
    trait_tags=[], clauses=[experiment.make_clause('closed_title')],
)
NEW_CONFIG_BODY = experiment.generate_config(
    trait_tags=[], clauses=[experiment.make_clause('config_title')],
)
DRAFT_CONFIG_BODY = experiment.generate_config(
    trait_tags=[], clauses=[experiment.make_clause('config_draft_title')],
)


async def _check_revision(taxi_exp_client, number, is_config=False):
    url = '/v1/experiments/' if not is_config else '/v1/configs/'
    response = await taxi_exp_client.get(
        url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['biz_revision'] == number

    response = await taxi_exp_client.get(
        url + 'updates/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'limit': 1, 'newer_than': body['last_modified_at'] - 1},
    )
    assert response.status == 200, await response.text()
    if not is_config:
        assert (await response.json())['experiments'][0][
            'biz_revision'
        ] == number
    else:
        assert (await response.json())['configs'][0]['biz_revision'] == number

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'limit': 1, 'revision': body['last_modified_at']},
    )
    assert response.status == 200, await response.text()
    assert (await response.json())['body']['biz_revision'] == number

    response = await taxi_exp_client.get(
        url + 'list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'show_closed': 'True'},
    )
    assert response.status == 200, await response.text()
    if not is_config:
        assert (await response.json())['experiments'][0][
            'biz_revision'
        ] == number
    else:
        assert (await response.json())['configs'][0]['biz_revision'] == number


@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'check_biz_revision': True,
                'enable_uplift_experiment': True,
            },
        },
    },
)
async def test_biz_revizion(taxi_exp_client):
    # create
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=INIT_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # disable
    response = await taxi_exp_client.post(
        '/v1/experiments/disable/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # enable
    response = await taxi_exp_client.post(
        '/v1/experiments/enable/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 2},
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # restore
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 3, 'revision': 1},
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # update
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 4},
        json=NEW_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # update experiment by draft
    # check darft
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 5},
        json=EXP_BODY_FOR_DRAFT,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['data']['status_biz_revision'] == 'no_change'
    # apply darft
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 5},
        json=body['data'],
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # uplifting
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'X-Ya-Service-Ticket': '123'},
        json={
            'experiment_name': EXPERIMENT_NAME,
            'last_updated_at': 6,
            'default_value': {},
        },
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION, is_config=True)

    # update closed
    response = await taxi_exp_client.put(
        '/v1/closed-experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 8},
        json=CLOSED_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # update closed experiment by draft
    # check darft
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 9},
        json=EXP_BODY_FOR_DRAFT,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['data']['status_biz_revision'] == 'no_change'
    # apply darft
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 9},
        json=body['data'],
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION)

    # update config
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 7},
        json=NEW_CONFIG_BODY,
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION, is_config=True)

    # update config by draft
    # check darft
    response = await taxi_exp_client.put(
        '/v1/configs/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 11},
        json=DRAFT_CONFIG_BODY,
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['data']['status_biz_revision'] == 'no_change'
    # apply darft
    response = await taxi_exp_client.put(
        '/v1/configs/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 11},
        json=body['data'],
    )
    assert response.status == 200, await response.text()
    await _check_revision(taxi_exp_client, ALWAYS_BIZ_REVISION, is_config=True)
