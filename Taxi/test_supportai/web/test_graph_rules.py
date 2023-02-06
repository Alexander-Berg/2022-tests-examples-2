import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql(
        'supportai',
        files=['default.sql', 'data.sql', 'sample_graph_rules.sql'],
    ),
]


async def test_get_graph_examples(web_app_client, mockserver):
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
        '/v2/scenarios/1/examples?user_id=1&project_slug=ya_lavka',
    )
    assert rules_response.status == 200

    json_rules = await rules_response.json()
    assert len(json_rules['examples']) == 1
    assert json_rules['examples'][0]['phrase'] == 'Где мой заказ?'
    assert json_rules['examples'][0]['id'] == '1'


async def test_add_graph_example(web_app_client, mockserver):
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
        '/v2/scenarios/1/examples?user_id=1&project_slug=ya_lavka',
        json={'type': 'addition', 'phrase': 'Где мой заказ?'},
    )

    assert rule_response.status == 200
    rule_json = await rule_response.json()
    assert rule_json['phrase'] == 'Где мой заказ?'
    assert rule_json['type'] == 'addition'
    assert rule_json['id'] == '2'

    rule_response = await web_app_client.get(
        '/v2/scenarios/1/examples?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    json_rule = await rule_response.json()
    assert len(json_rule['examples']) == 1


async def test_edit_graph_phrase_example(web_app_client, mockserver):
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
        '/v2/scenarios/1/examples?user_id=1&project_slug=ya_lavka',
    )
    assert rule_response.status == 200

    rule_response = await web_app_client.put(
        f'/v2/scenarios/1/examples/{put_json["id"]}'
        '?user_id=1&project_slug=ya_lavka',
        json={'type': put_json['type'], 'phrase': put_json['text']},
    )

    assert rule_response.status == 200
    updated_rule = await rule_response.json()
    assert updated_rule['phrase'] == put_json['text']
    assert updated_rule['type'] == put_json['type']


@pytest.mark.parametrize(
    ('predicate', 'is_valid'),
    [
        ('feature1 = 123', True),
        ('sure_topic is \'qwerty\'', True),
        ('incorrect_feature is \'best\'', False),
        ('feature1 = ', False),
        ({'predicates': []}, True),
        (
            {
                'predicates': [
                    {
                        'is_active': True,
                        'type': 'form',
                        'form_predicate': [
                            {
                                'feature': 'feature1',
                                'operator': '=',
                                'value': '10',
                            },
                        ],
                    },
                ],
            },
            True,
        ),
        (
            {
                'predicates': [
                    {
                        'is_active': True,
                        'type': 'form',
                        'form_predicate': [
                            {
                                'feature': 'feature1',
                                'operator': '=',
                                'value': '',
                            },
                        ],
                    },
                ],
            },
            False,
        ),
    ],
)
async def test_validate_graph_predicate(web_app_client, predicate, is_valid):
    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        json={
            'id': '0',
            'topic_id': '2',
            'title': 'Test',
            'nodes': [
                {
                    'id': 'XXXX',
                    'version': 'SOME',
                    'type': 'close',
                    'action': {'type': 'close', 'is_final': False},
                    'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                    'tags': [],
                },
            ],
            'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
            'predicate': predicate,
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['valid'] == is_valid


async def test_graph_extra_model_topics(web_app_client):
    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        json={
            'id': '0',
            'topic_id': '2',
            'title': 'Test',
            'nodes': [
                {
                    'id': 'XXXX',
                    'version': 'SOME',
                    'type': 'close',
                    'action': {'type': 'close', 'is_final': False},
                    'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                    'tags': [{'slug': 'tag1', 'id': '0'}],
                },
            ],
            'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
            'extra_model_topics': ['1', '2'],
        },
    )

    assert response.status == 200
