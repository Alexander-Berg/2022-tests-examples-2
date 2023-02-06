import json

import pytest  # noqa: F401

from . import common


@pytest.mark.parametrize(
    'status,body',
    [
        (200, {'metadata': {'stages': []}}),
        (
            200,
            {
                'metadata': {
                    'stages': [
                        {
                            'name': 'first_one',
                            'arguments': [
                                {
                                    'name': 'one',
                                    'type': 'string',
                                    'optional': True,
                                },
                                {
                                    'name': 'two',
                                    'type': 'boolean',
                                    'optional': False,
                                },
                            ],
                        },
                    ],
                },
            },
        ),
        (400, {'code': '400', 'message': 'error'}),
        (500, 'error'),
    ],
)
async def test_compile(web_app_client, mockserver, load_json, status, body):
    consumer = 'taxi-surge'
    service = 'surge-calculator'

    actual_requests = []

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        actual_requests.append(request.json)
        if status != 200:
            return mockserver.make_response(
                json.dumps(body),
                status,
                headers={'X-YaTaxi-Error-Code': 'error_code'},
            )

        return body

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }

    expected = body
    response = await web_app_client.post(
        '/v2/pipeline/compile',
        params={'consumer': consumer},
        json={'pipeline': pipeline},
    )
    data = await response.json()

    if status == 500:
        assert response.status == 400
        assert data['code'] == '500'
    else:
        assert response.status == status
        assert data == expected

    pipeline['consumer'] = consumer

    # since dynamic consumer doesn't use codegen client,
    # it won't add defaults from schema
    common.remove_deprecated_fields(pipeline)

    # normally we expect 1 request but there will be retries for code 500
    for request in actual_requests:
        assert request == {'extended_check': False, 'pipeline': pipeline}
