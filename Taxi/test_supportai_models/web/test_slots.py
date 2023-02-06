import pytest


@pytest.mark.config(
    SUPPORTAI_MODELS_SETTINGS={
        'shards': [
            {'shard_id': 'shard1', 'slot_count': 8},
            {'shard_id': 'shard2', 'slot_count': 2},
        ],
    },
)
@pytest.mark.pgsql('supportai_models', files=['models.sql'])
async def test_get_free_slots(web_app_client):
    response = await web_app_client.get('/v1/slots/free')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 1
    slot = content['slots'][0]

    assert slot['shard_id'] == 'shard2'
    assert slot['worker_id'] == 1


@pytest.mark.pgsql('supportai_models', files=['models.sql'])
async def test_get_slots_for_model(web_app_client):
    response = await web_app_client.get('/v1/slots?model_id=3')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 3


@pytest.mark.config(
    SUPPORTAI_MODELS_SETTINGS={
        'shards': [
            {'shard_id': 'shard1', 'slot_count': 8},
            {'shard_id': 'shard2', 'slot_count': 2},
        ],
    },
)
@pytest.mark.pgsql('supportai_models', files=['models.sql'])
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
        json={'model_id': '1', 'shard_id': 'shard2', 'worker_id': 2},
    )

    assert response.status == 400


@pytest.mark.pgsql('supportai_models', files=['models.sql'])
async def test_slot_unlock(web_app_client):
    response = await web_app_client.post('/v1/slots/7/unlock')

    assert response.status == 200

    response = await web_app_client.get('/v1/slots?model_id=3')
    assert response.status == 200

    content = await response.json()
    assert len(content['slots']) == 2
