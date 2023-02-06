import json

import pytest


@pytest.mark.pgsql('personal_goals', files=['import_tasks.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected_status',
    [
        ('88db6b2edc064a3caf6d192846860227', 'completed'),
        ('df79575218014715ba078fe25b73c016', 'applying'),
    ],
)
async def test_commit_import_simple(
        taxi_personal_goals_web, import_task_id, expected_status,
):
    body = {'import_task_id': import_task_id}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/import/commit', data=json.dumps(body),
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['status'] == expected_status


@pytest.mark.pgsql('personal_goals', files=['import_tasks.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected_status, expected_errors',
    [('88db6b2edc064a3caf6d192846860288', 'partially_completed', 2)],
)
async def test_commit_import_partially_complete(
        taxi_personal_goals_web,
        import_task_id,
        expected_status,
        expected_errors,
):
    body = {'import_task_id': import_task_id}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/import/commit', data=json.dumps(body),
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['status'] == expected_status
    assert response_data['errors'] == [
        {
            'failed_count': 1,
            'message': 'Some goals out of 10 failed to import with: cause-a',
        },
        {
            'failed_count': expected_errors,
            'message': (
                '2 goals out of 10 failed to import with: cause-b: x, y'
            ),
        },
    ]


@pytest.mark.pgsql('personal_goals', files=['import_tasks.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected_status',
    [('fdedcdd557fe43c4bc00a394f23ac7e7', 'applying')],
)
async def test_commit_import_pending(
        taxi_personal_goals_web, stq, import_task_id, expected_status,
):
    body = {'import_task_id': import_task_id}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/import/commit', data=json.dumps(body),
    )
    assert response.status == 200
    assert stq.goals_importing.times_called == 1

    task_in_queue = stq.goals_importing.next_call()
    assert task_in_queue['id'] == import_task_id

    response_data = await response.json()
    assert response_data['status'] == expected_status


@pytest.mark.pgsql('personal_goals', files=['import_tasks.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected_status',
    [('dddddddddddddddddddddddddddddddd', 409)],
)
async def test_commit_import_errors(
        taxi_personal_goals_web, import_task_id, expected_status,
):
    body = {'import_task_id': import_task_id}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/import/commit', data=json.dumps(body),
    )
    assert response.status == expected_status
