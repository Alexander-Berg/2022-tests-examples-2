import pytest


# pylint: disable=C0103
pytestmark = [pytest.mark.pgsql('supportai_models', files=['models.sql'])]


async def test_get_all_models(web_app_client):
    response = await web_app_client.get('/internal/supportai-models/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 11
    model = content['models'][0]
    assert 'title' in model
    assert 'slug' in model
    assert 'version' in model
    assert 'language' in model
    assert 'model_arch' in model


pytestmark = [pytest.mark.pgsql('supportai_models', files=['models.sql'])]


async def test_model_info_by_slugs_versions(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v1/model_info_by_slugs_versions',
        json={
            'models': [
                {'slug': 'detmir_dialog', 'version': '1'},
                {'slug': 'dialog_act_hello', 'version': '1'},
            ],
        },
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 2


async def test_model_info_by_slugs_versions_no_models(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models/v1/model_info_by_slugs_versions',
        json={'models': []},
    )
    assert response.status == 200

    content = await response.json()
    assert not content['models']


@pytest.mark.set_worker(worker_id=5)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_get_model_topics_not_found(
        web_context, web_app_client, monkeypatch,
):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/models/topics?'
        'model_slug=genotek_dialog&model_version=1',
    )
    assert response.status == 404


@pytest.mark.set_worker(worker_id=6)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_get_model_topics(web_context, web_app_client, monkeypatch):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/models/topics?'
        'model_slug=genotek_dialog&model_version=1',
    )
    assert response.status == 200

    content = await response.json()
    assert content['model_topics']
    model_topic = content['model_topics'][0]
    assert 'slug' in model_topic
    assert 'key_metric' in model_topic
    assert 'threshold' in model_topic


@pytest.mark.set_worker(worker_id=5)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_get_model_data_not_found(
        web_context, web_app_client, monkeypatch,
):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/models/data?'
        'model_slug=genotek_dialog&model_version=1',
    )
    assert response.status == 404


@pytest.mark.set_worker(worker_id=6)
@pytest.mark.download_ml_resource(attrs={'type': 'genotek_dialog'})
async def test_get_model_data(web_context, web_app_client, monkeypatch):
    response = await web_app_client.get(
        '/internal/supportai-models/v1/models/data?'
        'model_slug=genotek_dialog&model_version=1',
    )
    assert response.status == 200

    content = await response.json()

    assert content['test_data']
    test_record = content['test_data'][0]

    assert 'ground_truth_slug' in test_record
    assert 'probabilities' in test_record

    assert test_record['probabilities']
    probability = test_record['probabilities'][0]
    assert 'slug' in probability
    assert 'probability' in probability
