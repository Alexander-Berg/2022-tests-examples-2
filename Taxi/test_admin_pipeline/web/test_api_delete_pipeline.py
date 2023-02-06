import datetime
import uuid

import pytest  # noqa: F401


@pytest.mark.parametrize('return_new_api_path', [False, True])
async def test_delete(
        web_app_client, mockserver, load_json, return_new_api_path,
):
    @mockserver.json_handler(
        '/surge-calculator/v1/js/pipeline/is-safe-to-deactivate',
    )
    def _taxi_is_safe_to_deactivate_pipeline(request):
        reason_map = {'non_blocking': '<error message>'}
        return {'unsafe_reason': reason_map.get(request.query['name'], '')}

    # try remove in use
    pipeline_id = '5de7baf5eb70bf332afa25f1'

    response = await web_app_client.delete(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': pipeline_id},
        headers={'X-Yandex-Login': 'testsuite'},
    )

    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': 'Unable to delete - <error message>',
    }

    # draft with the same name as in use
    draft_pipeline = {
        'id': 'test_id',
        'name': 'non_blocking',
        'state': 'draft',
        'stages': [],
    }
    create_response = await web_app_client.post(
        '/v2/pipeline/',
        json=draft_pipeline,
        params={'consumer': 'taxi-surge'},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert create_response.status == 200
    delete_response = await web_app_client.delete(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': draft_pipeline['id']},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert delete_response.status == 200

    # remove
    pipeline_id = '5de7baf5eb70bf332afa25f3'
    response = await web_app_client.delete(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': pipeline_id},
        headers={'X-Yandex-Login': 'testsuite'},
    )

    assert response.status == 200

    def make_change_doc_id(doc_id: str) -> str:
        return '{}_{}'.format(
            f'admin_pipeline/pipelines'
            f'{"" if return_new_api_path else "/taxi-surge"}',
            doc_id,
        )

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': make_change_doc_id(
                    '5de7baf5eb70bf332afa25f0',
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
            {
                'change_doc_id': make_change_doc_id(
                    '5de7baf5eb70bf332afa25f1',
                ),
                'status': 'succeeded',
                'created_by': 'islam-boziev',
            },
            {
                'change_doc_id': make_change_doc_id(
                    '5de7baf5eb70bf332afa25f3',
                ),
                'status': 'succeeded',
                'created_by': 'username',
            },
        ]

    response = await web_app_client.post(
        '/v2/pipeline/enumerate/', params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200

    expected = list(
        filter(
            lambda x: x['id'] != pipeline_id,
            load_json('taxi_enumerate_expected.json'),
        ),
    )

    for e_item in expected:
        if 'approvals_info' in e_item:
            e_item['approvals_info']['change_doc_id'] = make_change_doc_id(
                e_item['id'],
            )

    actual = sorted(await response.json(), key=lambda x: x['id'])

    assert actual == expected


@pytest.mark.parametrize('draft_status', ['need_approval', 'succeeded'])
async def test_delete_approval_recall(
        web_app_client, mockserver, load_json, draft_status,
):
    draft_id = 1
    approvals_requests = []

    @mockserver.json_handler('/taxi_approvals/drafts/1/')
    def _taxi_approvals_drafts_1(request):
        approvals_requests.append({})
        approvals_requests[-1].update(
            _path=request.path, _method=request.method,
        )
        return {}

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
                'id': draft_id,
                'change_doc_id': f'admin_pipeline/pipelines_{pipeline_id}',
                'status': draft_status,
                'created_by': 'testsuite',
            },
        ]

    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    pipeline = {
        'id': 'test-id',
        'name': 'new',
        'state': 'approving',
        'comment': 'test_comment',
        'stages': load_json('pipeline_stages.json'),
    }
    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': 'taxi-surge'},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    expected = pipeline.copy()
    expected['created'] = expected['updated'] = now
    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': pipeline['id']},
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json == {
        'pipeline': expected,
        'approvals_info': {
            'id': draft_id,
            'change_doc_id': f'admin_pipeline/pipelines_{pipeline["id"]}',
            'status': draft_status,
            'created_by': 'testsuite',
        },
    }

    expected = pipeline.copy()
    expected['state'] = 'active'
    expected['consumer'] = 'taxi-surge'
    request_id = uuid.uuid4().hex

    for approvals_request in approvals_requests:
        if 'request_id' in approvals_request:
            approvals_request['request_id'] = request_id  # mock random number

    approvals_requests_expected = [
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
                'admin_pipeline/pipelines/taxi-surge',
            ],
            'change_doc_ids': [
                f'admin_pipeline/pipelines_{pipeline["id"]}',
                f'admin_pipeline/pipelines/taxi-surge_{pipeline["id"]}',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
    ]

    assert approvals_requests == approvals_requests_expected

    response = await web_app_client.delete(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': pipeline['id']},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    approvals_requests_expected.append(
        {
            '_path': '/taxi_approvals/drafts/list/',
            'api_paths': [
                'admin_pipeline/pipelines',
                'admin_pipeline/pipelines/taxi-surge',
            ],
            'change_doc_ids': [
                f'admin_pipeline/pipelines_{pipeline["id"]}',
                f'admin_pipeline/pipelines/taxi-surge_{pipeline["id"]}',
            ],
            'offset': '0',
            'service_name': 'admin-pipeline',
        },
    )

    if draft_status == 'need_approval':
        approvals_requests_expected.append(
            {
                '_path': f'/taxi_approvals/drafts/{draft_id}/',
                '_method': 'DELETE',
            },
        )

    assert approvals_requests == approvals_requests_expected
