import pytest


@pytest.mark.parametrize(
    [
        'request_clown_branch_id',
        'expected_resp_code',
        'expected_resp_json',
        'expected_branch_juggler_host',
        'expected_branches_times_called',
        'expected_services_times_called',
    ],
    [
        pytest.param(
            777,
            200,
            {
                'clown_branch_id': 777,
                'juggler_host': 'some_direct_link_stable',
            },
            [[777, 'some_direct_link_stable', False]],
            1,
            1,
            id='happy path nanny',
        ),
        pytest.param(
            776,
            200,
            {
                'clown_branch_id': 776,
                'juggler_host': 'pg_some_project_postgres_service_stable',
            },
            [[776, 'pg_some_project_postgres_service_stable', False]],
            1,
            1,
            id='happy path postgres',
        ),
        pytest.param(
            775,
            200,
            {
                'clown_branch_id': 775,
                'juggler_host': 'some_direct_link_stable',
            },
            [
                [775, 'some_direct_link_stable', False],
                [777, 'some_direct_link_stable', False],
            ],
            3,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager',
                files=['conflicting_stable_pre_stable.sql'],
            ),
            id=(
                'multiple branches for juggler host from '
                'same service/environment'
            ),
        ),
        pytest.param(
            1,
            400,
            {
                'message': (
                    'Stable clown branch missing direct_link for '
                    'clown_service_id=1'
                ),
                'code': 'CLOWNDUCTOR_MISSING_DIRECT_LINK',
            },
            [],
            2,
            1,
            id='stable with empty direct_link',
        ),
        pytest.param(
            2,
            400,
            {
                'message': 'For some reason juggler_host suggest is empty',
                'code': 'EMPTY_JUGGLER_HOST',
            },
            [],
            1,
            1,
            id='last resort sanity check',
        ),
        pytest.param(
            773,
            400,
            {
                'message': (
                    'new_branch.service_id=228 conflicts with '
                    'db_branch.service_id=665'
                ),
                'code': 'BRANCH_CONFLICT',
            },
            [[776, 'pg_some_project_postgres_service_stable', False]],
            2,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager', files=['conflicting_by_service.sql'],
            ),
            id='multiple branches for juggler host from different services',
        ),
        pytest.param(
            772,
            400,
            {
                'message': (
                    'new_branch.env=testing conflicts with '
                    'db_branch.env=stable'
                ),
                'code': 'BRANCH_CONFLICT',
            },
            [[777, 'some_direct_link_stable', False]],
            2,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager', files=['conflicting_by_env.sql'],
            ),
            id=(
                'multiple branches for juggler host from '
                'different environments'
            ),
        ),
        pytest.param(
            777,
            400,
            {
                'message': (
                    'branch is alreaady assigned to ' 'another juggler_host'
                ),
                'code': 'BRANCH_CONFLICT',
            },
            [[777, 'some_other_direct_link', False]],
            1,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager',
                files=['conflicting_clown_branch_id.sql'],
            ),
            id=(
                'try to create policy for clown_branch_id, '
                'which already has policy created. '
                'juggler_host_suggest from clown '
                'differs from stored in database'
            ),
        ),
        pytest.param(
            777,
            200,
            {
                'clown_branch_id': 777,
                'juggler_host': 'some_direct_link_stable',
            },
            [
                [777, 'some_direct_link_stable', False],
                [777, 'some_other_direct_link', True],
            ],
            1,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager',
                files=['conflicting_clown_branch_id_deleted.sql'],
            ),
            id=(
                'try to create policy for clown_branch_id, which has '
                'deleted policy with other juggler_host'
            ),
        ),
        pytest.param(
            777,
            200,
            {
                'clown_branch_id': 777,
                'juggler_host': 'some_direct_link_stable',
            },
            [[777, 'some_direct_link_stable', False]],
            1,
            1,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager', files=['idempotency.sql'],
            ),
            id='test if handler is idempotent',
        ),
        pytest.param(
            228,
            400,
            {
                'code': 'BAD_BRANCH_ENV',
                'message': 'Branch env=nonexistent is not supported',
            },
            [],
            1,
            0,
            id='bad branch env',
        ),
        pytest.param(
            774,
            400,
            {
                'code': 'BAD_CLUSTER_TYPE',
                'message': 'cluster_type=mongo_lxc is not supported',
            },
            [],
            1,
            1,
            id='bad cluster type',
        ),
    ],
)
async def test_simple(
        taxi_clowny_alert_manager_web,
        fetch_db_branch_juggler_host,
        load_json,
        mock_clownductor,
        request_clown_branch_id,
        expected_resp_code,
        expected_resp_json,
        expected_branch_juggler_host,
        expected_branches_times_called,
        expected_services_times_called,
):
    await taxi_clowny_alert_manager_web.invalidate_caches()

    @mock_clownductor('/v1/branches/')
    def _mock_branches(request):
        branch_id = request.query.get('branch_id')
        branch_ids = request.query.get('branch_ids')
        service_id = request.query.get('service_id')
        data = load_json('branches_response.json')

        if branch_id:
            return [data[branch_id]]
        if branch_ids:
            return [data[id_] for id_ in branch_ids.split(',')]
        if service_id:
            return [
                item
                for item in data.values()
                if item['service_id'] == int(service_id)
            ]

        raise ValueError

    @mock_clownductor('/v1/services/')
    def _mock_services(request):
        data = load_json('services_response.json')
        service_id = request.query['service_id']

        return [data[service_id]]

    response = await taxi_clowny_alert_manager_web.post(
        '/v1/policy', params={'clown_branch_id': request_clown_branch_id},
    )

    assert response.status == expected_resp_code
    assert await response.json() == expected_resp_json

    assert fetch_db_branch_juggler_host() == expected_branch_juggler_host
    assert _mock_branches.times_called == expected_branches_times_called
    assert _mock_services.times_called == expected_services_times_called


@pytest.mark.parametrize(
    [
        'request_clown_branch_id',
        'expected_resp_code',
        'expected_resp_json',
        'expected_branch_juggler_host',
        'expected_projects_times_called',
        'expected_services_times_called',
        'expected_branches_times_called',
        'expected_tp_times_called',
    ],
    [
        pytest.param(
            777,
            200,
            {
                'clown_branch_id': 777,
                'juggler_host': 'some_direct_link_stable',
                'job_id': 123,
            },
            [[777, 'some_direct_link_stable', False]],
            1,
            1,
            2,
            1,
            id='happy path nanny',
        ),
        pytest.param(
            5,
            200,
            {
                'clown_branch_id': 5,
                'juggler_host': 'some_direct_link_testing',
                'job_id': 123,
            },
            [[5, 'some_direct_link_testing', False]],
            1,
            1,
            2,
            1,
            id='happy path nanny testing',
        ),
        pytest.param(
            776,
            200,
            {
                'clown_branch_id': 776,
                'juggler_host': 'pg_some_project_postgres_service_stable',
                'job_id': 123,
            },
            [[776, 'pg_some_project_postgres_service_stable', False]],
            1,
            1,
            1,
            1,
            id='happy path postgres',
        ),
        pytest.param(
            775,
            200,
            {
                'clown_branch_id': 775,
                'juggler_host': 'some_direct_link_stable',
            },
            [
                [775, 'some_direct_link_stable', False],
                [777, 'some_direct_link_stable', False],
            ],
            0,
            1,
            3,
            0,
            marks=pytest.mark.pgsql(
                'clowny_alert_manager',
                files=['conflicting_stable_pre_stable.sql'],
            ),
            id=(
                'multiple branches for juggler host from '
                'same service/environment'
            ),
        ),
        pytest.param(
            4,
            400,
            {
                'message': (
                    'Failed to retrieve direct_links '
                    'on diff proposal generation'
                ),
                'code': 'CLOWNDUCTOR_MISSING_DIRECT_LINK',
            },
            [[4, 'some_direct_link_stable', False]],
            0,
            1,
            2,
            0,
            id='empty pre_stable direct_link',
        ),
    ],
)
async def test_with_default_check_file_generation(
        taxi_clowny_alert_manager_web,
        fetch_db_branch_juggler_host,
        load_json,
        mock_arcanum,
        mock_clownductor,
        mock_task_processor,
        request_clown_branch_id,
        expected_resp_code,
        expected_resp_json,
        expected_branch_juggler_host,
        expected_projects_times_called,
        expected_services_times_called,
        expected_branches_times_called,
        expected_tp_times_called,
):
    await taxi_clowny_alert_manager_web.invalidate_caches()

    @mock_clownductor('/v1/projects/')
    def _mock_projects(request):
        data = load_json('projects_response.json')
        project_name = request.query['name']

        return [data[project_name]]

    @mock_clownductor('/v1/services/')
    def _mock_services(request):
        data = load_json('services_response.json')
        service_id = request.query['service_id']

        return [data[service_id]]

    @mock_clownductor('/v1/branches/')
    def _mock_branches(request):
        branch_id = request.query.get('branch_id')
        branch_ids = request.query.get('branch_ids')
        service_id = request.query.get('service_id')
        data = load_json('branches_response.json')

        if branch_id:
            return [data[branch_id]]
        if branch_ids:
            return [data[id_] for id_ in branch_ids.split(',')]
        if service_id:
            return [
                item
                for item in data.values()
                if item['service_id'] == int(service_id)
            ]

        raise ValueError

    @mock_arcanum(
        r'/api/v1/repos/(?P<repo_name>[^/]+)/tree/node(?P<path>.+)',
        regex=True,
    )
    def _mock_tree_node(request, repo_name, path):
        return {'data': {}}

    @mock_task_processor('/v1/jobs/start/')
    def _mock_jobs_start(request):
        data = load_json('expected_pr_content.json')
        assert request.json == data[f'{request_clown_branch_id}']

        return {'job_id': 123}

    response = await taxi_clowny_alert_manager_web.post(
        '/v1/policy',
        params={
            'clown_branch_id': request_clown_branch_id,
            'generate_default_check_file': True,
        },
    )

    assert response.status == expected_resp_code
    assert await response.json() == expected_resp_json

    assert fetch_db_branch_juggler_host() == expected_branch_juggler_host
    assert _mock_projects.times_called == expected_projects_times_called
    assert _mock_services.times_called == expected_services_times_called
    assert _mock_branches.times_called == expected_branches_times_called
    assert _mock_jobs_start.times_called == expected_tp_times_called
