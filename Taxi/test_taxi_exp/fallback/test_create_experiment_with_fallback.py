import pytest

from taxi_exp.util import pg_helpers
from taxi_exp.util import predicate_helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_fallback'


def _clean_and_get_rev(experiment_body):
    predicate_helpers.remove_ql(experiment_body)
    experiment_body.pop('removed', None)
    experiment_body.pop('owners', None)
    experiment_body.pop('watchers', None)
    experiment_body.pop('created', None)
    experiment_body.pop('last_manual_update', None)
    experiment_body.pop('biz_revision')
    rev = experiment_body.pop('last_modified_at')
    return experiment_body, rev


async def _count_fallbacks(app):
    query = 'SELECT COUNT(*) as count FROM clients_schema.fallbacks;'
    result = await pg_helpers.fetchrow(app['pool'], query)
    return result['count']


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_experiment_with_fallback(taxi_exp_client):
    experiment_body = experiment.generate(
        name=EXPERIMENT_NAME,
        fallback=experiment.make_fallback(
            short_description='Short description',
            what_happens_when_turn_off='Blackout',
            need_turn_off=True,
        ),
    )
    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == 200

    # get experiment
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200
    body = await response.json()
    body, last_modified_at = _clean_and_get_rev(body)
    assert body == experiment_body

    # get history
    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'revision': 1},
    )
    assert response.status == 200, await response.text()
    body = (await response.json())['body']
    body, last_modified_at = _clean_and_get_rev(body)
    assert body == experiment_body

    # get updates
    response = await taxi_exp_client.get(
        '/v1/experiments/updates/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 1, 'newer_than': last_modified_at - 1},
    )
    assert response.status == 200
    body = await response.json()
    assert len(body['experiments']) == 1
    exp_body = body['experiments'][0]
    exp_body, last_modified_at = _clean_and_get_rev(exp_body)
    assert exp_body == experiment_body

    # update experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': last_modified_at},
        json=experiment_body,
    )
    assert response.status == 200
    assert await _count_fallbacks(taxi_exp_client.app) == 1

    # get fallbacks
    response = await taxi_exp_client.get(
        '/v1/fallbacks/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    body = await response.json()
    assert body['fallbacks']
