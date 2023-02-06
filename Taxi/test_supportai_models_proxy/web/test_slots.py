import pytest


# pylint: disable=C0103
pytestmark = [
    pytest.mark.pgsql('supportai_models_proxy', files=['models.sql']),
]


async def test_get_free_slots(web_app_client):
    response = await web_app_client.get('/v1/slots/free')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 3


async def test_get_slots_for_model(web_app_client):
    response = await web_app_client.get('/v1/slots?model_id=1')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 1

    assert content['slots'][0]['shard_id'] == 'shard1'
    assert content['slots'][0]['worker_id'] == 0


async def test_slot_lock(web_app_client):
    response = await web_app_client.post(
        '/v1/slots/lock',
        json={'model_id': '1', 'shard_id': 'shard2', 'worker_id': 1},
    )

    assert response.status == 200

    response = await web_app_client.get('/v1/slots?model_id=1')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 2

    response = await web_app_client.post(
        '/v1/slots/lock',
        json={'model_id': '1', 'shard_id': 'shard3', 'worker_id': 1},
    )

    assert response.status == 400

    response = await web_app_client.post(
        '/v1/slots/lock',
        json={'model_id': '1', 'shard_id': 'shard1', 'worker_id': 2},
    )

    assert response.status == 400


async def test_slot_unlock(web_app_client):
    response = await web_app_client.post('/v1/slots/1/unlock')

    assert response.status == 200

    response = await web_app_client.get('/v1/slots?model_id=1')
    assert response.status == 200

    content = await response.json()
    assert not content['slots']
