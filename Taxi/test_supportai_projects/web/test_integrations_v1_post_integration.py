import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'request_body': {
                'slug': 'test_integration_1',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'wrong_type'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'api_key'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'api_key', 'location_data': {}},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'wrong_location',
                        'path': '$.api_key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'path': '$.api_key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'path': '$.api_key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'query'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'body',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'signature_data': {'type': 'required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'param_name': 'action'},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'path': '$.action'},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'query', 'index': 2},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'wrong_location'},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            'response_status': 200,
        },
        {
            'request_body': {
                'slug': 'unique_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'path', 'index': 2},
            },
            'response_status': 200,
        },
        {
            'request_body': {
                'slug': 'unique_integration_3',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
            'response_status': 200,
        },
        {
            'request_body': {
                'slug': 'unique_integration_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 200,
        },
        {
            'request_body': {
                'slug': 'unique_integration_5',
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
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            'response_status': 200,
        },
        {
            'request_body': {
                'slug': 'unique_integration_6',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'body',
                        'path': '$.X-Real-IP',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            '/v1/integrations', json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    test_samples = [
        {
            'request_body': {
                'slug': 'unique_integration_1',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            'response_body': {
                'id': 6,
                'slug': 'unique_integration_1',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'path': '$.action'},
            },
        },
        {
            'request_body': {
                'slug': 'unique_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
            'response_body': {
                'id': 7,
                'slug': 'unique_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
        },
        {
            'request_body': {
                'slug': 'unique_integration_3',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_body': {
                'id': 8,
                'slug': 'unique_integration_3',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
        },
        {
            'request_body': {
                'slug': 'unique_integration_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            'response_body': {
                'id': 9,
                'slug': 'unique_integration_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
        },
        {
            'request_body': {
                'slug': 'unique_integration_5',
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
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_body': {
                'id': 10,
                'slug': 'unique_integration_5',
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
                'action_data': {'location': 'path', 'index': 3},
            },
        },
        {
            'request_body': {
                'slug': 'unique_integration_6',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'body',
                        'path': '$.X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            'response_body': {
                'id': 11,
                'slug': 'unique_integration_6',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'body',
                        'path': '$.X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
        },
    ]

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
        'total': 11,
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
            {
                'id': 6,
                'slug': 'unique_integration_1',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            {
                'id': 7,
                'slug': 'unique_integration_2',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
            {
                'id': 8,
                'slug': 'unique_integration_3',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            {
                'id': 9,
                'slug': 'unique_integration_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            {
                'id': 10,
                'slug': 'unique_integration_5',
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
                'action_data': {'location': 'path', 'index': 3},
            },
            {
                'id': 11,
                'slug': 'unique_integration_6',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'body',
                        'path': '$.X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
        ],
    }

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_before

    for test_sample in test_samples:
        response = await web_app_client.post(
            '/v1/integrations', json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_after
