import tests_bank_idm.db_helpers as db_helpers


async def test_restore_role(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(pgsql, 'test/slug_path', 'Slug Path', system_id)

    response = await taxi_bank_idm.post(
        'v1/drop-role',
        json={
            'system_slug': system_slug,
            'user_login': user_login,
            'slug_path': 'test/slug_path',
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_idm.post(
        'v1/restore-role',
        json={
            'system_slug': system_slug,
            'user_login': user_login,
            'slug_path': 'test/slug_path',
        },
    )
    assert response.status_code == 200

    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select rolenode_status from bank_idm.role_nodes
        where system_id = {system_id} and slug_path = 'test/slug_path'
        """,
    )
    rolenode_status = cursor.fetchall()[0][0]
    assert rolenode_status == 'enabled'


async def test_restore_role_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    db_helpers.add_system(pgsql, system_slug, user_id)

    user_without_permission = 'user_without_permission'
    db_helpers.add_user(pgsql, user_without_permission, 'test@gmail.com')
    response = await taxi_bank_idm.post(
        'v1/restore-role',
        json={
            'system_slug': system_slug,
            'user_login': user_without_permission,
            'slug_path': 'test/slug_path',
        },
    )
    assert response.status_code == 403


async def test_restore_role_user_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    db_helpers.add_system(pgsql, system_slug, user_id)

    response = await taxi_bank_idm.post(
        'v1/restore-role',
        json={
            'system_slug': system_slug,
            'user_login': 'not_existed_user',
            'slug_path': 'test/slug_path',
        },
    )
    assert response.status_code == 404


async def test_restore_role_slugpath_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    db_helpers.add_system(pgsql, system_slug, user_id)

    response = await taxi_bank_idm.post(
        'v1/restore-role',
        json={
            'system_slug': system_slug,
            'user_login': user_login,
            'slug_path': 'test/not_existed_slug_path',
        },
    )
    assert response.status_code == 404
