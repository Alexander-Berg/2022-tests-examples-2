# pylint: disable=too-many-lines
import pytest

from supportai import models as db_models
from supportai.utils import scenario_graph_helpers

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql']),
]


async def test_graph_editor_create_graph(
        web_app_client, mockserver, mock_translator,
):
    @mock_translator('/tr.json/translate')
    async def _translate():
        return mockserver.make_response(
            status=200,
            json={'code': 200, 'lang': 'ru-en', 'text': ['привет']},
        )

    response = await web_app_client.get(
        '/v1/languages?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200

    response = await web_app_client.post(
        '/v1/translate?user_id=1&project_slug=ya_lavka',
        json={'text': 'hello', 'target_language': 'ru'},
    )

    assert response.status == 200

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

    graph = await response.json()

    graph_id = graph['id']
    assert graph['id'] != '0'
    assert graph['title'] == sample_empty['title']
    assert graph['topic_id'] == sample_empty['topic_id']

    response = await web_app_client.put(
        f'/v2/scenarios/{graph_id}?user_id=1&project_slug=ya_lavka',
        json=sample_empty,
    )
    assert response.status == 200

    response = await web_app_client.put(
        f'/v2/scenarios/{graph_id}?user_id=1&project_slug=ya_lavka',
        json=graph,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    scenarios = await response.json()
    scenario = scenarios['scenarios'][0]

    assert scenario['status'] == 'new'

    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
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
    }

    response = await web_app_client.put(
        f'/v2/scenarios/{graph_id}?user_id=1&project_slug=ya_lavka',
        json=sample_not_empty,
    )
    assert response.status == 200

    graph = await response.json()

    assert graph['valid'] is True

    assert len(graph['nodes']) == 1
    assert graph['nodes'][0]['id'] == sample_not_empty['nodes'][0]['id']
    assert graph['nodes'][0]['action']['is_final'] is False


async def test_graph_editor_create_graph_multiple_actions(web_app_client):
    sample_multiple_actions = {
        'id': '0',
        'topic_id': '1',
        'title': 'Testgvhgvhgvhgvghv',
        'nodes': [
            {
                'id': 'XXXX',
                'title': 'asdasd',
                'version': 'SOME',
                'type': 'action',
                'counter': 1,
                'action': {
                    'type': 'custom',
                    'action_type': 'send_mail',
                    'parameters': {
                        'version': '1',
                        'call_params': [
                            {'to_emails': ['at.8441451@yandex.ru']},
                            {'title': 'title'},
                            {'from_email': 'at.8441451@yandex.ru'},
                            {'from_name': 'Ivan Petrov'},
                            {'text': 'message'},
                        ],
                    },
                },
                'actions': [
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                ],
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
            {
                'id': 'XXXX1',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
        ],
        'links': [
            {'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}},
            {'from_id': 'XXXX', 'to_id': 'XXXX1', 'meta': {'path': []}},
        ],
    }

    response = await web_app_client.post(
        f'/v2/scenarios?user_id=1&project_slug=ya_lavka',
        json=sample_multiple_actions,
    )
    assert response.status == 200
    graph = await response.json()
    import logging
    logging.error(graph)
    assert graph['valid'] is True

    assert graph['nodes'] == sample_multiple_actions['nodes']


async def test_release_graph_scenario(web_app_client, web_context):
    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'slug': 'tag1', 'id': '0'}],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )
    assert response.status == 200

    graph = await response.json()
    assert graph['nodes'][0]['tags'][0] == {'slug': 'tag1', 'id': '1'}

    response = await web_app_client.post(
        '/v1/versions/draft/release?user_id=1&project_slug=ya_lavka',
        json={'name': 'Test'},
    )

    assert response.status == 200
    response_json = await response.json()

    async with web_context.pg.slave_pool.acquire() as conn:
        scenario_graphs = await db_models.ScenarioGraph.select_by_version_id(
            web_context, conn, int(response_json['id']),
        )
        assert len(scenario_graphs) == 1

        scenario_graph = await scenario_graph_helpers.ScenarioGraph.from_db(
            web_context, conn, scenario_graphs[0].id,
        )

    assert len(scenario_graph.tags) == 1
    assert list(scenario_graph.tags.values())[0][0].id in {3, 4}


async def test_release_graph_scenario_multiple_actions(
        web_app_client, web_context,
):
    sample_multiple_actions = {
        'id': '0',
        'topic_id': '1',
        'title': 'Testgvhgvhgvhgvghv',
        'nodes': [
            {
                'id': 'XXXX',
                'title': 'asdasd',
                'version': 'SOME',
                'type': 'action',
                'counter': 1,
                'action': {
                    'type': 'custom',
                    'action_type': 'send_mail',
                    'parameters': {
                        'version': '1',
                        'call_params': [
                            {'to_emails': ['at.8441451@yandex.ru']},
                            {'title': 'title'},
                            {'from_email': 'at.8441451@yandex.ru'},
                            {'from_name': 'Ivan Petrov'},
                            {'text': 'message'},
                        ],
                    },
                },
                'actions': [
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                ],
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
            {
                'id': 'XXXX1',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
        ],
        'links': [
            {'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}},
            {'from_id': 'XXXX', 'to_id': 'XXXX1', 'meta': {'path': []}},
        ],
    }
    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        json=sample_multiple_actions,
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/versions/draft/release?user_id=1&project_slug=ya_lavka',
        json={'name': 'Test'},
    )
    assert response.status == 200
    response_json = await response.json()

    async with web_context.pg.slave_pool.acquire() as conn:
        scenario_graphs = await db_models.ScenarioGraph.select_by_version_id(
            web_context, conn, int(response_json['id']),
        )
        assert len(scenario_graphs) == 1

        scenario_graph = await scenario_graph_helpers.ScenarioGraph.from_db(
            web_context, conn, scenario_graphs[0].id,
        )

    assert len(scenario_graph.tags) == 2
    assert list(scenario_graph.tags.values())[0][0].id in {3, 4}


async def test_graph_scenario_statuses(web_app_client, web_context):
    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'slug': 'tag1', 'id': '0'}],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )

    assert response.status == 200

    graph = await response.json()
    graph_id = graph['id']

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    scenarios = await response.json()
    scenario = scenarios['scenarios'][0]

    assert scenario['status'] == 'new'

    await web_app_client.post(
        '/v1/versions/draft/release?user_id=1&project_slug=ya_lavka',
        json={'name': 'Test'},
    )

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    scenarios = await response.json()
    scenario = scenarios['scenarios'][0]

    assert scenario['status'] == 'published'

    response = await web_app_client.put(
        f'/v2/scenarios/{graph_id}?user_id=1&project_slug=ya_lavka',
        json=sample_not_empty,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    scenarios = await response.json()
    scenario = scenarios['scenarios'][0]

    assert scenario['status'] == 'changed'


async def test_create_scenario_with_tags(web_app_client, web_context):
    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'id': '0', 'slug': 'speak'}],
            },
            {
                'id': 'XXXX2',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'id': '0', 'slug': 'speak'}],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )
    assert response.status == 200
    graph = await response.json()

    assert graph['nodes'][0]['tags']
    assert graph['nodes'][0]['tags'][0]['slug'] == 'speak'


@pytest.mark.now('2021-08-02T10:00:00')
async def test_get_scenarios(web_app_client):
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

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200

    scenarios = await response.json()

    assert scenarios['total'] == 1
    assert len(scenarios['scenarios']) == 1

    scenario = scenarios['scenarios'][0]
    assert scenario['id'] == '1'
    assert scenario['title'] == 'Test'
    assert scenario['topic_id'] == '1'
    assert scenario['topic_slug'] == 'topic1'
    assert not scenario['valid']
    assert scenario['updated_at'] == '2021-08-02T10:00:00+03:00'
    assert scenario['status'] == 'new'

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka&limit=1&offset=0',
    )

    assert response.status == 200

    scenarios = await response.json()

    assert scenarios['total'] == 1
    assert len(scenarios['scenarios']) == 1

    sample_multiple_actions = {
        'id': '0',
        'topic_id': '2',
        'title': 'Testgvhgvhgvhgvghv',
        'nodes': [
            {
                'id': 'XXXX',
                'title': 'asdasd',
                'version': 'SOME',
                'type': 'action',
                'counter': 1,
                'action': {
                    'type': 'custom',
                    'action_type': 'send_mail',
                    'parameters': {
                        'version': '1',
                        'call_params': [
                            {'to_emails': ['at.8441451@yandex.ru']},
                            {'title': 'title'},
                            {'from_email': 'at.8441451@yandex.ru'},
                            {'from_name': 'Ivan Petrov'},
                            {'text': 'message'},
                        ],
                    },
                },
                'actions': [
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                    {
                        'type': 'custom',
                        'action_type': 'send_mail',
                        'parameters': {
                            'version': '1',
                            'call_params': [
                                {'to_emails': ['at.8441451@yandex.ru']},
                                {'title': 'title'},
                                {'from_email': 'at.8441451@yandex.ru'},
                                {'from_name': 'Ivan Petrov'},
                                {'text': 'message'},
                            ],
                        },
                    },
                ],
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
            {
                'id': 'XXXX1',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {
                    'validation_result': {'is_valid': True},
                    'x': 0.0,
                    'y': 0.0,
                },
                'tags': [{'slug': 'tag1', 'id': '1'}],
            },
        ],
        'links': [
            {'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}},
            {'from_id': 'XXXX', 'to_id': 'XXXX1', 'meta': {'path': []}},
        ],
    }
    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        json=sample_multiple_actions,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    scenarios = await response.json()
    assert scenarios['total'] == 2
    assert len(scenarios['scenarios']) == 2

    scenario = scenarios['scenarios'][1]
    assert scenario['id'] == '2'
    assert scenario['title'] == 'Testgvhgvhgvhgvghv'
    assert scenario['topic_id'] == '2'
    assert scenario['topic_slug'] == 'topic2'
    assert scenario['valid']
    assert scenario['updated_at'] == '2021-08-02T10:00:00+03:00'
    assert scenario['status'] == 'new'


async def test_delete_scenarios(web_app_client):
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

    response_json = await response.json()

    scenario_id = response_json['id']

    response = await web_app_client.delete(
        f'/v2/scenarios/{scenario_id}?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200

    sample_not_empty = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )

    assert response.status == 200

    response_json = await response.json()

    scenario_id = response_json['id']

    response = await web_app_client.delete(
        f'/v2/scenarios/{scenario_id}?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200


async def test_invalid_graph(web_app_client, web_context):
    example_graph = {
        'id': '0',
        'topic_id': '1',
        'title': 'Test',
        'nodes': [
            {
                'id': 'XXXX',
                'version': 'SOME',
                'type': 'response',
                'action': {'type': 'response', 'texts': ['1']},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'id': '0', 'slug': 'speak'}],
                'title': '1',
                'counter': 10,
            },
            {
                'id': 'XXXX2',
                'version': 'SOME',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'title': '', 'x': 0.0, 'y': 0.0},
                'tags': [{'id': '0', 'slug': 'speak'}],
            },
        ],
        'links': [{'from_id': '', 'to_id': 'XXXX', 'meta': {'path': []}}],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=example_graph,
    )
    assert response.status == 200

    graph = await response.json()
    assert graph['valid'] is False

    assert graph['nodes'][0]['meta']['validation_result']['is_valid'] is False
    assert (
        graph['nodes'][0]['meta']['validation_result']['description']
        == 'Empty output link'
    )

    assert graph['nodes'][1]['meta']['validation_result']['is_valid'] is False
    assert (
        graph['nodes'][1]['meta']['validation_result']['description']
        == 'Dangling graph vertex'
    )

    async with web_context.pg.slave_pool.acquire() as conn:
        version = await db_models.Version.select_draft_by_project_slug(
            web_context, conn, 'ya_lavka',
        )
        scenario_graphs = await db_models.ScenarioGraph.select_by_version_id(
            web_context, conn, version.id, valid=False,
        )

        assert len(scenario_graphs) == 1

        graph = scenario_graphs[0]
        assert graph.valid is False

    example_graph['links'].append(
        {'from_id': 'XXXX', 'to_id': 'XXXX2', 'meta': {'path': []}},
    )

    response = await web_app_client.put(
        f'/v2/scenarios/{graph.id}?user_id=1&project_slug=ya_lavka',
        json=example_graph,
    )
    assert response.status == 200

    graph = await response.json()
    assert graph['valid'] is True
    assert graph['nodes'][1]['meta']['validation_result']['is_valid']
    assert graph['nodes'][0]['meta']['validation_result']['is_valid']

    assert graph['links'][1]['meta']['validation_result']['is_valid']
    assert graph['links'][0]['meta']['validation_result']['is_valid']


async def test_save_valid_graph(web_app_client, web_context):
    sample_not_empty = {
        'id': '485',
        'title': 'Название сценария',
        'nodes': [
            {
                'id': '693df16f-08a9-443f-9d69-649b616b9dff',
                'version': '1',
                'type': 'response',
                'action': {'type': 'response', 'texts': ['Привет']},
                'meta': {'x': 0, 'y': 0},
                'tags': [],
                'title': 'Здравствуйте',
                'counter': 10,
            },
            {
                'id': 'e26ef555-1f63-484f-920b-a7515d4b9c50',
                'version': '1',
                'type': 'condition',
                'action': {
                    'type': 'condition',
                    'cases': [
                        {
                            'predicate': 'true',
                            'next': '3009f286-5b14-4be5-928a-d713e31babcd',
                            'title': 'TRUE',
                        },
                        {
                            'next': '8e1253a4-54ad-4ffa-8254-6b968437a8e0',
                            'title': 'FALSE',
                        },
                    ],
                },
                'meta': {'x': 287.9306945800781, 'y': -113.00990295410156},
                'tags': [],
                'title': 'some',
                'counter': 10,
            },
            {
                'id': '8e1253a4-54ad-4ffa-8254-6b968437a8e0',
                'version': '1',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'x': 438.1806945800781, 'y': -1.0099010467529297},
                'tags': [],
            },
            {
                'id': '3009f286-5b14-4be5-928a-d713e31babcd',
                'version': '1',
                'type': 'close',
                'action': {'type': 'close'},
                'meta': {'x': 470.9405822753906, 'y': -258.5742492675781},
                'tags': [],
            },
        ],
        'links': [
            {
                'from_id': '',
                'meta': {'path': []},
                'to_id': '693df16f-08a9-443f-9d69-649b616b9dff',
            },
            {
                'from_id': '693df16f-08a9-443f-9d69-649b616b9dff',
                'meta': {'path': []},
                'to_id': 'e26ef555-1f63-484f-920b-a7515d4b9c50',
            },
            {
                'from_id': 'e26ef555-1f63-484f-920b-a7515d4b9c50',
                'meta': {'path': []},
                'to_id': '8e1253a4-54ad-4ffa-8254-6b968437a8e0',
            },
            {
                'from_id': 'e26ef555-1f63-484f-920b-a7515d4b9c50_0',
                'meta': {'path': []},
                'to_id': '3009f286-5b14-4be5-928a-d713e31babcd',
            },
        ],
        'topic_id': '1',
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample_not_empty,
    )
    assert response.status == 200

    async with web_context.pg.slave_pool.acquire() as conn:
        version = await db_models.Version.select_draft_by_project_slug(
            web_context, conn, 'ya_lavka',
        )
        scenario_graphs = await db_models.ScenarioGraph.select_by_version_id(
            web_context, conn, version.id, valid=True,
        )

        assert len(scenario_graphs) == 1
        assert scenario_graphs[0].valid is True


async def test_add_action(web_app_client):
    data = {
        'id': '',
        'title': 'Лояльность информация: Бонусы на День рождения',
        'topic_id': '1',
        'nodes': [
            {
                'id': '49c262c4-d14b-43ad-bbb5-eca4b6a30076',
                'type': 'action',
                'version': '1',
                'tags': [],
                'action': {
                    'type': 'custom',
                    'action_type': 'send_mail',
                    'parameters': {
                        'version': '1',
                        'call_params': [
                            {'to_emails': ['at.8441451@yandex.ru']},
                            {'title': 'title'},
                            {'from_email': 'at.8441451@yandex.ru'},
                            {'from_name': 'Ivan Petrov'},
                            {'text': 'message'},
                        ],
                    },
                },
                'title': '',
                'meta': {'x': 0, 'y': 0},
            },
            {
                'id': 'a55097c0-93f6-4c8c-a8d1-a477ce1d6fb6',
                'type': 'close',
                'version': '1',
                'tags': [],
                'action': {'type': 'close'},
                'title': '',
                'meta': {'x': 197.6, 'y': 0},
            },
        ],
        'links': [
            {
                'from_id': '',
                'to_id': '49c262c4-d14b-43ad-bbb5-eca4b6a30076',
                'meta': {'path': []},
            },
            {
                'from_id': '49c262c4-d14b-43ad-bbb5-eca4b6a30076',
                'to_id': 'a55097c0-93f6-4c8c-a8d1-a477ce1d6fb6',
                'meta': {'path': []},
            },
        ],
    }

    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=data,
    )

    assert response.status == 200


async def test_copy_scenario_graph(web_app_client, web_context):
    async def scenarios_count():
        response = await web_app_client.get(
            '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        )
        assert response.status == 200
        scenarios = await response.json()
        return len(scenarios['scenarios'])

    assert await scenarios_count() == 0

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

    graph = await response.json()
    old_graph_id = graph['id']

    response = await web_app_client.post(
        f'/v2/scenarios/copy/{old_graph_id}?user_id=1&project_slug=ya_lavka',
        json={'title': 'New scenario'},
    )

    assert response.status == 200
    assert await scenarios_count() == 2

    graph = await response.json()
    new_graph_id = graph['id']

    async with web_context.pg.slave_pool.acquire() as conn:
        new_graph = await db_models.ScenarioGraph.select_by_id(
            web_context, conn, int(new_graph_id),
        )

        assert new_graph is not None

        assert new_graph.id == int(new_graph_id)
        assert new_graph.project_slug == 'ya_lavka'
        assert new_graph.topic_id == 10
        assert new_graph.title == 'New scenario'
        assert new_graph.status == 'new'

        new_topic = await db_models.Topic.select_by_id(
            web_context, conn, new_graph.topic_id,
        )

        assert new_topic is not None

        assert new_topic.id == 10
        assert new_topic.project_slug == 'ya_lavka'
        assert new_topic.parent_id is None
        assert new_topic.slug == 'New_scenario'
        assert new_topic.title == 'New scenario'
        assert new_topic.rule == 'model_sure_topic is "topic1"'
        assert new_topic.description is None


@pytest.mark.parametrize(
    'initial_graph_sample_path', ['initial_graph_with_virtual_nodes.json'],
)
async def test_copy_with_virtual_links(
        web_app_client, web_context, initial_graph_sample_path, load_json,
):
    def is_virtual_node_id(node_id: str) -> bool:
        return '_' in node_id

    async def scenarios_count():
        response = await web_app_client.get(
            '/v2/scenarios?user_id=1&project_slug=ya_lavka',
        )
        assert response.status == 200
        scenarios = await response.json()
        return len(scenarios['scenarios'])

    assert await scenarios_count() == 0

    sample = load_json(initial_graph_sample_path)
    response = await web_app_client.post(
        '/v2/scenarios?user_id=1&project_slug=ya_lavka', json=sample,
    )
    assert response.status == 200
    assert await scenarios_count() == 1

    graph = await response.json()
    old_graph_id = graph['id']

    response = await web_app_client.post(
        f'/v2/scenarios/copy/{old_graph_id}?user_id=1&project_slug=ya_lavka',
        json={'title': 'New scenario'},
    )

    assert response.status == 200
    assert await scenarios_count() == 2

    graph = await response.json()
    new_graph_id = graph['id']

    response = await web_app_client.get(
        f'/v2/scenarios/{new_graph_id}?user_id=1&project_slug=ya_lavka',
    )

    response_json = await response.json()

    for initial_link, copied_link in zip(
            sample['links'], response_json['links'],
    ):
        if initial_link['from_id']:
            assert initial_link['from_id'] != copied_link['from_id']
            assert is_virtual_node_id(
                initial_link['from_id'],
            ) == is_virtual_node_id(copied_link['from_id'])
        if initial_link['to_id']:
            assert initial_link['to_id'] != copied_link['to_id']
            assert is_virtual_node_id(
                initial_link['to_id'],
            ) == is_virtual_node_id(copied_link['to_id'])

    for initial_node, copied_node in zip(
            sample['nodes'], response_json['nodes'],
    ):
        if 'cases' in initial_node['action']:
            for initial_case, copied_case in zip(
                    initial_node['action']['cases'],
                    copied_node['action']['cases'],
            ):
                assert initial_case['next'] != copied_case['next']
                assert is_virtual_node_id(
                    initial_case['next'],
                ) == is_virtual_node_id(copied_case['next'])


async def test_add_graph_folder(web_app_client):
    folder_response = await web_app_client.post(
        '/v2/scenarios/folder?user_id=1&project_slug=ya_lavka',
        json={'title': 'Новая группа'},
    )

    assert folder_response.status == 200
    folder_json = await folder_response.json()
    assert folder_json['title'] == 'Новая группа'
    assert folder_json['scenarios'] == []
