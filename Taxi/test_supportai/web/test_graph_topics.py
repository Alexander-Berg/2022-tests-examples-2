import random

import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql(
        'supportai', files=['default.sql', 'sample_graph_topics.sql'],
    ),
]


async def test_get_graph_topics(web_app_client):
    topics_response = await web_app_client.get(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
    )
    assert topics_response.status == 200

    json_response = await topics_response.json()
    assert len(json_response['topics']) == 2
    assert len(json_response['topics'][0]['topics']) == 3
    assert json_response['topics'][1]['title'] == 'Тема 1'


async def test_add_graph_topic(web_app_client):
    topic_response = await web_app_client.post(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
        json={'title': 'Новая тематика'},
    )

    assert topic_response.status == 200
    topic_json = await topic_response.json()
    assert topic_json['title'] == 'Новая тематика'

    topics_response = await web_app_client.get(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
    )
    assert topics_response.status == 200

    json_response = await topics_response.json()
    assert len(json_response['topics']) == 3

    topic_response = await web_app_client.post(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
        json={
            'title': 'Бонус 3',
            'description': 'Тематика с бонусами 3',
            'folder_id': '1',
        },
    )

    assert topic_response.status == 200
    topic_json = await topic_response.json()
    assert topic_json['title'] == 'Бонус 3'
    assert topic_json['description'] == 'Тематика с бонусами 3'

    topics_response = await web_app_client.get(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
    )
    assert topics_response.status == 200

    json_response = await topics_response.json()
    assert len(json_response['topics']) == 3
    assert len(json_response['topics'][0]['topics']) == 4


async def test_delete_graph_topic(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'matrix': [
                    {
                        'id': '1',
                        'text': 'Где мой заказ?',
                        'vector': [1, 2, 3, 4, 5],
                        'topic': 'topic1',
                        'type': 'addition',
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1/confirm',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    async def scenarios_count():
        response = await web_app_client.get(
            '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        )
        assert response.status == 200
        scenarios = await response.json()
        return len(scenarios['scenarios'])

    sample_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [],
        'links': [],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_empty,
    )
    assert response.status == 200
    assert await scenarios_count() == 1

    response = await web_app_client.delete(
        '/v2/topics/1?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200
    assert await scenarios_count() == 0


async def test_add_graph_topics_folder(web_app_client):
    topic_response = await web_app_client.post(
        '/v2/topics/folder?user_id=1&project_slug=ya_lavka',
        json={'title': 'Новая группа'},
    )

    assert topic_response.status == 200
    topic_json = await topic_response.json()
    assert topic_json['title'] == 'Новая группа'
    assert topic_json['topics'] == []

    topics_response = await web_app_client.get(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
    )
    assert topics_response.status == 200

    json_response = await topics_response.json()
    assert len(json_response['topics']) == 3


async def test_update_graph_topic(web_app_client):
    topic_response = await web_app_client.put(
        '/v2/topics/1?user_id=1&project_slug=ya_lavka',
        json={
            'id': '1',
            'title': 'Статус заказа 2.0',
            'description': 'Новая тематика о статусе заказа',
        },
    )

    assert topic_response.status == 200
    updated_topic = await topic_response.json()
    assert updated_topic['description'] == 'Новая тематика о статусе заказа'

    topics_response = await web_app_client.get(
        '/v2/topics?user_id=1&project_slug=ya_lavka',
    )
    assert topics_response.status == 200

    json_response = await topics_response.json()
    assert json_response['topics'][1]['title'] == 'Статус заказа 2.0'


async def test_get_graph_topic_rules(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'matrix': [
                    {
                        'id': '1',
                        'text': 'Где мой заказ?',
                        'vector': [1, 2, 3, 4, 5],
                        'topic': 'topic1',
                        'type': 'addition',
                    },
                ],
            },
        )

    rules_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rules_response.status == 200

    json_rules = await rules_response.json()
    assert len(json_rules['rules']) == 2
    assert json_rules['rules'][0]['specified'] == 'rule'
    assert json_rules['rules'][0]['content'] == 'text contains "заказ"'
    assert json_rules['rules'][0]['id'] == 'rule_1'
    assert json_rules['rules'][1]['specified'] == 'example'
    assert json_rules['rules'][1]['content'] == 'Где мой заказ?'
    assert json_rules['rules'][1]['id'] == 'example_1'


async def test_add_graph_topic_rule(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        if request.method == 'GET':
            return mockserver.make_response(
                status=200,
                json={
                    'matrix': [
                        {
                            'id': '2',
                            'text': 'Где мой заказ?',
                            'vector': [1, 2, 3, 4, 5],
                            'topic': 'topic1',
                            'type': 'addition',
                        },
                    ],
                },
            )
        return mockserver.make_response(
            status=200,
            json={
                'id': '2',
                'text': 'Где мой заказ?',
                'vector': [1, 2, 3, 4, 5],
                'topic': 'topic1',
                'type': 'addition',
            },
        )

    rule_response = await web_app_client.post(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
        json={
            'type': 'addition',
            'specified': 'example',
            'content': 'Где мой заказ?',
        },
    )

    assert rule_response.status == 200
    rule_json = await rule_response.json()
    assert rule_json['content'] == 'Где мой заказ?'
    assert rule_json['specified'] == 'example'
    assert rule_json['id'] == 'example_2'

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    json_rule = await rule_response.json()
    assert len(json_rule['rules']) == 2

    rule_response = await web_app_client.post(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
        json={
            'type': 'addition',
            'specified': 'rule',
            'content': 'text contains \'заказ123\'',
        },
    )

    assert rule_response.status == 200
    rule_json = await rule_response.json()
    assert rule_json['content'] == 'text contains \'заказ123\''
    assert rule_json['specified'] == 'rule'
    assert rule_json['id'] == 'rule_2'

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    json_rule = await rule_response.json()
    assert len(json_rule['rules']) == 3


async def test_update_graph_topic_rule(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        if request.method == 'GET':
            return mockserver.make_response(
                status=200,
                json={
                    'matrix': [
                        {
                            'id': '2',
                            'text': 'статус заказа',
                            'vector': [1, 2, 3, 4, 5],
                            'topic': 'topic1',
                            'type': 'addition',
                        },
                    ],
                },
            )
        return mockserver.make_response(
            status=200,
            json={
                'id': '2',
                'text': 'статус заказа',
                'vector': [1, 2, 3, 4, 5],
                'topic': 'topic1',
                'type': 'addition',
            },
        )

    rule_response = await web_app_client.put(
        '/v2/topics/1/rules/rule_1?user_id=1&project_slug=ya_lavka',
        json={
            'type': 'addition',
            'specified': 'rule',
            'content': 'text contains \'статус заказа\'',
        },
    )

    assert rule_response.status == 200
    updated_rule = await rule_response.json()
    assert updated_rule['content'] == 'text contains \'статус заказа\''
    assert updated_rule['id'] == 'rule_2'

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    updated_rule = await rule_response.json()
    assert len(updated_rule['rules']) == 2
    assert (
        updated_rule['rules'][0]['content']
        == 'text contains \'статус заказа\''
    )
    assert updated_rule['rules'][0]['id'] == 'rule_2'

    rule_response = await web_app_client.put(
        '/v2/topics/1/rules/rule_2?user_id=1&project_slug=ya_lavka',
        json={
            'type': 'addition',
            'specified': 'example',
            'content': 'статус заказа',
        },
    )

    assert rule_response.status == 200
    updated_rule = await rule_response.json()
    assert updated_rule['content'] == 'статус заказа'
    assert updated_rule['id'] == 'example_2'

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    updated_rule = await rule_response.json()
    assert len(updated_rule['rules']) == 1
    assert updated_rule['rules'][0]['content'] == 'статус заказа'
    assert updated_rule['rules'][0]['id'] == 'example_2'


async def test_delete_graph_topic_rule(web_app_client, mockserver):
    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        return mockserver.make_response(status=200, json={'matrix': []})

    rule_response = await web_app_client.delete(
        '/v2/topics/1/rules/rule_1?user_id=1&project_slug=ya_lavka',
    )

    assert rule_response.status == 200

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    updated_rule = await rule_response.json()
    assert updated_rule['rules'] == []


async def test_edit_graph_topic_phrase_rule(web_app_client, mockserver):

    put_json = {
        'id': '2',
        'text': 'статус заказа (изменено)',
        'vector': [1, 2, 3, 4, 5],
        'topic': 'topic1',
        'type': 'exception',
    }

    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    async def _(request):
        return mockserver.make_response(
            status=200, json={'matrix': [put_json]},
        )

    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix/2')
    async def _(request):
        return mockserver.make_response(status=200, json=put_json)

    rule_response = await web_app_client.get(
        '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    rule_response = await web_app_client.put(
        f'/v2/topics/1/rules/example_{put_json["id"]}'
        '?user_id=1&project_slug=ya_lavka',
        json={
            'type': put_json['type'],
            'specified': 'example',
            'content': put_json['text'],
        },
    )

    assert rule_response.status == 200
    updated_rule = await rule_response.json()
    assert updated_rule['content'] == put_json['text']
    assert updated_rule['type'] == put_json['type']
    assert updated_rule['specified'] == 'example'


async def test_graph_topic_rule_validation(web_app_client, mockserver):
    cases = [
        ('text = ', 400, 'Unexpected end of predicate!'),
        ('last_user_message matches \'lal\'', 200, None),
        ('text matches \'lal\'', 200, None),
        (
            'no_such_feature = 2',
            400,
            'Features [\'no_such_feature\'] do not exist!',
        ),
    ]

    last_rule_id = 'rule_1'

    for predicate, status, error_message in cases:
        rule_response = await web_app_client.post(
            '/v2/topics/1/rules?user_id=1&project_slug=ya_lavka',
            json={
                'type': random.choice(['addition', 'exception']),
                'specified': 'rule',
                'content': predicate,
            },
        )
        assert rule_response.status == status
        if error_message:
            response_json = await rule_response.json()
            assert response_json.get('message') == error_message
        else:
            last_rule_id = (await rule_response.json())['id']

        rule_response = await web_app_client.put(
            f'/v2/topics/1/rules/{last_rule_id}'
            f'?user_id=1&project_slug=ya_lavka',
            json={
                'type': random.choice(['addition', 'exception']),
                'specified': 'rule',
                'content': predicate,
            },
        )
        assert rule_response.status == status
        if error_message:
            response_json = await rule_response.json()
            assert response_json.get('message') == error_message
        else:
            last_rule_id = (await rule_response.json())['id']
