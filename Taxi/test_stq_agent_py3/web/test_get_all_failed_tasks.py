import pytest


@pytest.mark.parametrize(
    'path, expected',
    [
        (
            '/tasks/get_failed?queue_name=test_queue'
            '&from=2021-11-02T12:00:00&to=2022-02-02T14:00:00',
            {
                'failed_tasks': [
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 4,
                        'first_fail_time': '2021-12-02T09:58:20+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id1',
                    },
                    {
                        'task_id': 'task_id4',
                        'first_fail_time': '2021-12-02T10:00:00+00:00',
                        'failures_count': 4,
                        'args': '[1, 2, 3]',
                        'kwargs': '{"v": {"c": 1}}',
                    },
                    {
                        'task_id': 'task_id5',
                        'first_fail_time': '2021-12-02T10:00:02+00:00',
                        'failures_count': 5,
                        'args': '[1, 2, 3]',
                        'kwargs': '{"v": {"c": 1}}',
                    },
                ],
                'limit_reached': False,
            },
        ),
        (
            '/tasks/get_failed?queue_name=test_queue'
            '&from=2021-12-02T14:00:00',
            {
                'failed_tasks': [
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 5,
                        'first_fail_time': '2025-02-01T19:45:00+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id2',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 6,
                        'first_fail_time': '2025-02-01T19:47:12+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id6',
                    },
                ],
                'limit_reached': False,
            },
        ),
        (
            '/tasks/get_failed?queue_name=test_queue',
            {
                'failed_tasks': [
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 4,
                        'first_fail_time': '2021-12-02T09:58:20+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id1',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 5,
                        'first_fail_time': '2025-02-01T19:45:00+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id2',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 4,
                        'first_fail_time': '2021-12-02T10:00:00+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id4',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 5,
                        'first_fail_time': '2021-12-02T10:00:02+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id5',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 6,
                        'first_fail_time': '2025-02-01T19:47:12+00:00',
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id6',
                    },
                    {
                        'args': '[1, 2, 3]',
                        'failures_count': 5,
                        'kwargs': '{"v": {"c": 1}}',
                        'task_id': 'task_id7',
                    },
                ],
                'limit_reached': False,
            },
        ),
    ],
)
@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_get_failed_task_200(
        web_app_client, path, expected, cron_runner,
):
    await cron_runner.create_stq_indexes()
    response = await web_app_client.get(path)

    assert response.status == 200, await response.text()
    content = await response.json()
    assert content == expected


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_get_failed_task_limit_exceed_200(monkeypatch, web_app_client):
    monkeypatch.setattr(
        'stq_agent_py3.api.get_failed_tasks.MAX_DOCUMENT_COUNT', 3,
    )

    response = await web_app_client.get(
        '/tasks/get_failed?queue_name=test_queue'
        '&from=2021-11-02T12:00:00&to=2022-02-02T14:00:00',
    )

    assert response.status == 200, await response.text()
    content = await response.json()
    assert len(content['failed_tasks']) == 3
    assert content['limit_reached'] is True


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_get_failed_400(monkeypatch, web_app_client, cron_runner):
    await cron_runner.create_stq_indexes()
    response = await web_app_client.get(
        '/tasks/get_failed?queue_name=test_queue'
        '&from=2021-11-03T12:00:00&to=2020-02-02T14:00:00',
    )

    assert response.status == 400
    assert (await response.json())['code'] == 'invalid-interval'
    assert (await response.json())[
        'message'
    ] == '"To" time should be earlier than "from" time'


@pytest.mark.parametrize(
    'queue, namespace', [('with_tplatform', 'lavka'), ('test_queue', None)],
)
async def test_get_failed_with_tplatform(web_app_client, queue, namespace):
    response = await web_app_client.get(
        '/tasks/get_failed?queue_name='
        + queue
        + '&from=2021-11-02T12:00:00&to=2022-02-02T14:00:00',
    )
    assert response.status == 200
    assert (await response.json()).get('tplatform_namespace') == namespace
