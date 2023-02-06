import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql']),
]


async def test_get_model_topics(web_app_client):
    response = await web_app_client.get(
        '/v1/model/topics?project_slug=ya_lavka&user_id=123',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['model_topics']) == 2
    model_topic = response_json['model_topics'][0]
    assert 'slug' in model_topic
    assert 'key_metric' in model_topic
    assert 'threshold' in model_topic


async def test_update_model_topic(web_app_client, mockserver):
    response = await web_app_client.put(
        '/v1/model/topics?project_slug=ya_lavka&user_id=123',
        json={
            'id': '1',
            'slug': 'topic1',
            'key_metric': 'precision',
            'threshold': 0.98,
        },
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['threshold'] == pytest.approx(0.98)

    response = await web_app_client.get(
        '/v1/model/topics?project_slug=ya_lavka&user_id=123',
    )
    response_json = await response.json()
    assert response_json['model_topics'][0]['threshold'] == pytest.approx(0.98)


async def test_get_model_topic_plots(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-models/internal/supportai-models/v1/models/data',
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'test_data': [
                    {
                        'ground_truth_slug': 'topic2',
                        'probabilities': [
                            {'slug': 'topic1', 'probability': 0.2},
                            {'slug': 'topic2', 'probability': 0.8},
                        ],
                    },
                    {
                        'ground_truth_slug': 'topic1',
                        'probabilities': [
                            {'slug': 'topic1', 'probability': 0.9},
                            {'slug': 'topic2', 'probability': 0.1},
                        ],
                    },
                    {
                        'ground_truth_slug': 'topic1',
                        'probabilities': [
                            {'slug': 'topic1', 'probability': 0.7},
                            {'slug': 'topic2', 'probability': 0.3},
                        ],
                    },
                    {
                        'ground_truth_slug': 'topic2',
                        'probabilities': [
                            {'slug': 'topic1', 'probability': 0.6},
                            {'slug': 'topic2', 'probability': 0.4},
                        ],
                    },
                ],
            },
        )

    response = await web_app_client.get(
        '/v1/model/topics/topic1/plots?'
        'project_slug=ya_lavka&user_id=123&key_metric=precision',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['points']) == 150
    point = response_json['points'][0]
    assert 'automatization' in point
    assert 'automatization_topic' in point
    assert 'precision' in point
    assert 'recall' in point
    assert 'threshold' in point
