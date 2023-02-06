import pytest


async def test_v1_admin_projects_ok(
        taxi_eats_notifications, load_json, taxi_config,
):

    # add 2 projects
    response = await taxi_eats_notifications.post(
        '/v1/admin/project', json=load_json('project1.json'),
    )
    assert response.status_code == 204

    project2 = load_json('project2.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/project', json=project2,
    )
    assert response.status_code == 204

    # show all projects
    all_projects = load_json('all_projects.json')
    response = await taxi_eats_notifications.get(
        '/v1/admin/projects', params={'page_number': 1, 'page_size': 20},
    )
    assert response.status_code == 200
    assert response.json() == all_projects

    # delete one project
    response = await taxi_eats_notifications.delete(
        '/v1/admin/project', json={'id': 2},
    )
    assert response.status_code == 204
    del all_projects['projects'][1]

    # update project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project',
        json={
            'id': 1,
            'data': {'name': 'project1_upd', 'intent': 'intent_upd'},
        },
    )
    assert response.status_code == 204

    # show all projects
    response = await taxi_eats_notifications.get(
        '/v1/admin/projects', params={'page_number': 1, 'page_size': 20},
    )
    assert response.status_code == 200
    assert response.json() == load_json('projects_after_modifications.json')


async def test_v1_admin_check_create_project_200(
        taxi_eats_notifications, load_json, taxi_config,
):
    # try add project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project/check-create', json=load_json('project1.json'),
    )
    assert response.status_code == 200


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects('
        'name, key, tanker_project, tanker_keyset, intent)'
        'VALUES (\'project\', \'key_k\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_check_create_project_400(
        taxi_eats_notifications, load_json, taxi_config,
):
    # try add project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project/check-create', json=load_json('project1.json'),
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects('
        'name, key, tanker_project, tanker_keyset, intent)'
        'VALUES (\'project\', \'key_k\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_check_update_project_200(
        taxi_eats_notifications, load_json, taxi_config,
):

    # update project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project/check-update',
        json={'id': 1, 'data': {'key': 'project_UPD', 'intent': 'intent_upd'}},
    )
    assert response.status_code == 200
    assert response.json()['data'] == {
        'id': 1,
        'data': {'key': 'project_upd', 'intent': 'intent_upd'},
    }


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects('
        'name, key, tanker_project, tanker_keyset, intent)'
        'VALUES (\'project\', \'key_k\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_check_update_project_400(
        taxi_eats_notifications, load_json, taxi_config,
):

    # try update project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project/check-update', json={'id': 2, 'data': {}},
    )
    assert response.status_code == 400

    # try update project
    response = await taxi_eats_notifications.put(
        '/v1/admin/project/check-update',
        json={'id': 1, 'data': {'key': 'incorrect 0'}},
    )
    assert response.status_code == 400


async def test_v1_admin_project_create_conflict(
        taxi_eats_notifications, load_json,
):
    response = await taxi_eats_notifications.post(
        '/v1/admin/project', json=load_json('project1.json'),
    )
    assert response.status_code == 204

    response = await taxi_eats_notifications.post(
        '/v1/admin/project', json=load_json('project1.json'),
    )
    assert response.status_code == 409


async def test_v1_admin_project_update_not_found(taxi_eats_notifications):
    response = await taxi_eats_notifications.put(
        '/v1/admin/project', json={'id': 0, 'data': {'name': 'project1_upd'}},
    )
    assert response.status_code == 404


async def test_v1_admin_project_delete_not_found(taxi_eats_notifications):
    response = await taxi_eats_notifications.delete(
        '/v1/admin/project', json={'id': 0},
    )
    assert response.status_code == 404


async def test_v1_admin_projects_invalid_pagination(taxi_eats_notifications):
    response = await taxi_eats_notifications.get(
        '/v1/admin/projects', params={'page_number': 0, 'page_size': 20},
    )
    assert response.status_code == 400
