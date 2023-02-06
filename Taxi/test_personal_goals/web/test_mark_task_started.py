import pytest


@pytest.mark.pgsql('personal_goals', files=['mark_task_started.sql'])
@pytest.mark.parametrize(
    'import_task_id, expected_status',
    [
        ('88db6b2edc064a3caf6d192846860288', 'completed'),
        ('df79575218014715ba078fe25b73c016', 'in_progress'),
        ('fdedcdd557fe43c4bc00a394f23ac7e7', 'in_progress'),
        ('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', None),
    ],
)
async def test_update_task_status(
        taxi_personal_goals_web, import_task_id, expected_status,
):
    query = {'import_task_id': import_task_id}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/import_tasks/mark_started', params=query,
    )
    assert response.status == 200

    if expected_status:
        control = await taxi_personal_goals_web.get(
            '/internal/admin/import_tasks', params=query,
        )
        control_data = await control.json()
        assert control_data['status'] == expected_status
