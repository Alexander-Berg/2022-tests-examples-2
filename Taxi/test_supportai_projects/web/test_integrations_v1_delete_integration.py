import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {'id': 100500, 'response_status': 404},
        {'id': 1, 'response_status': 204},
    ]

    for test_sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/integrations/{test_sample["id"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    sample_id = 1

    list_response_body_before = {
        'total': 5,
        'integrations': [
            {
                'id': 1,
                'slug': 'test_integration_1',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'path': '$.action_slug'},
            },
            {
                'id': 2,
                'slug': 'test_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 2},
            },
            {
                'id': 3,
                'slug': 'test_integration_3',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            {
                'id': 4,
                'slug': 'test_integration_4',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            {
                'id': 5,
                'slug': 'test_integration_5',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'Signature',
                    },
                },
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-Real-IP',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
        ],
    }

    list_response_body_after = {
        'total': 4,
        'integrations': [
            {
                'id': 2,
                'slug': 'test_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 2},
            },
            {
                'id': 3,
                'slug': 'test_integration_3',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            {
                'id': 4,
                'slug': 'test_integration_4',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            {
                'id': 5,
                'slug': 'test_integration_5',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'Signature',
                    },
                },
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-Real-IP',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
        ],
    }

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_before

    response = await web_app_client.delete(f'/v1/integrations/{sample_id}')
    assert response.status == 204

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_after
