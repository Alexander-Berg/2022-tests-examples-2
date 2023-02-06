import os

import pytest


@pytest.mark.pgsql('clowny_alert_manager', files=['simple.sql'])
@pytest.mark.parametrize(
    ['clown_branch_id', 'expected_branch_juggler_host'],
    [
        (
            777,
            [
                [444, 'some_direct_link2', False],
                [555, 'some_pg_direct_link', False],
                [777, 'some_direct_link', True],
            ],
        ),
        (
            666,
            [
                [444, 'some_direct_link2', False],
                [555, 'some_pg_direct_link', False],
                [777, 'some_direct_link', False],
            ],
        ),
    ],
)
async def test_simple(
        taxi_clowny_alert_manager_web,
        fetch_db_branch_juggler_host,
        clown_branch_id,
        expected_branch_juggler_host,
):
    response = await taxi_clowny_alert_manager_web.delete(
        '/v1/policy', params={'clown_branch_id': clown_branch_id},
    )

    assert response.status == 200

    assert fetch_db_branch_juggler_host() == expected_branch_juggler_host


@pytest.mark.pgsql('clowny_alert_manager', files=['simple.sql'])
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
            {'job_id': 123},
            [
                [444, 'some_direct_link2', False],
                [555, 'some_pg_direct_link', False],
                [777, 'some_direct_link', True],
            ],
            1,
            1,
            1,
            1,
        ),
        pytest.param(
            666,
            200,
            {'job_id': 123},
            [
                [444, 'some_direct_link2', False],
                [555, 'some_pg_direct_link', False],
                [777, 'some_direct_link', False],
            ],
            1,
            1,
            1,
            1,
        ),
        pytest.param(
            555,
            400,
            {
                'message': 'cluster_type=postgres is not supported',
                'code': 'BAD_CLUSTER_TYPE',
            },
            [
                [444, 'some_direct_link2', False],
                [555, 'some_pg_direct_link', True],
                [777, 'some_direct_link', False],
            ],
            0,
            1,
            1,
            0,
        ),
        pytest.param(
            444,
            200,
            {},
            [
                [444, 'some_direct_link2', True],
                [555, 'some_pg_direct_link', False],
                [777, 'some_direct_link', False],
            ],
            1,
            1,
            1,
            0,
        ),
    ],
)
async def test_delete_default_check_file(
        taxi_clowny_alert_manager_web,
        fetch_db_branch_juggler_host,
        load_json,
        testpoint,
        mockserver,
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

    @mock_arcanum(
        r'/api/v1/repos/(?P<repo_name>[^/]+)/tree/node(?P<path>.+)',
        regex=True,
    )
    def _mock_get_review_requests(request, repo_name, path):
        assert repo_name == 'arc_vcs'
        assert request.query['commit_id'] == 'trunk'

        taxi_devops_prod = (
            '/taxi/infra/testing/infra-cfg-juggler'
            '/checks/production/taxi-devops.prod'
        )
        if path in [
                taxi_devops_prod,
                os.path.join(
                    taxi_devops_prod, 'rtc_taxi-devops_nanny_service_stable',
                ),
        ]:
            return {'data': {}}

        return mockserver.make_response(
            status=404,
            json={'errors': [{'status': '404', 'message': 'message'}]},
        )

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

    @mock_task_processor('/v1/jobs/start/')
    def _mock_jobs_start(request):
        data = load_json('expected_pr_content.json')
        assert request.json == data[f'{request_clown_branch_id}']

        return {'job_id': 123}

    response = await taxi_clowny_alert_manager_web.delete(
        '/v1/policy',
        params={
            'clown_branch_id': request_clown_branch_id,
            'delete_default_check_file': True,
        },
    )

    assert response.status == expected_resp_code
    assert await response.json() == expected_resp_json

    assert fetch_db_branch_juggler_host() == expected_branch_juggler_host
    assert _mock_projects.times_called == expected_projects_times_called
    assert _mock_services.times_called == expected_services_times_called
    assert _mock_branches.times_called == expected_branches_times_called
    assert _mock_jobs_start.times_called == expected_tp_times_called
