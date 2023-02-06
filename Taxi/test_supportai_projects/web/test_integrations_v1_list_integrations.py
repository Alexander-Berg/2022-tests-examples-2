import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    expected_response = {
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

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_limit_data(web_app_client):
    limit = 2
    expected_response_body = {
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
        ],
    }

    response = await web_app_client.get(f'/v1/integrations?limit={limit}')
    assert response.status == 200
    response_json = await response.json()
    assert expected_response_body == response_json


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_offset_data(web_app_client):
    offset = 2
    expected_response_body = {
        'total': 5,
        'integrations': [
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

    response = await web_app_client.get(f'/v1/integrations?offset={offset}')
    assert response.status == 200
    response_json = await response.json()
    assert expected_response_body == response_json


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_limit_offset_data(web_app_client):
    limit = 2
    offset = 2
    expected_response_body = {
        'total': 5,
        'integrations': [
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
        ],
    }

    response = await web_app_client.get(
        f'/v1/integrations?limit={limit}&offset={offset}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert expected_response_body == response_json
