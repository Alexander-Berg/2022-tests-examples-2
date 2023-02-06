import pytest


@pytest.mark.pgsql('supportai_models', files=['models.sql'])
async def test_get_all_models(web_app_client):
    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 15
    model = content['models'][0]
    assert 'title' in model
    assert 'slug' in model
    assert 'version' in model
    assert 'language' in model
    assert 'model_arch' in model


async def test_create_model(web_app_client):
    response = await web_app_client.post(
        '/v1/models',
        json={
            'id': '',
            'title': 'New model',
            'slug': 'new_model',
            'version': '1.0.0',
            's3_path': 'somewhere',
            'language': 'ru',
            'preprocess_type': 'one_message',
            'model_arch': 'sentence_bert',
        },
    )

    assert response.status == 200

    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 1

    model = content['models'][0]
    assert model['s3_path'] == 'somewhere'
    assert model['version'] == '1.0.0'


async def test_create_model_default_params(web_app_client):
    response = await web_app_client.post(
        '/v1/models',
        json={
            'id': '',
            'title': 'New model',
            'slug': 'new_model',
            'version': '1.0.0',
            's3_path': 'somewhere',
            'model_arch': 'dialog_text_classification',
        },
    )

    assert response.status == 200


@pytest.mark.pgsql('supportai_models', files=['models.sql'])
async def test_delete_model(web_app_client):
    response = await web_app_client.delete('/v1/models/11')
    assert response.status == 200

    response = await web_app_client.get('/v1/models')
    assert response.status == 200

    content = await response.json()
    assert len(content['models']) == 14
