import datetime

import pytest


@pytest.fixture(name='taxi_approvals')
def _taxi_approvals(mockserver):
    class Context:
        pipeline_id: str
        consumer: str

    context = Context()

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _taxi_approvals_drafts_create(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': (
                    f'admin_pipeline/pipelines/'
                    f'{context.consumer}_{context.pipeline_id}'
                ),
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
        ]

    return context


async def test_activate(web_app_client, taxi_approvals, mockserver, load_json):
    taxi_approvals.pipeline_id = pipeline_id = 'test-id'
    taxi_approvals.consumer = consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    async def send_activate(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            '/v2/pipeline/activate', json=pipeline_doc,
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': pipeline_id,
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
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'active'
    pipeline['version'] = 0
    response = await send_activate(pipeline)
    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'pipeline': pipeline,
        'approvals_info': {
            'change_doc_id': (
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}'
            ),
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    # activate with substitution
    taxi_approvals.pipeline_id = pipeline_id = 'test-id2'

    pipeline = {
        'id': pipeline_id,
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
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'active'
    pipeline['version'] = 1
    pipeline['parent_id'] = 'test-id'

    response = await web_app_client.post(
        '/v2/pipeline/activate', json=pipeline,
    )
    assert response.status == 422
    assert await response.json() == {
        'code': 'invalid_pipeline',
        'message': 'No consumer',
    }

    response = await send_activate(pipeline)
    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'pipeline': pipeline,
        'approvals_info': {
            'change_doc_id': (
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}'
            ),
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    # activate missing
    pipeline['id'] = 'missing'
    response = await send_activate(pipeline)
    assert response.status == 404


async def test_activate_approved(
        web_app_client, taxi_approvals, mockserver, load_json,
):
    taxi_approvals.pipeline_id = pipeline_id = 'test-id'
    taxi_approvals.consumer = consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    async def send_activate(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            '/v2/pipeline/activate', json=pipeline_doc,
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': pipeline_id,
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
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'approved'
    response = await send_activate(pipeline)
    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'pipeline': pipeline,
        'approvals_info': {
            'change_doc_id': (
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}'
            ),
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'active'
    pipeline['version'] = 0
    pipeline['parent_id'] = 'test-id'

    response = await web_app_client.put(
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

    assert data == {
        'pipeline': pipeline,
        'approvals_info': {
            'change_doc_id': (
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}'
            ),
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }


async def test_unique_approved(
        web_app_client, taxi_approvals, mockserver, load_json,
):
    taxi_approvals.pipeline_id = pipeline_id = 'test-id'
    taxi_approvals.consumer = consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    async def send_activate(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            '/v2/pipeline/activate', json=pipeline_doc,
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': pipeline_id,
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
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'approved'
    response = await send_activate(pipeline)
    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'pipeline': pipeline,
        'approvals_info': {
            'change_doc_id': (
                f'admin_pipeline/pipelines/{consumer}_{pipeline["id"]}'
            ),
            'status': 'succeeded',
            'created_by': 'vryanova',
        },
    }

    taxi_approvals.pipeline_id = pipeline_id = 'test_id_invalid'

    pipeline = {
        'id': pipeline_id,
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
    pipeline['created'] = pipeline['updated'] = now
    pipeline['state'] = 'approved'
    response = await send_activate(pipeline)
    assert response.status == 422


async def test_activate_fail(
        web_app_client, taxi_approvals, mockserver, load_json,
):
    taxi_approvals.pipeline_id = pipeline_id = 'test-id'
    taxi_approvals.consumer = consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    async def send_activate(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            f'/v2/pipeline/activate', json=pipeline_doc,
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': pipeline_id,
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

    pipeline['state'] = 'active'
    response = await send_activate(pipeline)
    assert response.status == 400

    assert await response.text() == (
        '400: State transition from valid to active is not allowed'
    )

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    expected = pipeline.copy()
    expected['created'] = expected['updated'] = now
    expected['state'] = 'valid'

    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': consumer, 'id': pipeline['id']},
    )
    assert response.status == 200
    data = await response.json()

    assert data['pipeline'] == expected


@pytest.mark.parametrize('code', [200, 422])
async def test_activate_remove(
        web_app_client, taxi_approvals, mockserver, load_json, code,
):
    taxi_approvals.pipeline_id = pipeline_id = '5de7baf5eb70bf332afa25f1'
    taxi_approvals.consumer = consumer = 'taxi-surge'
    service = 'surge-calculator'

    reason_map = {'non_blocking': '' if code == 200 else '<error message>'}

    @mockserver.json_handler(
        '/surge-calculator/v1/js/pipeline/is-safe-to-deactivate',
    )
    def _taxi_is_safe_to_deactivate_pipeline(request):
        return {'unsafe_reason': reason_map.get(request.query['name'], '')}

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(request):
        return {'metadata': dict()}

    async def send_activate(pipeline_doc):
        pipeline_doc['consumer'] = consumer
        response = await web_app_client.post(
            f'/v2/pipeline/activate', json=pipeline_doc,
        )
        del pipeline_doc['consumer']
        return response

    pipeline = {
        'id': pipeline_id,
        'name': 'non_blocking',
        'state': 'removed',
        'comment': 'test_comment',
        'stages': [],
    }

    response = await send_activate(pipeline)
    assert response.status == code
    expected = (
        {}
        if code == 200
        else {
            'message': 'Unable to delete - <error message>',
            'code': 'invalid_pipeline',
        }
    )
    assert await response.json() == expected
