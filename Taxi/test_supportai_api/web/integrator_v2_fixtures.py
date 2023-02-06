# pylint: disable=unused-variable

from aiohttp import web
import pytest


@pytest.fixture()
def mock_projects_response_data(mockserver):
    @mockserver.json_handler(
        '/supportai-projects/supportai-projects/v1/integrations-data',
    )
    async def _dummy_integrations_data(request):
        return mockserver.make_response(
            status=200,
            json={
                'integrations': {
                    'current_ids': [1, 2, 3, 4, 5],
                    'data': [
                        {
                            'id': 1,
                            'slug': 'test_integration_1',
                            'check_signature': False,
                            'auth_type': 'tvm',
                            'data': (
                                '{"ACTION": '
                                '{"location": "body", '
                                '"path": "$.action_slug"}}'
                            ),
                        },
                        {
                            'id': 2,
                            'slug': 'test_integration_2',
                            'check_signature': False,
                            'auth_type': 'tvm',
                            'data': (
                                '{"SIGNATURE": '
                                '{"location": "body", '
                                '"path": "$.signature"}, '
                                '"ACTION": {"location": '
                                '"path", "index": 5}}'
                            ),
                        },
                        {
                            'id': 3,
                            'slug': 'test_integration_3',
                            'check_signature': False,
                            'auth_type': 'api_key',
                            'data': (
                                '{"API_KEY": '
                                '{"location": "body", '
                                '"path": "$.api_key"}, '
                                '"ACTION": {"location": '
                                '"path", "index": 5}}'
                            ),
                        },
                        {
                            'id': 4,
                            'slug': 'test_integration_4',
                            'check_signature': True,
                            'auth_type': 'api_key',
                            'data': (
                                '{"API_KEY": '
                                '{"location": "query", '
                                '"param_name": "X-YaTaxi-API-Key"}, '
                                '"SIGNATURE": {"location": "query", '
                                '"param_name": "signature"}, '
                                '"ACTION": {"location": "body", '
                                '"path": "$.action_id"}}'
                            ),
                        },
                        {
                            'id': 5,
                            'slug': 'test_integration_5',
                            'check_signature': True,
                            'auth_type': 'ip_address',
                            'data': (
                                '{"IP_ADDRESS": '
                                '{"location": "header", '
                                '"param_name": "X-Real-IP"}, '
                                '"SIGNATURE": '
                                '{"location": "header", '
                                '"param_name": "Signature"}, '
                                '"ACTION": {"location": "query", '
                                '"param_name": "action_id"}}'
                            ),
                        },
                    ],
                },
                'actions': {
                    'current_ids': [1, 2, 3, 4, 5, 6],
                    'data': [
                        {
                            'id': 1,
                            'integration_id': 1,
                            'slug': 'test_action_1',
                            'is_ignored': False,
                            'request_mapping': (
                                '{"dialog": {"messages": []}, "features": []}'
                            ),
                            'response_mapping': (
                                '{{ "{" }}'
                                '{% if "most_probable_topic" in features %}'
                                '"topic": '
                                '"{{ features.most_probable_topic }}",'
                                '{% endif %}'
                                '"message": "{{ reply.text }}"'
                                '{{ "}" }}'
                            ),
                        },
                        {
                            'id': 2,
                            'integration_id': 1,
                            'slug': 'default',
                            'is_ignored': True,
                            'request_mapping': (
                                '{"dialog": {"messages": []}, "features": []}'
                            ),
                            'response_mapping': (
                                '{"response": "some awesome mapping!!!"}'
                            ),
                        },
                        {
                            'id': 3,
                            'integration_id': 3,
                            'slug': 'default',
                            'is_ignored': True,
                            'request_mapping': (
                                '{"dialog": {"messages": []}, "features": []}'
                            ),
                            'response_mapping': '{}',
                        },
                        {
                            'id': 4,
                            'integration_id': 3,
                            'slug': 'test_action_4',
                            'is_ignored': True,
                            'request_mapping': (
                                '{"dialog": '
                                '{"messages": {{ messages|tojson }}}, '
                                '"features": []}'
                            ),
                            'response_mapping': '{}',
                        },
                        {
                            'id': 5,
                            'integration_id': 3,
                            'slug': 'test_action_5',
                            'is_ignored': False,
                            'request_mapping': (
                                '{"dialog": {"messages": []}, "features": []}'
                            ),
                            'response_mapping': (
                                '{"message": "{{ reply.text }}"}'
                            ),
                        },
                        {
                            'id': 6,
                            'integration_id': 4,
                            'slug': 'test_action_6',
                            'is_ignored': False,
                            'request_mapping': (
                                '{"dialog": '
                                '{"messages": {{ messages|tojson }}},'
                                '"features": {{ features|tojson }}}'
                            ),
                            'response_mapping': (
                                '{"message": "{{ reply.text }}",'
                                '"line": "{{ forward.line }}"}'
                            ),
                        },
                    ],
                },
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [
                        {
                            'id': 1,
                            'action_id': 1,
                            'condition': 'forward',
                            'uri': '/callback-1',
                            'request_method': 'GET',
                            'request_mapping': '{}',
                        },
                        {
                            'id': 2,
                            'action_id': 1,
                            'condition': 'close',
                            'uri': '/callback-2',
                            'request_method': 'POST',
                            'request_mapping': '{"data": "{{ forward }}"}',
                        },
                        {
                            'id': 3,
                            'action_id': 1,
                            'condition': 'tag',
                            'uri': '/callback-3',
                            'request_method': 'DELETE',
                            'request_mapping': '{}',
                        },
                        {
                            'id': 4,
                            'action_id': 2,
                            'condition': 'reply',
                            'uri': '/callback-4',
                            'request_method': 'DELETE',
                            'request_mapping': (
                                '{"message": "Do not delete anything"}'
                            ),
                        },
                        {
                            'id': 5,
                            'action_id': 3,
                            'condition': 'close',
                            'uri': '/callback-5',
                            'request_method': 'GET',
                            'request_mapping': '{}',
                        },
                        {
                            'id': 6,
                            'action_id': 5,
                            'condition': 'reply_iterable',
                            'uri': '/callback-6',
                            'request_method': 'GET',
                            'request_mapping': '{}',
                        },
                        {
                            'id': 7,
                            'action_id': 5,
                            'condition': 'forward',
                            'uri': '/callback-7',
                            'request_method': 'POST',
                            'request_mapping': (
                                '{"data": "{{ forward.line }}"}'
                            ),
                        },
                        {
                            'id': 8,
                            'action_id': 6,
                            'condition': 'tag',
                            'uri': '/callback-8',
                            'request_method': 'GET',
                            'request_mapping': '{}',
                        },
                    ],
                },
            },
        )

    @mockserver.json_handler(
        '/supportai-projects/supportai-projects/v1/secret-data',
    )
    async def _dummy_integrations_secrets(request):
        return mockserver.make_response(
            status=200,
            json={
                'project_integrations': [
                    {
                        'id': 1,
                        'project_id': 1,
                        'integration_id': 1,
                        'base_url': '$mockserver',
                        'secret_data': '{}',
                    },
                    {
                        'id': 2,
                        'project_id': 1,
                        'integration_id': 2,
                        'base_url': '$mockserver',
                        'secret_data': '{"SIGNATURE_TOKEN": "token-token"}',
                    },
                    {
                        'id': 3,
                        'project_id': 1,
                        'integration_id': 3,
                        'base_url': '$mockserver',
                        'secret_data': '{"API_KEY": "keeeeeeeey"}',
                    },
                    {
                        'id': 4,
                        'project_id': 2,
                        'integration_id': 4,
                        'base_url': '$mockserver',  # maybe delete?
                        'secret_data': (
                            '{"API_KEY": "keykeykey", '
                            '"SIGNATURE_TOKEN": "123123123"}'
                        ),
                    },
                    {
                        'id': 5,
                        'project_id': 3,
                        'integration_id': 5,
                        'base_url': '$mockserver',
                        'secret_data': (
                            '{"API_KEY": "kkkey", '
                            '"SIGNATURE_TOKEN": "tik-tak-token"}'
                        ),
                    },
                ],
                'api_keys': [
                    {'id': 1, 'project_id': 1, 'api_key': 'AsdadasdaQ23r'},
                    {'id': 2, 'project_id': 2, 'api_key': '321232131231'},
                    {'id': 3, 'project_id': 3, 'api_key': '12345678'},
                ],
                'allowed_ips': [
                    {'id': 1, 'project_id': 1, 'ip_address': '127.0.0.1'},
                    {'id': 2, 'project_id': 1, 'ip_address': '0.0.0.0'},
                    {'id': 3, 'project_id': 1, 'ip_address': '167.2.3.5'},
                    {'id': 4, 'project_id': 2, 'ip_address': '172.2.8.6'},
                    {'id': 5, 'project_id': 2, 'ip_address': '172.2.8.8'},
                    {'id': 6, 'project_id': 3, 'ip_address': '8.8.8.8'},
                    {'id': 7, 'project_id': 3, 'ip_address': '9.9.9.9'},
                ],
            },
        )


@pytest.fixture()
async def support_simple_mock(mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )


@pytest.fixture()
async def support_explicit_mock(mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def handler(request):
        return web.json_response(
            data={
                'reply': {'text': 'hello', 'texts': ['hello']},
                'features': {
                    'most_probable_topic': 'topic',
                    'probabilities': [],
                    'features': [{'key': 'alice_state', 'value': 1}],
                },
                'tag': {'add': ['image']},
                'buttons_block': {
                    'buttons': [
                        {'text': 'totalchest 1'},
                        {'text': 'totalchest 2'},
                    ],
                },
                'forward': {'line': '12'},
            },
        )
