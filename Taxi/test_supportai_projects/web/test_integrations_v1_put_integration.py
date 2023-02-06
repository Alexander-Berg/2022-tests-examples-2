import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {'type': 'not_required'},
                'auth_data': {'type': 'wrong_type'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'auth_data': {'type': 'api_key'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'Signature',
                    },
                },
                'auth_data': {'type': 'api_key', 'location_data': {}},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
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
                        'location': 'wrong_location',
                        'path': '$.api_key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
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
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
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
                        'path': '$.api_key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'Signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'query'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'query',
                        'param_name': 'signature',
                    },
                },
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body'},
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
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
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'auth_data': {
                    'type': 'ip_address',
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
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'query',
                        'path': '$.X-YaTaxi-API-Key',
                    },
                },
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'path': '$.action'},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'param_name': 'action'},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'query', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'query', 'path': '$.action'},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'param_name': 'action'},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'body', 'index': 3},
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_status': 200,
        },
        {
            'integration_id': 2,
            'request_body': {
                'slug': 'yet_another_slug_2',
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            'response_status': 200,
        },
        {
            'integration_id': 3,
            'request_body': {
                'slug': 'yet_another_slug_3',
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
                'action_data': {'location': 'query', 'param_name': 'action'},
            },
            'response_status': 200,
        },
        {
            'integration_id': 4,
            'request_body': {
                'slug': 'yet_another_slug_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
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
            'integration_id': 5,
            'request_body': {
                'slug': 'yet_another_slug_5',
                'signature_data': {'type': 'not_required'},
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
    ]

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/integrations/{test_sample["integration_id"]}',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    test_samples = [
        {
            'integration_id': 1,
            'request_body': {
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            'response_body': {
                'id': 1,
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
        },
        {
            'integration_id': 2,
            'request_body': {
                'slug': 'yet_another_slug_2',
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            'response_body': {
                'id': 2,
                'slug': 'yet_another_slug_2',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
        },
        {
            'integration_id': 3,
            'request_body': {
                'slug': 'yet_another_slug_3',
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
                'action_data': {'location': 'query', 'param_name': 'action'},
            },
            'response_body': {
                'id': 3,
                'slug': 'yet_another_slug_3',
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
                'action_data': {'location': 'query', 'param_name': 'action'},
            },
        },
        {
            'integration_id': 4,
            'request_body': {
                'slug': 'yet_another_slug_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
            'response_body': {
                'id': 4,
                'slug': 'yet_another_slug_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
        },
        {
            'integration_id': 5,
            'request_body': {
                'slug': 'yet_another_slug_5',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
            'response_body': {
                'id': 5,
                'slug': 'yet_another_slug_5',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
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
        'total': 5,
        'integrations': [
            {
                'id': 1,
                'slug': 'yet_another_slug',
                'signature_data': {
                    'type': 'required',
                    'location_data': {
                        'location': 'body',
                        'path': '$.signature',
                    },
                },
                'auth_data': {'type': 'tvm'},
                'action_data': {'location': 'path', 'index': 3},
            },
            {
                'id': 2,
                'slug': 'yet_another_slug_2',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {'location': 'body', 'path': '$.api_key'},
                },
                'action_data': {'location': 'body', 'path': '$.action'},
            },
            {
                'id': 3,
                'slug': 'yet_another_slug_3',
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
                'action_data': {'location': 'query', 'param_name': 'action'},
            },
            {
                'id': 4,
                'slug': 'yet_another_slug_4',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'api_key',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-YaTaxi-API-Key',
                    },
                },
                'action_data': {
                    'location': 'query',
                    'param_name': 'action_id',
                },
            },
            {
                'id': 5,
                'slug': 'yet_another_slug_5',
                'signature_data': {'type': 'not_required'},
                'auth_data': {
                    'type': 'ip_address',
                    'location_data': {
                        'location': 'header',
                        'param_name': 'X-Real-IP',
                    },
                },
                'action_data': {'location': 'body', 'path': '$.action_id'},
            },
        ],
    }

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_before

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/integrations/{test_sample["integration_id"]}',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

    response = await web_app_client.get('/v1/integrations')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_response_body_after
