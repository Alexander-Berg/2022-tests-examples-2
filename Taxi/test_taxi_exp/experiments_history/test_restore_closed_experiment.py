import pytest


from taxi_exp.lib import constants
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'closed_for_restore'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.now('2020-11-01T23:59:59+03:00')
async def test_restore_closed_experiment(taxi_exp_client):
    # add experiment
    body = experiment.generate_default(
        action_time={
            'from': '2020-01-01T00:00:00+03:00',
            'to': '2020-12-31T23:59:59+03:00',
        },
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    # make it closed
    data = {
        'experiment_name': NAME,
        'last_updated_at': 1,
        'modification': 'close',
    }
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'X-Ya-Service-Ticket': '123'},
        json=data,
    )
    assert response.status == 200, await response.text()
    # check uplifting
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert (
        response_body['match']['action_time']['from']
        == constants.EPOCH_START_STR
    )
    assert (
        response_body['match']['action_time']['to'] == constants.EPOCH_END_STR
    )

    # update closed
    body = experiment.generate_default(
        clauses=[experiment.make_clause('title')], closed=True,
    )
    response = await taxi_exp_client.put(
        '/v1/closed-experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 3},
        json=body,
    )
    assert response.status == 200, await response.text()

    assert len(await db.get_experiments_history(taxi_exp_client.app)) == 4

    # restore closed experiment
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 4, 'revision': 3},
    )
    assert response.status == 200

    # recovery check
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body['clauses'] == [
        {'predicate': {'type': 'true'}, 'title': 'default', 'value': {}},
    ]
    assert (
        response_body['match']['action_time']['from']
        == constants.EPOCH_START_STR
    )
    assert (
        response_body['match']['action_time']['to'] == constants.EPOCH_END_STR
    )
