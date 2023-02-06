import pytest

from test_taxi_exp.helpers import experiment

NAME = 'config_for_restore'


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_restore_config(taxi_exp_client):
    # add config
    body = experiment.generate_config(
        clauses=[experiment.make_clause('title-v1')],
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200

    # update config
    body = experiment.generate_config(
        clauses=[experiment.make_clause('title-v2')],
    )
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 1},
        json=body,
    )
    assert response.status == 200

    # restore config
    response = await taxi_exp_client.post(
        '/v1/configs/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 2, 'revision': 1},
    )
    assert response.status == 200, await response.text()

    # recovery check
    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body['clauses'] == [
        {'predicate': {'type': 'true'}, 'title': 'title-v1', 'value': {}},
    ]
