import copy
import datetime
import uuid

from . import common


async def test_update(web_app_client, mockserver, load_json, mongodb):
    consumer = 'taxi-surge'
    calculator = 'surge-calculator'
    compile_requests = []

    @mockserver.json_handler(f'/{calculator}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        compile_requests.append(request.json)
        return {'metadata': dict()}

    mongodb.admin_pipeline_pipelines.update(
        {}, {'$set': {'consumer': consumer}},
    )

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
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
    pipeline['state'] = 'valid'
    pipeline['updated'] = now
    response = await web_app_client.put(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    expected = copy.deepcopy(pipeline)
    expected['created'] = expected['updated'] = now
    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': 'test_id'},
    )
    assert response.status == 200
    data = await response.json()

    assert data['pipeline'] == expected

    # update missing
    pipeline['id'] = 'missing'
    response = await web_app_client.put(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 404

    common.remove_deprecated_fields(pipeline)

    pipeline['id'] = 'test_id'
    pipeline['created'] = now
    pipeline['consumer'] = consumer

    assert compile_requests == [{'extended_check': True, 'pipeline': pipeline}]


async def test_update_approve(web_app_client, mockserver, load_json):
    consumer = 'taxi-surge'
    calculator = 'surge-calculator'
    approvals_requests = []

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _taxi_approvals_drafts_create(request):
        approvals_requests.append(request.json)
        approvals_requests[-1].update(_path=request.path)
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        approvals_requests.append(request.json)
        approvals_requests[-1].update(_path=request.path)
        pipeline_id = 'test-id'
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', pipeline_id,
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
        ]

    compile_requests = []

    @mockserver.json_handler(f'/{calculator}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        compile_requests.append(request.json)
        return {'metadata': dict()}

    pipeline = {
        'id': 'test-id',
        'name': 'test_name',
        'state': 'valid',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }
    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    expected_compile_requests = [
        {'extended_check': True, 'pipeline': pipeline.copy()},
    ]

    pipeline['state'] = 'approving'
    response = await web_app_client.put(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    pipeline['created'] = pipeline['updated'] = now

    expected_compile_requests.append(
        {'extended_check': True, 'pipeline': pipeline.copy()},
    )

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )

    assert response.status == 200
    expected = copy.deepcopy(pipeline)
    assert await response.json() == {
        'pipeline': expected,
        'approvals_info': {
            'change_doc_id': f'admin_pipeline/pipelines_{pipeline["id"]}',
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    expected['state'] = 'active'
    expected['consumer'] = consumer
    request_id = uuid.uuid4().hex

    for approvals_request in approvals_requests:
        if 'request_id' in approvals_request:
            approvals_request['request_id'] = request_id  # mock random number

    assert approvals_requests == [
        {
            '_path': '/taxi_approvals/drafts/create/',
            'api_path': 'admin_pipeline/pipelines',
            'data': expected,
            'mode': 'push',
            'request_id': request_id,
            'run_manually': False,
            'service_name': 'admin-pipeline',
        },
        {
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                f'admin_pipeline/pipelines/{consumer}',
            ],
            'change_doc_ids': [
                f'admin_pipeline/pipelines_{pipeline["id"]}',
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
    ]

    for compile_request in expected_compile_requests:
        compile_request['pipeline']['consumer'] = consumer
        common.remove_deprecated_fields(compile_request['pipeline'])

    assert compile_requests == expected_compile_requests
