import tests_bank_idm.db_helpers as db_helpers


async def test_deprive_role(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    responsible_user = 'responsible'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, responsible_user=responsible_user,
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    response = await taxi_bank_idm.post(
        'v1/deprive-role',
        json={'role_id': role_id, 'user_login': responsible_user},
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status, version from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'deprived'
    assert role[1] == 1  # new version


async def test_deprive_role_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    response = await taxi_bank_idm.post(
        'v1/deprive-role', json={'role_id': 100500, 'user_login': user_login},
    )
    assert response.status_code == 404


async def test_deprive_role_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'test_user_without_permissions'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    response = await taxi_bank_idm.post(
        'v1/deprive-role', json={'role_id': role_id, 'user_login': user_login},
    )
    assert response.status_code == 403


async def test_deprive_role_already_deprived(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    responsible_user = 'responsible'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, responsible_user=responsible_user,
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'deprived')
    response = await taxi_bank_idm.post(
        'v1/deprive-role',
        json={'role_id': role_id, 'user_login': responsible_user},
    )
    assert response.status_code == 409
