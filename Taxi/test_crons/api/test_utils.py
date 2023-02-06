# pylint: disable=redefined-outer-name
import datetime

import pytest

NOW = datetime.datetime(2020, 5, 6, 12)


@pytest.fixture
def create_task(web_app_client):
    async def do_it(status, run_id):
        response = await web_app_client.post(
            '/v1/task/crons-crontasks-test/start/',
            json={
                'task_run_id': run_id,
                'hostname': 'test.dev',
                'start_time': '2020-05-06T11:55:00.0Z',
            },
        )
        assert response.status == 200
        response = await web_app_client.post(
            '/v1/task/crons-crontasks-test/finish/',
            json={
                'task_run_id': run_id,
                'status': status,
                'start_time': '2020-05-06T11:55:00.0Z',
                'end_time': '2020-05-06T11:56:00.0Z',
                'execution_time': 10.0,
                'clock_time': 0.1,
            },
        )
        assert response.status == 200

    return do_it


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'task_name, expected',
    [
        pytest.param('non-existing', {'count': 0}, id='non-existing'),
        pytest.param('crons-crontasks-test', {'count': 1}, id='existing'),
    ],
)
async def test_get_success_tasks(
        web_app_client, create_task, task_name, expected,
):
    await create_task('finished', '1')
    await create_task('exception', '2')
    await create_task('in_progress', '3')

    response = await web_app_client.post(
        '/utils/v1/get-finished-tasks-count/',
        json={'period': 100500, 'task_name': task_name},
    )
    assert response.status == 200
    assert expected == (await response.json())
