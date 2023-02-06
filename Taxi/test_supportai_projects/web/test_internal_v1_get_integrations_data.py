import pytest


INTEGRATIONS = [
    {
        'id': 1,
        'slug': 'test_integration_1',
        'check_signature': False,
        'auth_type': 'tvm',
        'data': '{"ACTION": {"location": "body", "path": "$.action_slug"}}',
    },
    {
        'id': 2,
        'slug': 'test_integration_2',
        'check_signature': True,
        'auth_type': 'tvm',
        'data': (
            '{"SIGNATURE": '
            '{"location": "body", "path": "$.signature"}, '
            '"ACTION": '
            '{"location": "path", "index": 2}}'
        ),
    },
    {
        'id': 3,
        'slug': 'test_integration_3',
        'check_signature': False,
        'auth_type': 'api_key',
        'data': (
            '{"API_KEY": '
            '{"location": "body", "path": "$.api_key"}, '
            '"ACTION": '
            '{"location": "path", "index": 3}}'
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
]

ACTIONS = [
    {
        'id': 1,
        'integration_id': 1,
        'slug': 'test_action_1',
        'is_ignored': False,
        'request_mapping': '{"key": "value"}',
        'response_mapping': '{}',
    },
    {
        'id': 2,
        'integration_id': 1,
        'slug': 'test_action_2',
        'is_ignored': True,
        'request_mapping': '{}',
        'response_mapping': '{"response": "some awesome mapping!!!"}',
    },
    {
        'id': 3,
        'integration_id': 3,
        'slug': 'test_action_3',
        'is_ignored': True,
        'request_mapping': '{"key_1": "value_1", "key_2": "value_2"}',
        'response_mapping': '{}',
    },
    {
        'id': 4,
        'integration_id': 3,
        'slug': 'test_action_4',
        'is_ignored': True,
        'request_mapping': '{"key": "value"}',
        'response_mapping': '{}',
    },
    {
        'id': 5,
        'integration_id': 3,
        'slug': 'test_action_5',
        'is_ignored': False,
        'request_mapping': '{}',
        'response_mapping': '{}',
    },
    {
        'id': 6,
        'integration_id': 4,
        'slug': 'test_action_6',
        'is_ignored': False,
        'request_mapping': '{}',
        'response_mapping': '{}',
    },
]

CALLBACKS = [
    {
        'id': 1,
        'action_id': 1,
        'condition': 'reply',
        'uri': '/',
        'request_method': 'GET',
        'request_mapping': '{}',
    },
    {
        'id': 2,
        'action_id': 1,
        'condition': 'tag',
        'uri': '/some_slug',
        'request_method': 'POST',
        'request_mapping': '{"message": "Awwww, infinite loops, my pleasure"}',
    },
    {
        'id': 3,
        'action_id': 1,
        'condition': 'tag',
        'uri': '/another_slug',
        'request_method': 'DELETE',
        'request_mapping': '{}',
    },
    {
        'id': 4,
        'action_id': 2,
        'condition': 'close',
        'uri': '/',
        'request_method': 'DELETE',
        'request_mapping': '{"message": "Do not delete anything"}',
    },
    {
        'id': 5,
        'action_id': 3,
        'condition': 'forward',
        'uri': '/sluggy_slug',
        'request_method': 'GET',
        'request_mapping': '{}',
    },
    {
        'id': 6,
        'action_id': 5,
        'condition': 'reply_iterable',
        'uri': '/',
        'request_method': 'GET',
        'request_mapping': '{}',
    },
    {
        'id': 7,
        'action_id': 5,
        'condition': 'forward',
        'uri': '/',
        'request_method': 'POST',
        'request_mapping': '{"message": "Awesome POST session"}',
    },
    {
        'id': 8,
        'action_id': 6,
        'condition': 'tag',
        'uri': '/',
        'request_method': 'GET',
        'request_mapping': '{}',
    },
]


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    expected_response = {
        'integrations': {'current_ids': [1, 2, 3, 4, 5], 'data': INTEGRATIONS},
        'actions': {'current_ids': [1, 2, 3, 4, 5, 6], 'data': ACTIONS},
        'callbacks': {
            'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
            'data': CALLBACKS,
        },
    }

    response = await web_app_client.get(
        '/supportai-projects/v1/integrations-data',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_modified_since_filter_data(web_app_client):

    test_samples = [
        {
            'modified_since': 200,
            'response_body': {
                'integrations': {
                    'current_ids': [1, 2, 3, 4, 5],
                    'data': INTEGRATIONS,
                },
                'actions': {
                    'current_ids': [1, 2, 3, 4, 5, 6],
                    'data': [
                        ACTIONS[0],
                        ACTIONS[1],
                        ACTIONS[2],
                        ACTIONS[4],
                        ACTIONS[5],
                    ],
                },
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [
                        CALLBACKS[0],
                        CALLBACKS[2],
                        CALLBACKS[3],
                        CALLBACKS[4],
                        CALLBACKS[6],
                        CALLBACKS[7],
                    ],
                },
            },
        },
        {
            'modified_since': 300,
            'response_body': {
                'integrations': {
                    'current_ids': [1, 2, 3, 4, 5],
                    'data': [
                        INTEGRATIONS[0],
                        INTEGRATIONS[2],
                        INTEGRATIONS[3],
                        INTEGRATIONS[4],
                    ],
                },
                'actions': {
                    'current_ids': [1, 2, 3, 4, 5, 6],
                    'data': [ACTIONS[0], ACTIONS[2], ACTIONS[4]],
                },
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [CALLBACKS[3], CALLBACKS[4], CALLBACKS[6]],
                },
            },
        },
        {
            'modified_since': 400,
            'response_body': {
                'integrations': {
                    'current_ids': [1, 2, 3, 4, 5],
                    'data': [INTEGRATIONS[2], INTEGRATIONS[4]],
                },
                'actions': {
                    'current_ids': [1, 2, 3, 4, 5, 6],
                    'data': [ACTIONS[0], ACTIONS[2], ACTIONS[4]],
                },
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [CALLBACKS[3], CALLBACKS[4]],
                },
            },
        },
        {
            'modified_since': 800,
            'response_body': {
                'integrations': {
                    'current_ids': [1, 2, 3, 4, 5],
                    'data': [INTEGRATIONS[4]],
                },
                'actions': {'current_ids': [1, 2, 3, 4, 5, 6], 'data': []},
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [CALLBACKS[3]],
                },
            },
        },
        {
            'modified_since': 1000,
            'response_body': {
                'integrations': {'current_ids': [1, 2, 3, 4, 5], 'data': []},
                'actions': {'current_ids': [1, 2, 3, 4, 5, 6], 'data': []},
                'callbacks': {
                    'current_ids': [1, 2, 3, 4, 5, 6, 7, 8],
                    'data': [],
                },
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/supportai-projects/v1/integrations-data'
            f'?modified_since={test_sample["modified_since"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
