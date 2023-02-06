async def test_start_apply_monitoring(
        taxi_clowny_balancer_web, mock_task_processor_start_job,
):
    task_processor_mock = mock_task_processor_start_job()
    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/start/apply-monitoring/',
        json={
            'fqdn': 'some-service.taxi.yandex.net',
            'branches': [
                {
                    'project_id': 1,
                    'service_id': 1,
                    'id': 1,
                    'full_name': 'taxi_some-service_unstable',
                    'env': 'unstable',
                },
            ],
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    assert (await response.json()) == {'job_id': 1}
    assert task_processor_mock.times_called == 1
