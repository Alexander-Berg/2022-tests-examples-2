import json

import pytest  # noqa: F401

from . import common


@pytest.mark.parametrize(
    'status,location,body',
    [
        (
            200,
            {'stage_name': 'initialization', 'in_binding_idx': 0},
            {'schema': {}},
        ),
        (
            200,
            {'stage_name': 'initialization', 'in_binding_idx': 1},
            'schema.json',
        ),
        (
            400,
            {'error': 'right here'},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'Unexpected fields: [\'error\']'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            400,
            {'stage_name': 'initialization', 'in_binding_idx': 0},
            {
                'code': '400',
                'message': 'Very bad',
                'details': {'reason': 'just no'},
            },
        ),
        (
            500,
            {'stage_name': 'initialization', 'in_binding_idx': 0},
            'such unexpected response',
        ),
    ],
    ids=[
        'empty_schema',
        'normal_object_schema',
        'service_wrong_parsing',
        'service_400',
        'service_500',
    ],
)
async def test(web_app_client, mockserver, load_json, status, location, body):
    consumer = 'taxi-surge'
    service = 'surge-calculator'
    actual_requests = []

    if isinstance(body, str) and body.endswith('.json'):
        body_obj = {'schema': load_json(body)}
    else:
        body_obj = body

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/schema')
    def _taxi_compile_pipeline(request):
        actual_requests.append(request.json)

        if status != 200:
            return mockserver.make_response(
                json.dumps(body),
                status,
                headers={'X-YaTaxi-Error-Code': 'error_code'},
            )

        return body_obj

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }

    sent_request = {'pipeline': pipeline, 'location': location}
    response = await web_app_client.post(
        '/v2/pipeline/schema',
        json=sent_request,
        params={'consumer': consumer},
    )
    data = await response.json()

    if status == 500:
        assert response.status == 400
        assert data['code'] == '500'
    else:
        assert response.status == status
        assert data == body_obj

    pipeline['consumer'] = consumer

    # since dynamic consumer doesn't use codegen client,
    # it won't add defaults from schema
    common.remove_deprecated_fields(pipeline)

    # normally we expect 1 request but there will be retries for code 500
    for request in actual_requests:
        assert request == sent_request
