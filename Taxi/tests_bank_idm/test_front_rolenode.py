import tests_bank_idm.db_helpers as db_helpers


async def test_front_rolenode(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    db_helpers.prepare_test_data(pgsql, user_login, approvers=[['test_user']])
    request = {'system_slug': system_slug, 'slug_path': slug_path}
    response = await taxi_bank_idm.post('v1/front/v1/rolenode', json=request)
    assert response.status_code == 200
    rolenode = response.json()['rolenode']
    assert rolenode['system_slug'] == system_slug
    assert rolenode['role_name'] == 'Slug Path'
    assert rolenode['slug_path'] == slug_path
    assert rolenode['is_leaf']
    assert rolenode['rolenode_status'] == 'enabled'
    assert rolenode['approvers'] == {'logins': [['test_user']]}
    assert rolenode['created_at']
    assert rolenode['updated_at']


async def test_front_rolenode_is_leaf_false(taxi_bank_idm, pgsql):
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, 'test_user', 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id, is_leaf=False,
    )

    request = {'system_slug': system_slug, 'slug_path': slug_path}
    response = await taxi_bank_idm.post('v1/front/v1/rolenode', json=request)
    assert response.status_code == 200
    rolenode = response.json()['rolenode']
    assert rolenode['system_slug'] == system_slug
    assert rolenode['role_name'] == 'Slug Path'
    assert rolenode['slug_path'] == slug_path
    assert not rolenode['is_leaf']
    assert rolenode['rolenode_status'] == 'enabled'
    assert rolenode['approvers'] == {'logins': []}


async def test_front_rolenode_system_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    slug_path = 'test/slug_path'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {'system_slug': 'not_existed_system', 'slug_path': slug_path}
    response = await taxi_bank_idm.post('v1/front/v1/rolenode', json=request)
    assert response.status_code == 404


async def test_front_rolenode_slug_path_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {
        'system_slug': system_slug,
        'slug_path': 'not_existed_slug_path',
    }
    response = await taxi_bank_idm.post('v1/front/v1/rolenode', json=request)
    assert response.status_code == 404
