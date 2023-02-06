import pytest


# pylint: disable=C0103
pytestmark = [pytest.mark.pgsql('supportai_models', files=['models.sql'])]


@pytest.mark.parametrize(
    ('model_id', 'version', 'worker'),
    [
        ('detmir_dialog', '5', '01'),
        ('ya_drive_dialog', '1', '05'),
        ('justschool_dialog', '1', '04'),
    ],
)
@pytest.mark.set_worker(worker_id=5)
async def test_worker_id(web_app_client, model_id, version, worker):
    response = await web_app_client.get(
        f'/internal/supportai-models/v1/worker_id'
        f'?model_id={model_id}&model_version={version}',
    )
    assert response.status == 200
    content = await response.text()
    assert content == worker


@pytest.mark.set_worker(worker_id=5)
async def test_no_worker_id(web_app_client):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/worker_id'
        '?model_id=other_model&model_version=1',
    )
    assert response.status == 404

    response = await web_app_client.get(
        '/internal/supportai-models/v1/worker_id'
        '?model_id=russian_post_b2b_orders_dialog&model_version=2',
    )
    assert response.status == 404


@pytest.mark.set_worker(worker_id=5)
async def test_choice_worker_id(web_app_client):
    workers = []
    for _ in range(30):
        response = await web_app_client.get(
            '/internal/supportai-models/v1/worker_id?'
            'model_id=russian_post_b2b_orders_dialog&model_version=1',
        )
        assert response.status == 200
        workers.append(await response.text())

    assert '00' in workers
    assert '03' in workers


@pytest.mark.parametrize(
    ('model_id', 'version'),
    [
        ('detmir_dialog', '5'),
        ('ya_drive_dialog', '1'),
        ('justschool_dialog', '1'),
    ],
)
async def test_shard_id(web_app_client, model_id, version):
    response = await web_app_client.get(
        f'/internal/supportai-models/v1/shard_id'
        f'?model_id={model_id}&model_version={version}',
    )
    assert response.status == 200
    content = await response.json()
    assert 'shard_id' in content
    assert content['shard_id'] == 'shard1'


async def test_no_shard_id(web_app_client):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/shard_id?'
        'model_id=other_model&model_version=1',
    )
    assert response.status == 404

    response = await web_app_client.get(
        '/internal/supportai-models/v1/shard_id?'
        'model_id=russian_post_b2b_orders_dialog&model_version=2',
    )
    assert response.status == 404


async def test_choice_shard_id(web_app_client):
    shards = []
    for _ in range(30):
        response = await web_app_client.get(
            '/internal/supportai-models/v1/shard_id?'
            'model_id=russian_post_b2b_orders_dialog&model_version=1',
        )
        assert response.status == 200
        content = await response.json()
        shards.append(content['shard_id'])

    assert 'shard1' in shards
    assert 'shard2' in shards


async def test_ping(web_app_client):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/ping?model_id=detmir_dialog',
    )
    assert response.status == 200
