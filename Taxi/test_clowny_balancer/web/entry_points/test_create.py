import pytest

from testsuite.utils import matching


def _request(**kwargs):
    return {
        'namespace_id': 1,
        'branch_id': 1,
        'fqdn': 'some.net',
        'protocol': 'http',
        'awacs_backend_id': 'service_stable',
        'awacs_upstream_id': 'custom-stable',
        **kwargs,
    }


@pytest.mark.usefixtures('mock_clownductor_handlers')
@pytest.mark.parametrize('use_drafts', [True, False])
@pytest.mark.parametrize(
    'data, expected_status, expected_result',
    [
        pytest.param(
            _request(namespace_id=100500),
            404,
            {'code': 'NOT_FOUND', 'message': 'Namespace 100500 not found'},
            id='namespace_not_found',
        ),
        pytest.param(
            _request(namespace_id=2, fqdn='test.net'),
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Entry point for fqdn "http://test.net" already exists'
                ),
            },
            id='duplicated_entry_point',
        ),
        pytest.param(
            _request(namespace_id=4),
            200,
            {'job_id': 1},
            id='ok_for_extending_shared',
        ),
        pytest.param(
            _request(namespace_id=3),
            200,
            {'job_id': 1},
            id='ok_for_extending_empty',
        ),
        pytest.param(
            _request(namespace_id=3, branch_id=10),
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'Branch for id 10 not found in clownductor',
            },
            id='not_found_any_branches',
        ),
        pytest.param(
            _request(namespace_id=3, branch_id=3),
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Cant create entry point for branch taxi_service_testing '
                    'in namespace ccc.net (stable) cause of environs mismatch'
                ),
            },
            id='cant_create_for_env_mismatch',
        ),
        pytest.param(
            _request(namespace_id=3, branch_id=5),
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Cant create entry point for tank branch taxi_service_tank'
                ),
            },
            id='cant_create_for_env_tank',
        ),
        pytest.param(
            _request(namespace_id=1, fqdn='more.net'),
            200,
            {'job_id': 1},
            id='ok for alike fqdn',
        ),
        pytest.param(
            _request(namespace_id=1, fqdn='http://more.net'),
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'fqdn http://more.net must be write without protocol'
                ),
            },
            id='fqdn with protocol',
        ),
    ],
)
async def test_create(
        mock_task_processor_start_job,
        taxi_clowny_balancer_web,
        use_drafts,
        data,
        expected_status,
        expected_result,
        load_json,
):
    mock_task_processor_start_job()

    if not use_drafts:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/create/', json=data,
        )
        result = await response.json()
        assert response.status == expected_status, result
        if expected_result is not None:
            assert result == expected_result
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/create/check/', json=data,
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_status != 200:
        return
    expected_check_result = load_json(
        f'check_handler_namespace_{data["namespace_id"]}_response.json',
    )
    assert expected_check_result == result

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/create/apply/',
        json=result['data'],
        headers={
            'X-YaTaxi-Ticket': 'COOLTICKET-1',
            'X-Yandex-Login': 'deoevgen',
        },
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_result is not None:
        assert result == expected_result


@pytest.mark.usefixtures('mock_clownductor_handlers')
@pytest.mark.parametrize('use_drafts', [True, False])
@pytest.mark.parametrize(
    'data, expected_status, expected_result, job_params',
    [
        (
            {'service_id': 1},
            200,
            {'job_id': 1},
            {
                'change_doc_id': 'EntryPointCreate-prestable-1',
                'idempotency_token': matching.any_string,
                'job_vars': {
                    'awacs_backend_id': 'taxi_service_prestable',
                    'awacs_domain_id': 'test-pre.net',
                    'awacs_upstream_id': 'taxi_service_prestable',
                    'clown_branch_id': 2,
                    'clown_service_id': 1,
                    'env': 'prestable',
                    'fqdn': 'test-pre.net',
                    'lock_name': 'test-pre.net:taxi_service_prestable',
                    'namespace_id': 1,
                    'protocol': 'http',
                    'st_ticket': 'COOLTICKET-1',
                    'author': 'deoevgen',
                },
                'provider_name': 'clowny-balancer',
                'recipe_name': 'EntryPointCreate',
            },
        ),
        (
            {'service_id': 2},
            200,
            {'job_id': 1},
            {
                'change_doc_id': 'EntryPointCreate-prestable-2',
                'idempotency_token': matching.any_string,
                'job_vars': {
                    'awacs_backend_id': 'taxi_one-service_stable',
                    'awacs_domain_id': 'one-more-pre.net',
                    'awacs_upstream_id': 'taxi_one-service_stable',
                    'clown_branch_id': 4,
                    'clown_service_id': 2,
                    'env': 'prestable',
                    'fqdn': 'one-more-pre.net',
                    'lock_name': 'one-more-pre.net:taxi_one-service_stable',
                    'namespace_id': 5,
                    'protocol': 'http',
                    'st_ticket': 'COOLTICKET-1',
                    'author': 'deoevgen',
                },
                'provider_name': 'clowny-balancer',
                'recipe_name': 'EntryPointCreate',
            },
        ),
    ],
)
async def test_create_prestable(
        mock_task_processor,
        taxi_clowny_balancer_web,
        use_drafts,
        data,
        expected_status,
        expected_result,
        job_params,
):
    @mock_task_processor('/v1/jobs/start/')
    def _start_job_handler(request):
        if not use_drafts:
            job_params['job_vars']['st_ticket'] = ''
            job_params['job_vars']['author'] = ''
        assert request.json == job_params
        return {'job_id': 1}

    if not use_drafts:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/create-prestable/', json=data,
        )
        result = await response.json()
        assert response.status == expected_status, result
        if expected_result is not None:
            assert result == expected_result
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/create-prestable/check/', json=data,
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_status != 200:
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/create-prestable/apply/',
        json=result['data'],
        headers={
            'X-YaTaxi-Ticket': 'COOLTICKET-1',
            'X-Yandex-Login': 'deoevgen',
        },
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_result is not None:
        assert result == expected_result
