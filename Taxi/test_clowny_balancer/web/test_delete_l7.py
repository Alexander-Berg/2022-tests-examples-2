async def test_start_delete_l7(
        taxi_clowny_balancer_web, mock_task_processor_start_job,
):
    task_processor_mock = mock_task_processor_start_job()
    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/start/delete/l7/',
        json={
            'awacs_namespace': 'some-service.taxi.yandex.net',
            'service_id': 1,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    assert (await response.json()) == {'job_id': 1}
    assert task_processor_mock.times_called == 1
