import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_capabilities(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']

    for user_id in permitted_user_ids:
        response = await web_app_client.get(
            f'/v1/capabilities?user_id={user_id}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['capabilities']) == 5


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_post_capabilities(web_app_client):
    forbidden_user_ids = [34, 35, '000000']
    permitted_user_id = '007'

    test_slug = 'test_capability'

    for user_id in forbidden_user_ids:
        response = await web_app_client.post(
            f'/v1/capabilities?user_id={user_id}', json={'slug': test_slug},
        )
        assert response.status == 403

    response = await web_app_client.post(
        f'/v1/capabilities?user_id={permitted_user_id}',
        json={'slug': test_slug},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['slug'] == test_slug

    response = await web_app_client.get(
        f'/v1/capabilities?user_id={permitted_user_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['capabilities']) == 6

    response = await web_app_client.post(
        f'/v1/capabilities?user_id={permitted_user_id}',
        json={'slug': test_slug},
    )
    assert response.status == 400


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_project_capabilities(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']
    for user_id in permitted_user_ids:
        response = await web_app_client.get(
            f'/v1/capabilities/project?user_id={user_id}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['capabilities']) == 4


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_post_project_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'test_capability'
    project_slug = 'ya_market'
    capability_type = 'allowed'
    invalid_type = 'invalid'

    await web_app_client.post(
        f'/v1/capabilities' f'?user_id={permitted_user_id}',
        json={'slug': capability_slug},
    )

    for user_id in forbidden_user_ids:
        response = await web_app_client.post(
            f'/v1/capabilities/project' f'?user_id={user_id}',
            json={
                'capability_slug': capability_slug,
                'project_slug': project_slug,
                'type': capability_type,
            },
        )
        assert response.status == 403

    response = await web_app_client.post(
        f'/v1/capabilities/project?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'project_slug': project_slug,
            'type': invalid_type,
        },
    )
    assert response.status == 400

    response = await web_app_client.post(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'project_slug': project_slug,
            'type': capability_type,
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'project_slug': project_slug,
        'type': capability_type,
    }

    response = await web_app_client.get(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['capabilities']) == 5

    response = await web_app_client.post(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
        json={'capability_slug': capability_slug, 'type': capability_type},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'type': capability_type,
    }

    response = await web_app_client.get(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['capabilities']) == 6

    response = await web_app_client.post(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
        json={'capability_slug': capability_slug, 'type': capability_type},
    )
    assert response.status == 400


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_project_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    common_capability_slug = 'topics'
    common_capability_new_type = 'blocked'

    project_capability_slug = 'features'
    project_slug = 'ya_market'
    project_capability_new_type = 'allowed'

    invalid_type = 'invalid'

    for user_id in forbidden_user_ids:
        response = await web_app_client.put(
            f'/v1/capabilities/project'
            f'?capability_slug={common_capability_slug}'
            f'&user_id={user_id}',
            json={'type': common_capability_new_type},
        )
        assert response.status == 403

    response = await web_app_client.put(
        f'/v1/capabilities/project'
        f'?capability_slug={common_capability_slug}'
        f'&user_id={permitted_user_id}',
        json={'type': invalid_type},
    )
    assert response.status == 400

    response = await web_app_client.put(
        f'/v1/capabilities/project'
        f'?capability_slug={common_capability_slug}'
        f'&user_id={permitted_user_id}',
        json={'type': common_capability_new_type},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'capability_slug': common_capability_slug,
        'type': common_capability_new_type,
    }

    response = await web_app_client.put(
        f'/v1/capabilities/project'
        f'?capability_slug={project_capability_slug}'
        f'&project_slug={project_slug}'
        f'&user_id={permitted_user_id}',
        json={'type': invalid_type},
    )
    assert response.status == 400

    response = await web_app_client.put(
        f'/v1/capabilities/project'
        f'?capability_slug={project_capability_slug}'
        f'&project_slug={project_slug}'
        f'&user_id={permitted_user_id}',
        json={'type': project_capability_new_type},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'capability_slug': project_capability_slug,
        'project_slug': project_slug,
        'type': project_capability_new_type,
        'project_title': 'Маркет',
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_delete_project_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    common_capability_slug = 'topics'

    project_capability_slug = 'features'
    project_slug = 'ya_market'

    for user_id in forbidden_user_ids:
        response = await web_app_client.delete(
            f'/v1/capabilities/project'
            f'?capability_slug={common_capability_slug}'
            f'&user_id={user_id}',
        )
        assert response.status == 403

    response = await web_app_client.delete(
        f'/v1/capabilities/project'
        f'?capability_slug={common_capability_slug}'
        f'&user_id={permitted_user_id}',
    )
    assert response.status == 204

    response = await web_app_client.delete(
        f'/v1/capabilities/project'
        f'?capability_slug={project_capability_slug}'
        f'&project_slug={project_slug}'
        f'&user_id={permitted_user_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/capabilities/project' f'?user_id={permitted_user_id}',
    )
    response_json = await response.json()
    assert len(response_json['capabilities']) == 2


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_user_capabilities(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']
    for user_id in permitted_user_ids:
        response = await web_app_client.get(
            f'/v1/capabilities/user' f'?user_id={user_id}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['capabilities']) == 1


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_post_user_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'features'
    capability_user_id = 1
    capability_type = 'allowed'
    invalid_type = 'invalid'

    for user_id in forbidden_user_ids:
        response = await web_app_client.post(
            f'/v1/capabilities/user?user_id={user_id}',
            json={
                'capability_slug': capability_slug,
                'user_id': capability_user_id,
                'type': capability_type,
            },
        )
        assert response.status == 403

    response = await web_app_client.post(
        f'/v1/capabilities/user?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'user_id': capability_user_id,
            'type': invalid_type,
        },
    )
    assert response.status == 400

    response = await web_app_client.post(
        f'/v1/capabilities/user?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'user_id': capability_user_id,
            'type': capability_type,
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'user_id': capability_user_id,
        'type': capability_type,
    }

    response = await web_app_client.get(
        f'/v1/capabilities/user?user_id={permitted_user_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['capabilities']) == 2


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_user_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'user_based'
    capability_user_id = 1
    new_type = 'blocked'
    invalid_type = 'invalid'

    for user_id in forbidden_user_ids:
        response = await web_app_client.put(
            f'/v1/capabilities/user'
            f'?capability_slug={capability_slug}'
            f'&capability_user_id={capability_user_id}'
            f'&user_id={user_id}',
            json={'type': new_type},
        )
        assert response.status == 403

    response = await web_app_client.put(
        f'/v1/capabilities/user'
        f'?capability_slug={capability_slug}'
        f'&capability_user_id={capability_user_id}'
        f'&user_id={permitted_user_id}',
        json={'type': invalid_type},
    )
    assert response.status == 400

    response = await web_app_client.put(
        f'/v1/capabilities/user'
        f'?capability_slug={capability_slug}'
        f'&capability_user_id={capability_user_id}'
        f'&user_id={permitted_user_id}',
        json={'type': new_type},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'user_id': capability_user_id,
        'type': new_type,
        'login': 'ya_user_1',
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_delete_user_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'user_based'
    capability_user_id = 1

    for user_id in forbidden_user_ids:
        response = await web_app_client.delete(
            f'/v1/capabilities/user'
            f'?capability_slug={capability_slug}'
            f'&capability_user_id={capability_user_id}'
            f'&user_id={user_id}',
        )
        assert response.status == 403

    response = await web_app_client.delete(
        f'/v1/capabilities/user'
        f'?capability_slug={capability_slug}'
        f'&capability_user_id={capability_user_id}'
        f'&user_id={permitted_user_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/capabilities/user?user_id={permitted_user_id}',
    )
    response_json = await response.json()
    assert not response_json['capabilities']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_role_capabilities(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']
    for user_id in permitted_user_ids:
        response = await web_app_client.get(
            f'/v1/capabilities/role' f'?user_id={user_id}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['capabilities']) == 2


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_post_role_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'features'
    role_id = 1
    capability_type = 'allowed'
    invalid_type = 'invalid'

    for user_id in forbidden_user_ids:
        response = await web_app_client.post(
            f'/v1/capabilities/role' f'?user_id={user_id}',
            json={
                'capability_slug': capability_slug,
                'role_id': role_id,
                'type': capability_type,
            },
        )
        assert response.status == 403

    response = await web_app_client.post(
        f'/v1/capabilities/role' f'?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'role_id': role_id,
            'type': invalid_type,
        },
    )
    assert response.status == 400

    response = await web_app_client.post(
        f'/v1/capabilities/role' f'?user_id={permitted_user_id}',
        json={
            'capability_slug': capability_slug,
            'role_id': role_id,
            'type': capability_type,
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'role_id': role_id,
        'type': capability_type,
    }

    response = await web_app_client.get(
        f'/v1/capabilities/role?user_id={permitted_user_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['capabilities']) == 3


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_role_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'user_based'
    role_id = 3
    new_type = 'blocked'
    invalid_type = 'invalid'

    for user_id in forbidden_user_ids:
        response = await web_app_client.put(
            f'/v1/capabilities/role'
            f'?capability_slug={capability_slug}'
            f'&role_id={role_id}'
            f'&user_id={user_id}',
            json={'type': new_type},
        )
        assert response.status == 403

    response = await web_app_client.put(
        f'/v1/capabilities/role'
        f'?capability_slug={capability_slug}'
        f'&role_id={role_id}'
        f'&user_id={permitted_user_id}',
        json={'type': invalid_type},
    )
    assert response.status == 400

    response = await web_app_client.put(
        f'/v1/capabilities/role'
        f'?capability_slug={capability_slug}'
        f'&role_id={role_id}'
        f'&user_id={permitted_user_id}',
        json={'type': new_type},
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json == {
        'capability_slug': capability_slug,
        'role_id': role_id,
        'type': new_type,
        'role_title': 'Project Editor',
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_delete_role_capabilities(web_app_client):
    forbidden_user_ids = [34, 45, '000000']
    permitted_user_id = '007'

    capability_slug = 'user_based'
    role_id = 3

    for user_id in forbidden_user_ids:
        response = await web_app_client.delete(
            f'/v1/capabilities/role'
            f'?capability_slug={capability_slug}'
            f'&role_id={role_id}'
            f'&user_id={user_id}',
        )
        assert response.status == 403

    response = await web_app_client.delete(
        f'/v1/capabilities/role'
        f'?capability_slug={capability_slug}'
        f'&role_id={role_id}'
        f'&user_id={permitted_user_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/capabilities/role' f'?user_id={permitted_user_id}',
    )
    response_json = await response.json()
    assert len(response_json['capabilities']) == 1


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_project_capabilities_for_user(web_app_client):
    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=1',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_market',
                'capabilities': ['user_based', 'topics'],
            },
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['user_based', 'demo', 'features', 'topics'],
            },
            {
                'project_slug': 'ya_useless',
                'capabilities': ['user_based', 'features', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=1'
        '&project_slug=ya_market',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_market',
                'capabilities': ['user_based', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=1'
        '&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['user_based', 'demo', 'features', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=1'
        '&project_slug=ya_useless',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_useless',
                'capabilities': ['user_based', 'features', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=2',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_market',
                'capabilities': ['topics', 'user_based'],
            },
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['demo', 'features', 'topics'],
            },
            {
                'project_slug': 'ya_useless',
                'capabilities': ['features', 'topics', 'user_based'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=2'
        '&project_slug=ya_market',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_market',
                'capabilities': ['topics', 'user_based'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=2'
        '&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['demo', 'features', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=2'
        '&project_slug=ya_useless',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_useless',
                'capabilities': ['features', 'topics', 'user_based'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=3',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {'project_slug': 'ya_market', 'capabilities': ['topics']},
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['demo', 'features', 'topics'],
            },
            {
                'project_slug': 'ya_useless',
                'capabilities': ['features', 'topics'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=4',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {
                'project_slug': 'ya_market',
                'capabilities': ['topics', 'su_user_based'],
            },
            {
                'project_slug': 'ya_lavka',
                'capabilities': [
                    'demo',
                    'features',
                    'topics',
                    'su_user_based',
                ],
            },
            {
                'project_slug': 'ya_useless',
                'capabilities': ['features', 'topics', 'su_user_based'],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/capabilities/project/for-user'
        '?user_id=007'
        '&capability_user_id=5',
    )
    assert response.status == 200
    assert (await response.json()) == {
        'project_capabilities': [
            {'project_slug': 'ya_market', 'capabilities': ['topics']},
            {
                'project_slug': 'ya_lavka',
                'capabilities': ['demo', 'features', 'topics'],
            },
            {
                'project_slug': 'ya_useless',
                'capabilities': ['features', 'topics'],
            },
        ],
    }
