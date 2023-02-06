import copy

import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'map_style'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={'features': {'common': {'check_biz_revision': True}}},
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_all_datetimes(taxi_exp_client):
    body = experiment.generate(
        action_time={
            'from': '2020-01-01T00:00:00+03:00',
            'to': '2023-01-01T00:00:00+03:00',
        },
        trait_tags=['analytical'],
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    get_body = await response.json()

    response = await taxi_exp_client.get(
        '/v1/experiments/updates/', headers={'X-Ya-Service-Ticket': '123'},
    )
    assert response.status == 200, await response.text()
    updates_body = (await response.json())['experiments'][0]

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'revision': 1},
    )
    assert response.status == 200, await response.text()
    history_body = (await response.json())['body']

    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    search_body = (await response.json())['experiments'][0]

    response = await taxi_exp_client.get(
        '/v1/experiments/revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    revisions_body = (await response.json())['revisions'][0]

    assert revisions_body['biz_revision'] == 1

    assert (
        get_body['match']['action_time']
        == updates_body['match']['action_time']
    )
    assert (
        get_body['match']['action_time']
        == history_body['match']['action_time']
    )

    assert get_body['last_manual_update'] == updates_body['last_manual_update']
    assert get_body['last_manual_update'] == history_body['last_manual_update']
    assert get_body['last_manual_update'] == search_body['last_manual_update']
    assert get_body['last_manual_update'] == revisions_body['updated']

    assert get_body['created'] == updates_body['created']
    assert get_body['created'] == history_body['created']
    assert get_body['created'] == search_body['created']

    put_body = copy.deepcopy(get_body)
    put_body['match']['predicate']['type'] = 'false'
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 1},
        json=put_body,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/experiments/revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    revisions_body = (await response.json())['revisions'][0]

    assert revisions_body['biz_revision'] == 2
