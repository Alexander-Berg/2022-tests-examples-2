import copy
import datetime

import pytest  # noqa: F401

from . import common


NOW = '2019-12-16T23:00:00+03:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize('draft_status', ['need_approval', 'succeeded'])
async def test_dynamic_consumer(
        web_app_client, mockserver, load_json, draft_status,
):
    consumer = 'new-consumer'
    service = 'new-service'
    draft_id = 1

    response = await web_app_client.get('/enumerate_consumers')
    assert response.status == 200
    data = await response.json()
    assert consumer not in data

    response = await web_app_client.post(
        '/v2/pipeline/enumerate', params={'consumer': consumer},
    )
    assert response.status == 400

    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    response = await web_app_client.get('/enumerate_consumers')
    assert response.status == 200
    data = await response.json()
    assert consumer in data

    external_requests = []

    @mockserver.json_handler(f'/taxi_approvals/drafts/{draft_id}/')
    def _taxi_approvals_drafts_1(request):
        external_requests.append({})
        external_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return {}

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        external_requests.append(request.json)
        external_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return {'metadata': {'stages': []}}

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _taxi_approvals_drafts_create(request):
        external_requests.append(request.json)
        external_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        external_requests.append(request.json)
        external_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return [
            {
                'id': draft_id,
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', 'test-id',
                ),
                'status': draft_status,
                'created_by': 'vryanova',
            },
        ]

    pipeline = {
        'id': 'test-id',
        'name': 'test_name',
        'state': 'approving',
        'comment': 'test_comment',
        'global_scope': {'source_code': 'some code'},
        'stages': load_json('pipeline_stages.json'),
    }
    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    expected = pipeline.copy()
    expected['created'] = expected['updated'] = now
    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data['pipeline'] == expected

    expected = [
        {
            'approvals_info': {
                'id': draft_id,
                'change_doc_id': 'admin_pipeline/pipelines_test-id',
                'created_by': 'vryanova',
                'status': draft_status,
            },
            'comment': 'test_comment',
            'created': NOW,
            'id': 'test-id',
            'name': 'test_name',
            'state': 'approving',
            'updated': NOW,
        },
    ]
    response = await web_app_client.post(
        '/v2/pipeline/enumerate', params={'consumer': consumer},
    )
    assert response.status == 200
    data = await response.json()
    data = sorted(data, key=lambda x: x['id'])

    assert data == expected

    # create duplicate
    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 400

    # Check that new pipeline doc has 'consumer' field
    response = await web_app_client.post(
        '/v2/pipeline/enumerate/', params={'consumer': consumer},
    )
    assert response.status == 200

    actual = sorted(await response.json(), key=lambda x: x['id'])

    assert actual == expected

    response = await web_app_client.delete(
        '/v2/pipeline/',
        params={'consumer': consumer, 'id': pipeline['id']},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    pipeline_in_draft = copy.deepcopy(pipeline)
    pipeline_in_draft['state'] = 'active'
    pipeline_in_draft['consumer'] = consumer

    common.remove_deprecated_fields(pipeline)
    pipeline['consumer'] = consumer

    del external_requests[1]['request_id']

    expected_external_requests = [
        {
            '_method': 'POST',
            '_path': '/new-service/v1/js/pipeline/compile',
            'extended_check': True,
            'pipeline': copy.deepcopy(pipeline),
        },
        {
            '_method': 'POST',
            '_path': '/taxi_approvals/drafts/create/',
            'api_path': 'admin_pipeline/pipelines',
            'data': pipeline_in_draft,
            'mode': 'push',
            'run_manually': False,
            'service_name': 'admin-pipeline',
        },
        {
            '_method': 'POST',
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                'admin_pipeline/pipelines/new-consumer',
            ],
            'change_doc_ids': [
                'admin_pipeline/pipelines_test-id',
                'admin_pipeline/pipelines/new-consumer_test-id',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
        {
            '_method': 'POST',
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                'admin_pipeline/pipelines/new-consumer',
            ],
            'change_doc_ids': [
                'admin_pipeline/pipelines_test-id',
                'admin_pipeline/pipelines/new-consumer_test-id',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
        {
            '_method': 'POST',
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                'admin_pipeline/pipelines/new-consumer',
            ],
            'change_doc_ids': [
                'admin_pipeline/pipelines_test-id',
                'admin_pipeline/pipelines/new-consumer_test-id',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
        {
            '_method': 'POST',
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                'admin_pipeline/pipelines/new-consumer',
            ],
            'change_doc_ids': [
                'admin_pipeline/pipelines_test-id',
                'admin_pipeline/pipelines/new-consumer_test-id',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
    ]

    if draft_status == 'need_approval':
        expected_external_requests.append(
            {
                '_path': f'/taxi_approvals/drafts/{draft_id}/',
                '_method': 'DELETE',
            },
        )

    # change service
    service = 'new-new-service'

    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _new_taxi_compile_pipeline(request):
        external_requests.append(request.json)
        external_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return {'metadata': {'stages': []}}

    pipeline['id'] = 'new-test-id'
    pipeline['state'] = 'valid'

    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    expected_external_requests.append(
        {
            '_method': 'POST',
            '_path': '/new-new-service/v1/js/pipeline/compile',
            'extended_check': True,
            'pipeline': pipeline,
        },
    )

    assert external_requests == expected_external_requests
