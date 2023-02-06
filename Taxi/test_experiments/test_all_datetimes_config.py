import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'map_style'


@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_all_datetimes(taxi_exp_client):
    body = experiment.generate_config()

    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    get_body = await response.json()

    response = await taxi_exp_client.get(
        '/v1/configs/updates/', headers={'X-Ya-Service-Ticket': '123'},
    )
    assert response.status == 200, await response.text()
    updates_body = (await response.json())['configs'][0]

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'revision': 1},
    )
    assert response.status == 200, await response.text()
    history_body = (await response.json())['body']

    response = await taxi_exp_client.get(
        '/v1/configs/list/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    search_body = (await response.json())['configs'][0]

    response = await taxi_exp_client.get(
        '/v1/configs/revisions/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    revisions_body = (await response.json())['revisions'][0]

    assert get_body['last_manual_update'] == updates_body['last_manual_update']
    assert get_body['last_manual_update'] == history_body['last_manual_update']
    assert get_body['last_manual_update'] == search_body['last_manual_update']
    assert get_body['last_manual_update'] == revisions_body['updated']

    assert get_body['created'] == updates_body['created']
    assert get_body['created'] == history_body['created']
    assert get_body['created'] == search_body['created']
