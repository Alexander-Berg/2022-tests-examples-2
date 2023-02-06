import pytest


@pytest.mark.pgsql('clowny_balancer', files=['init.sql'])
@pytest.mark.parametrize(
    'service_id, branch_id, env, dns_name, status, job_id, times_called',
    [
        (1, 1, 'stable', 'fqdn.net', 400, None, 0),
        (1, 3, 'testing', 'fqdn.test.net', 400, None, 0),
        (2, 1, 'unstable', 'fqdn.unstable.net', 200, 1, 1),
    ],
)
async def test_start_create(
        taxi_clowny_balancer_web,
        mock_task_processor_start_job,
        service_id,
        branch_id,
        env,
        dns_name,
        status,
        job_id,
        times_called,
):
    task_processor_mock = mock_task_processor_start_job()
    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/start/create/',
        json={
            'fqdn': dns_name,
            'branches': [
                {
                    'project_id': 1,
                    'service_id': service_id,
                    'id': branch_id,
                    'full_name': 'taxi_some-service_testing',
                    'env': env,
                },
            ],
            'size': 1,
            'datacenters': ['MAN'],
            'ticket': 'TAXIPLATFORM-1',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == status
    if status == 200:
        assert (await response.json())['job_id'] == job_id
    assert task_processor_mock.times_called == times_called
