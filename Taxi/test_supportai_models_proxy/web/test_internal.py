import json

import pytest


# pylint: disable=C0103
pytestmark = [
    pytest.mark.pgsql('supportai_models_proxy', files=['models.sql']),
]


async def test_get_all_models(web_app_client):
    response = await web_app_client.get(
        '/internal/supportai-models-proxy/v1/models?active_only=true',
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 3
    model = content['models'][0]
    assert 'title' in model
    assert 'slug' in model
    assert 'version' in model
    assert 'settings' in model
    assert 'language' in json.loads(model['settings'])


async def test_model_info_by_slugs_versions(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models-proxy/v1/models/info_by_keys',
        json={
            'models': [
                {'slug': 'ya_drive_dialog', 'version': '1'},
                {'slug': 'justschool_dialog', 'version': '1'},
            ],
        },
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 2


async def test_model_info_by_slugs_versions_no_models(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models-proxy/v1/models/info_by_keys',
        json={'models': []},
    )
    assert response.status == 200

    content = await response.json()
    assert not content['models']


async def test_model_info_by_slugs_versions_wrong_models(web_app_client):
    response = await web_app_client.post(
        '/internal/supportai-models-proxy/v1/models/info_by_keys',
        json={'models': [{'slug': 'wrong_model', 'version': '1'}]},
    )
    assert response.status == 200

    content = await response.json()
    assert not content['models']


async def test_get_model_topics(web_context, web_app_client, monkeypatch):
    response = await web_app_client.get(
        '/internal/supportai-models-proxy/v1/models/topics?'
        'model_slug=ya_drive_dialog&model_version=1',
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['model_topics']) == 2
    model_topic = content['model_topics'][0]
    assert 'slug' in model_topic
    assert 'key_metric' in model_topic
    assert 'threshold' in model_topic


async def test_get_model_data(web_context, web_app_client, monkeypatch):
    response = await web_app_client.get(
        '/internal/supportai-models-proxy/v1/models/data?'
        'model_slug=ya_drive_dialog&model_version=1',
    )
    assert response.status == 200

    content = await response.json()

    assert len(content['test_data']) == 2
    test_record = content['test_data'][0]

    assert 'ground_truth_slug' in test_record
    assert 'probabilities' in test_record

    assert len(test_record['probabilities']) == 1
    probability = test_record['probabilities'][0]
    assert 'slug' in probability
    assert 'probability' in probability
