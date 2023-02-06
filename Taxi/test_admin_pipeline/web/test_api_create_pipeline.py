import copy
import datetime
import uuid

import pytest

from . import common


@pytest.mark.now('2019-12-16T23:00:00+03:00')
async def test_create(web_app_client, load_json, mockserver):
    consumer = 'taxi-surge'

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f0',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f1',
                ),
                'status': 'succeeded',
                'created_by': 'islam-boziev',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f3',
                ),
                'status': 'succeeded',
                'created_by': 'username',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', 'test_id',
                ),
                'status': 'succeeded',
                'created_by': 'islam-boziev',
            },
        ]

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
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

    expected = load_json('taxi_enumerate_expected.json')

    expected.append(
        {
            'approvals_info': {
                'change_doc_id': 'admin_pipeline/pipelines_test_id',
                'created_by': 'islam-boziev',
                'status': 'succeeded',
            },
            'comment': 'test_comment',
            'created': '2019-12-16T23:00:00+03:00',
            'id': 'test_id',
            'name': 'test_name',
            'state': 'draft',
            'updated': '2019-12-16T23:00:00+03:00',
        },
    )
    actual = sorted(await response.json(), key=lambda x: x['id'])

    assert actual == expected


async def test_create_with_parent(web_app_client, load_json):
    consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    pipeline = {
        'id': 'test_id',
        'parent_id': 'test_parent_id',
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

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()
    assert data['pipeline']['parent_id'] == 'test_parent_id'


async def test_create_in_binding_hierarchy(web_app_client):
    consumer = 'taxi-surge'

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': [
            {
                'name': 'sample_in_hierarchy',
                'optional': False,
                'in_bindings': [
                    {
                        'domain': 'input',
                        'query': 'level_0',
                        'children': [
                            {
                                'query': 'level_1_a',
                                'children': [{'query': 'level_2_a'}],
                            },
                            {'query': 'level_1_b'},
                            {'query': 'level_1_c'},
                        ],
                    },
                ],
                'out_bindings': [],
                'conditions': [],
                'source_code': 'return {};',
            },
        ],
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


@pytest.mark.parametrize(
    'stage,error',
    [
        (
            {
                'name': 'sample_resource_fetch',
                'optional': False,
                'in_bindings': [],
                'conditions': [
                    {
                        'type': 'stage_status',
                        'stage_name': 'initialization',
                        'stage_statuses': ['passed'],
                    },
                ],
                'resources': [{'name': 'sample_resource_non_blocking'}],
                'out_bindings': [],
                'source_code': '',
            },
            '400: Invalid pipeline: at stage index 6: stage with name '
            '"sample_resource_fetch" is already defined, '
            'at stage index 6: Invalid pipeline stage: must be either '
            'logic, fetch or predicate',
        ),
        (
            {
                'name': 'sample_resource_fetch',
                'optional': False,
                'in_bindings': [],
                'conditions': [
                    {
                        'type': 'stage_status',
                        'stage_name': 'initialization',
                        'stage_statuses': ['passed'],
                    },
                ],
                'source_code': '',
            },
            '400: Invalid pipeline: at stage index 6: stage with name '
            '"sample_resource_fetch" is already defined, '
            'at stage index 6: Invalid pipeline stage: must be either '
            'logic, fetch or predicate',
        ),
        (
            {
                'name': 'sample_resource.fetch',
                'optional': False,
                'in_bindings': [],
                'conditions': [
                    {
                        'type': 'stage_status',
                        'stage_name': 'initialization',
                        'stage_statuses': ['passed'],
                    },
                ],
                'out_bindings': [],
                'source_code': '',
            },
            '',
        ),
        (
            {
                'name': '1_sample_resource_fetch',
                'optional': False,
                'in_bindings': [],
                'conditions': [
                    {
                        'type': 'stage_status',
                        'stage_name': 'initialization',
                        'stage_statuses': ['passed'],
                    },
                ],
                'out_bindings': [],
                'source_code': '',
            },
            '',
        ),
        (
            {
                'name': 'sample_resource_fetch',
                'optional': False,
                'in_bindings': [],
                'conditions': [
                    {
                        'type': 'stage_status',
                        'stage_name': '1_initialization',
                        'stage_statuses': ['passed'],
                    },
                ],
                'out_bindings': [],
                'source_code': '',
            },
            '',
        ),
    ],
    ids=['case_{}'.format(i) for i in range(5)],
)
async def test_create_bad(web_app_client, load_json, mockserver, stage, error):
    consumer = 'taxi-surge'

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    f'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f0',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    f'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f1',
                ),
                'status': 'succeeded',
                'created_by': 'islam-boziev',
            },
            {
                'change_doc_id': '{}_{}'.format(
                    f'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f3',
                ),
                'status': 'succeeded',
                'created_by': 'username',
            },
        ]

    pipeline = {
        'id': 'test_id',
        'name': 'test_name',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }
    pipeline['stages'].append(stage)

    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 400
    if error:
        assert await response.text() == error

    response = await web_app_client.post(
        '/v2/pipeline/enumerate/', params={'consumer': consumer},
    )
    assert response.status == 200

    expected = load_json('enumerate_expected.tpl.json')

    for item in expected:
        item['approvals_info']['change_doc_id'] = item['approvals_info'][
            'change_doc_id'
        ].format(consumer)

    actual = sorted(await response.json(), key=lambda x: x['id'])

    assert actual == expected


async def test_create_existing_fail(
        web_app_client, mockserver, load_json, mongodb,
):
    consumer = 'taxi-surge'

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': '{}_{}'.format(
                    'admin_pipeline/pipelines', '5de7baf5eb70bf332afa25f0',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
        ]

    mongodb.admin_pipeline_pipelines.update(
        {}, {'$set': {'consumer': consumer}},
    )

    pipeline = {
        'id': '5de7baf5eb70bf332afa25f0',
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
    assert response.status != 200

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': consumer, 'id': '5de7baf5eb70bf332afa25f0'},
    )
    assert response.status == 200

    expected = load_json('tpl_get_5de7baf5eb70bf332afa25f0.json')
    expected['approvals_info']['change_doc_id'] = expected['approvals_info'][
        'change_doc_id'
    ].format(consumer=consumer)

    actual = await response.json()

    assert actual == expected


async def test_create_approve(web_app_client, mockserver, load_json):
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
                'change_doc_id': f'admin_pipeline/pipelines_{pipeline_id}',
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
        'state': 'approving',
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
    expected = copy.deepcopy(pipeline)
    expected['created'] = expected['updated'] = now
    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )

    assert response.status == 200
    assert await response.json() == {
        'pipeline': expected,
        'approvals_info': {
            'change_doc_id': f'admin_pipeline/pipelines_{pipeline["id"]}',
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    expected = copy.deepcopy(pipeline)
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

    pipeline['consumer'] = consumer

    # since dynamic consumer doesn't use codegen client,
    # it won't add defaults from schema
    common.remove_deprecated_fields(pipeline)

    assert compile_requests == [{'extended_check': True, 'pipeline': pipeline}]
