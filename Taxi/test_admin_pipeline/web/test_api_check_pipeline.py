import json

import pytest  # noqa: F401


async def test_check(web_app_client, mockserver, load_json):
    compile_status = 200

    consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _approvals_drafts_create(request):
        return {}

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _compile_pipeline(request):
        if compile_status != 200:
            return mockserver.make_response(
                json.dumps({'code': '400', 'message': 'error from compile'}),
                compile_status,
                headers={'X-YaTaxi-Error-Code': 'error_code'},
            )

        return {'metadata': {'stages': []}}

    @mockserver.json_handler(
        '/surge-calculator/v1/js/pipeline/is-safe-to-deactivate',
    )
    def _taxi_is_safe_to_deactivate_pipeline(request):
        reason_map = {'non_blocking': '<error message>'}
        return {'unsafe_reason': reason_map.get(request.query['name'], '')}

    async def send_check(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            '/v2/pipeline/check',
            json=pipeline_doc,
            headers={'X-Yandex-Login': 'testsuite'},
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }

    # check invalid id state
    expected_text = 'Invalid state for approval - draft'
    response = await send_check(pipeline)
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': expected_text,
    }

    # create and activate for next checks
    active_pipeline = {
        'id': 'active-test-id',
        'name': 'test_name',
        'state': 'approving',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }
    response = await web_app_client.post(
        '/v2/pipeline/',
        json=active_pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    active_pipeline['state'] = 'active'
    active_pipeline['version'] = 0
    active_pipeline['consumer'] = consumer
    response = await web_app_client.post(
        f'/v2/pipeline/activate', json=active_pipeline,
    )
    assert response.status == 200

    # check not active delete
    pipeline['state'] = 'removed'
    response = await send_check(pipeline)
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': (
            'Unable to approve transition from '
            'state __default__ to state removed'
        ),
    }

    # check active in use delete
    consumer = 'taxi-surge'
    pipeline['id'] = '5de7baf5eb70bf332afa25f1'
    pipeline['name'] = 'non_blocking'
    response = await send_check(pipeline)
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': f'Unable to delete - <error message>',
    }

    # check active delete
    consumer = 'new-consumer'
    pipeline['id'] = 'active-test-id'
    pipeline['name'] = 'test_name'
    response = await send_check(pipeline)
    assert response.status == 200

    # check invalid existing state
    pipeline['state'] = 'active'
    expected_text = (
        'Unable to approve transition from state active to state active'
    )
    response = await send_check(pipeline)
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': expected_text,
    }

    # check invalid id
    pipeline['id'] = 'test_id'
    response = await send_check(pipeline)
    assert response.status == 500

    pipeline['id'] = 'test-id'
    response = await send_check(pipeline)
    assert response.status == 200, await response.text()
    assert (await response.json())[
        'change_doc_id'
    ] == f'admin_pipeline/pipelines_{pipeline["id"]}'

    # check invalid compile
    compile_status = 400
    expected_text = 'Unable to compile pipeline: error from compile'
    response = await send_check(pipeline)
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': expected_text,
    }

    compile_status = 200

    # check invalid validate
    pipeline['stages'].append({})
    expected = 'REQUEST_VALIDATION_ERROR'
    response = await send_check(pipeline)
    assert response.status == 400
    data = await response.json()

    assert data['code'] == expected
