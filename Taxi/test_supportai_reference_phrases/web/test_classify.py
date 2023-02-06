import pytest


@pytest.mark.redis_store(file='redis')
@pytest.mark.supportai_reference_phrases_cache(
    draft={
        'project_1': [
            {'topic': 'topic', 'vector': [0.1, 0.1, 0.1, 0.1]},
            {'topic': 'topic', 'vector': [0.1, 0.1, 0.1, 0.1]},
            {'topic': 'OTHER', 'vector': [0.0, 0.0, 0.0, 0.0]},
            {'topic': 'OTHER', 'vector': [0.0, 0.0, 0.0, 0.0]},
            {'topic': 'OTHER', 'vector': [0.0, 0.0, 0.0, 0.0]},
            {'topic': 'OTHER', 'vector': [0.0, 0.0, 0.0, 0.0]},
            {'topic': 'OTHER', 'vector': [0.0, 0.0, 0.0, 0.0]},
        ],
    },
)
async def test_classify(web_app_client, web_context):
    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/classify?'
        'project_id=project_1&version=draft',
        json={'text': 'text', 'vector': [0.1, 0.1, 0.1, 0.1]},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['common_topic_slug'] is None
    assert response_json['project_topic_slug'] == 'topic'


@pytest.mark.redis_store(file='redis')
@pytest.mark.supportai_reference_phrases_cache(
    draft={'project_1': [{'topic': 'topic', 'vector': [0.1, 0.1, 0.1, 0.1]}]},
)
async def test_classify_one_phrase(web_app_client):
    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/classify?'
        'project_id=project_1&version=draft',
        json={'text': 'text', 'vector': [0.1, 0.1, 0.1, 0.1]},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['common_topic_slug'] is None
    assert response_json['project_topic_slug'] == 'topic'

    response = await web_app_client.post(
        '/supportai-reference-phrases/v1/classify?'
        'project_id=project_1&version=draft',
        json={'text': 'text', 'vector': [0.9, 0.9, 0.2222222, 0.9]},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['common_topic_slug'] is None
    assert response_json['project_topic_slug'] is None
