import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset) '
        'VALUES (\'name\', \'key\', \'tanker_project\', \'tanker_keyset\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset) '
        'VALUES (\'name\', \'key2\', \'tanker_project\', \'tanker_keyset\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'eda_android\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'eda_ios\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'magnit_android\')',
    ],
)
@pytest.mark.parametrize(
    'project_id, applications, expected_response',
    [
        pytest.param(
            1,
            [
                {'application': 'eda_android', 'operation': 'add'},
                {'application': 'eda_ios', 'operation': 'add'},
                {'application': 'magnit_android', 'operation': 'add'},
            ],
            ['eda_android', 'eda_ios', 'magnit_android'],
            id='add multiple applications',
        ),
        pytest.param(
            2,
            [{'application': 'eda_ios', 'operation': 'delete'}],
            ['eda_android', 'magnit_android'],
            id='delete application',
        ),
    ],
)
async def test_204(
        pgsql,
        taxi_eats_notifications,
        taxi_config,
        project_id,
        applications,
        expected_response,
):
    response = await taxi_eats_notifications.put(
        '/v1/admin/applications',
        {'applications': applications, 'id': project_id},
    )

    assert response.status_code == 204

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT app_key '
        'FROM eats_notifications.project2app '
        f'WHERE project_id = {project_id}',
    )
    assert list(row[0] for row in cursor) == expected_response


async def test_404(taxi_eats_notifications, taxi_config):
    response = await taxi_eats_notifications.put(
        '/v1/admin/applications', {'applications': [], 'id': 1},
    )
    assert response.status_code == 404
