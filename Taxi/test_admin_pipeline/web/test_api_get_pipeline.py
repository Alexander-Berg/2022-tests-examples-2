import pytest


@pytest.mark.parametrize('return_new_api_path', [False, True])
async def test_get(web_app_client, mockserver, load_json, return_new_api_path):
    # check for existing static consumer name
    await web_app_client.post(
        f'/taxi-surge/register/',
        json={
            'service_balancer_hostname': 'surge-calculator',
            'service_tvm_name': 'surge-calculator',
        },
    )

    change_doc_id = '{}_{}'.format(
        f'admin_pipeline/pipelines'
        f'{"" if return_new_api_path else "/taxi-surge"}',
        '5de7baf5eb70bf332afa25f0',
    )

    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': change_doc_id,
                'status': 'succeeded',
                'created_by': 'vryanova',
            },
        ]

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'id': '5de7baf5eb70bf332afa25f0'},
    )
    assert response.status == 200

    expected = load_json('taxi_get_5de7baf5eb70bf332afa25f0.json')
    expected['approvals_info']['change_doc_id'] = change_doc_id
    actual0 = await response.json()

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'active_name': 'default'},
    )
    assert response.status == 200
    actual1 = await response.json()

    assert actual0 == actual1 == expected

    # query missing
    response = await web_app_client.get(
        '/v2/pipeline/', params={'consumer': 'taxi-surge', 'id': 'missing'},
    )
    assert response.status == 404

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'active_name': 'missing'},
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'params',
    [{}, {'id': '5de7baf5eb70bf332afa25f0', 'active_name': 'default'}],
)
async def test_get_bad(web_app_client, mockserver, params):
    consumer = 'new-consumer'
    service = 'new-service'

    params.setdefault('consumer', consumer)

    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

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
        ]

    response = await web_app_client.get('/v2/pipeline/', params=params)
    assert response.status == 400
    assert await response.text() == (
        '400: Must specify either id, child_id or active_name'
    )


@pytest.mark.filldb(admin_pipeline_pipelines='dublicate_names')
async def test_same_names_for_different_consumers(
        web_app_client, mockserver, load_json,
):
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

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={'consumer': 'taxi-surge', 'active_name': 'default'},
    )
    assert response.status == 200
    actual = await response.json()

    assert actual == {
        'approvals_info': {
            'change_doc_id': (
                'admin_pipeline/pipelines_5de7baf5eb70bf332afa25f0'
            ),
            'created_by': 'vryanova',
            'status': 'succeeded',
        },
        'pipeline': {
            'comment': 'Taxi surge pipeline',
            'created': '2019-12-16T23:38:47+03:00',
            'id': '5de7baf5eb70bf332afa25f0',
            'name': 'default',
            'stages': [
                {
                    'conditions': [],
                    'in_bindings': [],
                    'name': 'start',
                    'optional': False,
                    'out_bindings': [{'alias': 'places', 'query': 'places'}],
                    'source_code': 'return {places: []};',
                },
            ],
            'state': 'active',
            'updated': '2019-12-16T23:38:47+03:00',
            'version': 0,
        },
    }


async def test_get_parent(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return [
            {
                'change_doc_id': (
                    'admin_pipeline/pipelines_5de7baf5eb70bf332afa25f2'
                ),
                'status': 'succeeded',
                'created_by': 'username',
            },
        ]

    response = await web_app_client.get(
        '/v2/pipeline/',
        params={
            'consumer': 'taxi-surge',
            'child_id': '5de7baf5eb70bf332afa25f3',
        },
    )

    assert response.status == 200
    actual = await response.json()

    assert actual == {
        'approvals_info': {
            'change_doc_id': (
                'admin_pipeline/pipelines_5de7baf5eb70bf332afa25f2'
            ),
            'status': 'succeeded',
            'created_by': 'username',
        },
        'pipeline': {
            'id': '5de7baf5eb70bf332afa25f2',
            'comment': 'comment 3',
            'created': '2019-12-16T23:38:47+03:00',
            'name': 'non_blocking',
            'stages': [],
            'state': 'removed',
            'updated': '2019-12-16T23:38:47+03:00',
            'version': 0,
        },
    }
