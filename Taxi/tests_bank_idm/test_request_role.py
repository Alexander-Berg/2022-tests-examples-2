import tests_bank_idm.db_helpers as db_helpers


async def test_request_role(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id,
    )

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
        },
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status, comment, deprive_after_days from bank_idm.roles
        where rolenode_id = {rolenode_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'requested'
    assert role[1] is None
    assert role[2] is None


async def test_request_role_with_comment_and_ttl(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id,
    )

    comment = 'Test Comment'
    deprive_after_days = 100500
    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
            'comment': comment,
            'deprive_after_days': deprive_after_days,
        },
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status, comment, deprive_after_days from bank_idm.roles
        where rolenode_id = {rolenode_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'requested'
    assert role[1] == comment
    assert role[2] == deprive_after_days


async def test_request_role_user_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(pgsql, slug_path, 'Slug Path', system_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': 'not_existed_user',
            'requested_from': user_login,
        },
    )
    assert response.status_code == 404


async def test_drop_role_requested_user_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(pgsql, slug_path, 'Slug Path', system_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': 'not_existed_user',
        },
    )
    assert response.status_code == 404


async def test_request_role_rolenode_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(pgsql, slug_path, 'Slug Path', system_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': 'not/existed/slug',
            'user_login': user_login,
            'requested_from': user_login,
        },
    )
    assert response.status_code == 404


async def test_request_role_requested_system_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    db_helpers.add_role_nodes(pgsql, slug_path, 'Slug Path', system_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': 'not_existed_system',
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
        },
    )
    assert response.status_code == 404


async def test_request_role_already_granted(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id,
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
        },
    )
    assert response.status_code == 409


async def test_request_role_after_depriving(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id,
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id, role_status='deprived')

    new_comment = 'new comment'
    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
            'comment': new_comment,
            'deprive_after_days': 5,
        },
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
            select role_status, requested_from, comment, deprive_after_days
            from bank_idm.roles where rolenode_id = {rolenode_id}
            """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'requested'
    assert role[1] == user_id
    assert role[2] == new_comment
    assert role[3] == 5


async def test_request_role_system_disabled(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    slug_path = 'test/slug_path'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id, 'disabled')
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id,
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id)

    response = await taxi_bank_idm.post(
        'v1/request-role',
        json={
            'system_slug': system_slug,
            'slug_path': slug_path,
            'user_login': user_login,
            'requested_from': user_login,
        },
    )
    assert response.status_code == 400
