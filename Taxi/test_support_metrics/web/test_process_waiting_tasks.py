import datetime

import pytest


async def _check_chatterbox_waiting_tasks(db, expected_result):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_tasks.waiting_tasks '
        'ORDER BY id, delivery_id',
    )
    assert len(result) == len(expected_result)
    for i, record in enumerate(result):
        assert record['id'] == expected_result[i]['id']
        assert record['login'] == expected_result[i]['login']
        assert record['line'] == expected_result[i]['line']
        assert record['status'] == expected_result[i]['status']
        assert record['waiting_time'] == expected_result[i]['waiting_time']
        assert record['updated_ts'] == expected_result[i]['updated_ts']


async def _check_waiting_tasks_deliveries(db, expected_timestamp):
    result = await db.primary_fetch(
        'SELECT * FROM chatterbox_deliveries.waiting_task_deliveries '
        'ORDER BY created_ts DESC',
    )
    assert result[0]['created_ts'] == expected_timestamp


@pytest.mark.parametrize(
    'data, expected_result, expected_timestamp',
    [
        (
            {'tasks': [], 'created_ts': '2021-10-02T19:17:56+0300'},
            [],
            datetime.datetime(
                2021, 10, 2, 16, 17, 56, tzinfo=datetime.timezone.utc,
            ),
        ),
        (
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'login': '',
                        'line': '',
                        'status': 'new',
                        'waiting_time': 60,
                        'updated_ts': '2021-10-02T19:18:10+0300',
                    },
                    {
                        'id': 'task_2',
                        'login': 'support_1',
                        'line': 'first',
                        'status': 'in_progress',
                        'waiting_time': 120,
                        'updated_ts': '2021-10-02T19:18:39+0300',
                    },
                ],
                'created_ts': '2021-10-02T19:17:56+0300',
            },
            [
                {
                    'id': 'task_1',
                    'login': '',
                    'line': '',
                    'status': 'new',
                    'waiting_time': 60,
                    'updated_ts': datetime.datetime(
                        2021, 10, 2, 16, 18, 10, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'id': 'task_2',
                    'login': 'support_1',
                    'line': 'first',
                    'status': 'in_progress',
                    'waiting_time': 120,
                    'updated_ts': datetime.datetime(
                        2021, 10, 2, 16, 18, 39, tzinfo=datetime.timezone.utc,
                    ),
                },
            ],
            datetime.datetime(
                2021, 10, 2, 16, 17, 56, tzinfo=datetime.timezone.utc,
            ),
        ),
        pytest.param(
            {
                'tasks': [
                    {
                        'id': 'task_3',
                        'login': 'support_2',
                        'line': 'second',
                        'status': 'accepted',
                        'waiting_time': 70,
                        'updated_ts': '2021-10-02T19:19:06+0300',
                    },
                ],
                'created_ts': '2021-10-02T19:17:56+0300',
            },
            [
                {
                    'id': 'task_1',
                    'login': '',
                    'line': '',
                    'status': 'new',
                    'waiting_time': 60,
                    'updated_ts': datetime.datetime(
                        2021, 10, 2, 16, 18, 10, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'id': 'task_2',
                    'login': 'support_1',
                    'line': 'first',
                    'status': 'in_progress',
                    'waiting_time': 120,
                    'updated_ts': datetime.datetime(
                        2021, 10, 2, 16, 18, 39, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'id': 'task_3',
                    'login': 'support_2',
                    'line': 'second',
                    'status': 'accepted',
                    'waiting_time': 70,
                    'updated_ts': datetime.datetime(
                        2021, 10, 2, 16, 19, 6, tzinfo=datetime.timezone.utc,
                    ),
                },
            ],
            datetime.datetime(
                2021, 10, 2, 16, 17, 56, tzinfo=datetime.timezone.utc,
            ),
            marks=pytest.mark.pgsql(
                'support_metrics', files=['pg_support_metrics_replace.sql'],
            ),
        ),
    ],
)
async def test_bulk(
        web_app_client, web_context, data, expected_result, expected_timestamp,
):
    response = await web_app_client.post(
        '/v1/bulk_process_waiting_tasks', json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    db = web_context.postgresql.support_metrics[0]
    await _check_chatterbox_waiting_tasks(db, expected_result)
    await _check_waiting_tasks_deliveries(db, expected_timestamp)
