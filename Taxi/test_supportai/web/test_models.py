import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql']),
]


async def test_get_models(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/models',
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'models': [
                    {
                        'title': 'Модель 1',
                        'slug': 'model1',
                        'version': '1',
                        'language': 'ru',
                        'preprocess_type': 'one_message',
                        'model_arch': 'sentence_bert',
                    },
                    {
                        'title': 'Модель 2',
                        'slug': 'model2',
                        'version': '1',
                        'language': 'ru',
                        'preprocess_type': 'one_message',
                        'model_arch': 'sentence_bert',
                    },
                    {
                        'title': 'Модель 3',
                        'slug': 'model3',
                        'version': '4',
                        'language': 'ru',
                        'preprocess_type': 'one_message',
                        'model_arch': 'sentence_bert',
                    },
                ],
            },
        )

    response = await web_app_client.get(
        '/v1/models?project_slug=sunlight&user_id=123',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['models']) == 3
    model = response_json['models'][0]
    assert 'title' in model
    assert 'slug' in model
    assert 'version' in model


async def test_change_model(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/models/topics',
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'model_topics': [
                    {
                        'slug': 'topic1',
                        'key_metric': 'precision',
                        'threshold': 0.8,
                    },
                    {
                        'slug': 'topic3',
                        'key_metric': 'recall',
                        'threshold': 0.98,
                    },
                ],
            },
        )

    response = await web_app_client.get(
        '/v1/models/current?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['slug'] == 'test_model'

    response = await web_app_client.post(
        '/v1/models?project_slug=ya_lavka&user_id=123',
        json={'title': 'Модель 4', 'slug': 'new_model', 'version': '1'},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/models/current?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['slug'] == 'new_model'


async def test_add_model(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/models/topics',
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'model_topics': [
                    {
                        'slug': 'topic1',
                        'key_metric': 'precision',
                        'threshold': 0.8,
                    },
                    {
                        'slug': 'topic3',
                        'key_metric': 'recall',
                        'threshold': 0.98,
                    },
                ],
            },
        )

    response = await web_app_client.get(
        '/v1/models/current?project_slug=new_project&user_id=123',
    )
    assert response.status == 204

    response = await web_app_client.post(
        '/v1/models?project_slug=new_project&user_id=123',
        json={'title': 'Модель 4', 'slug': 'new_model', 'version': '1'},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/models/current?project_slug=new_project&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['slug'] == 'new_model'


async def test_delete_model(web_app_client):
    response = await web_app_client.get(
        '/v1/models/current?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['slug'] == 'test_model'

    response = await web_app_client.delete(
        '/v1/models?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/models/current?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 204
