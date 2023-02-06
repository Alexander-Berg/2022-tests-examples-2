import tests_bank_idm.db_helpers as db_helpers


async def test_front_roles_by_user_login(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    request = {'user_login': user_login}

    response = await taxi_bank_idm.post('v1/front/v1/roles', json=request)
    assert response.status_code == 200
    roles = response.json()['roles']
    assert len(roles) == 1
    role = roles[0]
    assert role['role_id'] == 3
    assert role['role_name'] == 'Slug Path'
    assert role['role_status'] == 'granted'
    assert role['slug_path'] == 'test/slug_path'
    assert role['system_name'] == 'TEST SYSTEM'
    assert role['system_slug'] == 'test_slug'
    assert role['receiver_login'] == user_login
    assert role['requester_login'] == user_login


async def test_front_roles_by_system_slug(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    request = {'system_slug': 'test_slug'}

    response = await taxi_bank_idm.post('v1/front/v1/roles', json=request)
    assert response.status_code == 200
    roles = response.json()['roles']
    assert len(roles) == 1
    role = roles[0]
    assert role['role_id'] == 3
    assert role['role_name'] == 'Slug Path'
    assert role['role_status'] == 'granted'
    assert role['slug_path'] == 'test/slug_path'
    assert role['system_name'] == 'TEST SYSTEM'
    assert role['system_slug'] == 'test_slug'


async def test_front_roles_by_user_login_and_system_slug(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    request = {'system_slug': 'test_slug', 'user_login': user_login}

    response = await taxi_bank_idm.post('v1/front/v1/roles', json=request)
    assert response.status_code == 200
    roles = response.json()['roles']
    assert len(roles) == 1
    role = roles[0]
    assert role['role_id'] == 3


async def test_front_roles_few_roles_by_user_login(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    request = {'user_login': user_login}

    rolenode_id_2 = db_helpers.add_role_nodes(
        pgsql, 'another/role/node', 'Yet another rolenode', 1,
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id_2)
    response = await taxi_bank_idm.post('v1/front/v1/roles', json=request)
    assert response.status_code == 200
    roles = response.json()['roles']
    assert len(roles) == 2


async def test_front_roles_no_roles(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {'user_login': user_login}

    response = await taxi_bank_idm.post('v1/front/v1/roles', json=request)
    assert response.status_code == 200
    assert not response.json()['roles']


async def test_front_roles_system_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/roles', json={'system_slug': 'not_existed_system'},
    )
    assert response.status_code == 404


async def test_front_roles_user_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/roles', json={'user_login': 'not_existed_user'},
    )
    assert response.status_code == 404


async def test_front_roles_no_body_args(taxi_bank_idm):
    response = await taxi_bank_idm.post('v1/front/v1/roles', json={})
    assert response.status_code == 400


async def test_front_roles_path(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id)

    response = await taxi_bank_idm.post(
        f'v1/front/v1/roles/{role_id}', json={},
    )
    assert response.status_code == 200
    role = response.json()['role']
    assert role['role_id'] == 3
    assert role['role_name'] == 'Slug Path'
    assert role['role_status'] == 'granted'
    assert role['slug_path'] == 'test/slug_path'
    assert role['system_name'] == 'TEST SYSTEM'
    assert role['system_slug'] == 'test_slug'


async def test_front_roles_path_role_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(f'v1/front/v1/roles/100500', json={})
    assert response.status_code == 404
