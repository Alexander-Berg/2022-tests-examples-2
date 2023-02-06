from crons.lib import http_status
from crons.lib import task


async def test_start(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/start/',
        json={
            'task_run_id': '123',
            'hostname': 'test.dev',
            'start_time': '2019-03-03T00:00:00.0Z',
        },
    )
    assert response.status == http_status.OK_HTTP_STATUS

    response = await web_app_client.post(
        '/v1/task/test/start/',
        json={
            'task_run_id': '123',
            'hostname': 'test.dev',
            'start_time': '2019-03-03T00:00:00.0Z',
        },
    )
    assert response.status == http_status.TASK_STATE_UPDATE_ERROR_HTTP_STATUS
    body = await response.json()
    assert body['code'] == task.TaskAlreadyStarted.code


async def test_finish(web_app_client):
    response = await web_app_client.post(
        '/v1/task/test/finish/',
        json={
            'task_run_id': '123',
            'status': 'in_progress',
            'start_time': '2019-03-03T00:00:00.0Z',
            'end_time': '2019-03-03T00:00:00.0Z',
            'execution_time': 10.0,
            'clock_time': 0.1,
        },
    )
    assert response.status == http_status.TASK_STATE_UPDATE_ERROR_HTTP_STATUS
    body = await response.json()
    assert body['code'] == task.TaskRunNotExists.code

    response = await web_app_client.post(
        '/v1/task/test/start/',
        json={
            'task_run_id': '123',
            'hostname': 'test.dev',
            'start_time': '2019-03-03T00:00:00.0Z',
        },
    )
    assert response.status == http_status.OK_HTTP_STATUS

    response = await web_app_client.post(
        '/v1/task/test/finish/',
        json={
            'task_run_id': '123',
            'status': 'in_progress',
            'start_time': '2019-03-03T00:00:00.0Z',
            'end_time': '2019-03-03T00:00:00.0Z',
            'execution_time': 10.0,
            'clock_time': 0.1,
        },
    )
    assert response.status == http_status.OK_HTTP_STATUS
