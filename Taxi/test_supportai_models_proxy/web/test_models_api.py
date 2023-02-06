import json

import pytest


# pylint: disable=C0103
pytestmark = [
    pytest.mark.pgsql('supportai_models_proxy', files=['models.sql']),
]


async def test_get_all_models(web_app_client):
    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 3
    model = content['models'][0]

    assert 'id' in model
    assert 'title' in model
    assert 'slug' in model
    assert 'version' in model
    assert 'settings' in model
    assert 'language' in json.loads(model['settings'])


async def test_create_model(web_app_client):
    response = await web_app_client.post(
        '/v1/models',
        json={
            'id': '',
            'title': 'New model',
            'slug': 'new_model',
            'version': '1.0.0',
            'settings': json.dumps(
                {
                    's3_path': 'somewhere',
                    'type': 'dialog_text_classification',
                    'language': 'ru',
                    'preprocess_type': 'one_message',
                    'model_arch': 'sentence_bert',
                },
            ),
        },
    )

    assert response.status == 200

    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 4

    model = content['models'][3]
    assert model['title'] == 'New model'
    assert model['version'] == '1.0.0'


async def test_create_model_default_params(web_app_client):
    response = await web_app_client.post(
        '/v1/models',
        json={
            'id': '',
            'title': 'New model',
            'slug': 'new_model',
            'version': '1.0.0',
            'settings': '{}',
        },
    )

    assert response.status == 200


async def test_delete_model(web_app_client):
    response = await web_app_client.delete('/v1/models/2')
    assert response.status == 200

    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 2
