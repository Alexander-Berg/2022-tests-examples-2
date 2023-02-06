import pytest


@pytest.mark.parametrize('use_drafts', [True, False])
@pytest.mark.parametrize(
    'data, expected_status, expected_result',
    [
        pytest.param({'entry_point_id': 1}, 200, {'job_id': 1}),
        pytest.param(
            {'entry_point_id': 10},
            404,
            {'message': 'Entry point 10 not found', 'code': 'NOT_FOUND'},
        ),
    ],
)
async def test_add_ssl(
        mock_task_processor_start_job,
        mock_get_branch,
        mock_get_service,
        mock_get_project,
        taxi_clowny_balancer_web,
        use_drafts,
        data,
        expected_status,
        expected_result,
):
    mock_task_processor_start_job()
    mock_get_branch()
    mock_get_service()
    mock_get_project(project_name='project')

    if not use_drafts:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/add-ssl/',
            json=data,
            headers={'X-Yandex-Login': 'd1mbas'},
        )
        assert response.status == expected_status, await response.text()
        assert await response.json() == expected_result
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/add-ssl/check/',
        json=data,
        headers={'X-Yandex-Login': 'd1mbas'},
    )

    assert response.status == expected_status, await response.text()
    if response.status != 200:
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/add-ssl/apply/',
        json=(await response.json())['data'],
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_result


@pytest.mark.config(
    CLOWNDUCTOR_PROJECT_QUEUES={
        '__default__': {'components': [123], 'queue': 'TAXIADMIN'},
        'eda_project': {'queue': 'EDAOPS'},
    },
)
@pytest.mark.parametrize(
    'project_name, expected_queue, expected_components',
    [
        pytest.param(
            'taxi_project',
            'TAXIADMIN',
            [123],
            id='create ticket in the default queue',
        ),
        pytest.param(
            'eda_project',
            'EDAOPS',
            None,
            id='create ticket in a queue from config',
        ),
        pytest.param(
            'lavka_project',
            'TAXIADMIN',
            None,
            id='ticket creation in case when config is empty',
            marks=[pytest.mark.config(CLOWNDUCTOR_PROJECT_QUEUES={})],
        ),
    ],
)
async def test_add_ssl_ticket_queue(
        mock_get_branch,
        mock_get_service,
        mock_get_project,
        mock_task_processor_start_job,
        taxi_clowny_balancer_web,
        project_name,
        expected_queue,
        expected_components,
):
    mock_task_processor_start_job()
    mock_get_branch()
    mock_get_service()
    mock_get_project(project_name=project_name)

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/add-ssl/check/',
        json={'entry_point_id': 1},
        headers={'X-Yandex-Login': 'd1mbas'},
    )

    response_text = await response.json()
    ticket_create_data = response_text['tickets']['create_data']
    assert ticket_create_data['ticket_queue'] == expected_queue
    assert ticket_create_data.get('components') == expected_components
