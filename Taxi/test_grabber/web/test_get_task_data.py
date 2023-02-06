from grabber.generated.service.swagger.models import api


async def test_get_task_data(web_app_client, pgsql):
    response_for_fake_id = await web_app_client.get('/v1/tasks/sdas/data')
    assert response_for_fake_id.status == 404

    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.operations (operation_id, operation_type, operation_status)'  # noqa E501
        'VALUES (\'operation_id\', \'yql_query\', \'created\')',
    )

    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.operations_data (operation_id, json_data)'
        'VALUES (\'operation_id\', \'"{\\"x\\": 1}"\')',
    )

    driver_timeline_request = {
        'data_type': 'driver_timeline',
        'data_filter': {},
    }
    body = {
        'order_id': 'bf86862d4a2a50118be569e8ca683979',
        'data_requests': [driver_timeline_request],
    }
    create_task_response = await web_app_client.post(
        '/v1/tasks/', json=body, headers={'X-Yandex-Login': 'login'},
    )
    assert create_task_response.status == 200

    task_json = await create_task_response.json()
    task = api.Task.deserialize(task_json)

    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.data_requests (request_id, task_id, data_type, data_filter, operation_id)'  # noqa E501
        'VALUES (\'request_id\', \'%s\', \'data_type\',  \'"{\\"x\\": 1}"\',  \'operation_id\')'  # noqa E501
        % task.task_id,
    )
