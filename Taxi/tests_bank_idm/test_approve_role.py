import pytest

import tests_bank_idm.db_helpers as db_helpers


async def test_approve_role(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'granted'
    assert response.json() == {'granted': True}


async def test_approve_role_approver_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': 100500, 'approver_login': user_login},
    )
    assert response.status_code == 404


async def test_approve_role_system_disabled(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, system_status='disabled', approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


async def test_approve_role_rolenode_disabled(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql,
        user_login,
        rolenode_status='disabled',
        approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('role_status', ['deprived', 'granted'])
async def test_approve_role_bad_role_status(taxi_bank_idm, pgsql, role_status):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, role_status)

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


async def test_approve_role_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'test_user_without_permissions'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 403


async def test_approve_role_already_approved(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    db_helpers.add_approve(pgsql, role_id, user_id)

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 409


async def test_approve_role_responsible_fallback(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    responsible_user = 'responsible'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, responsible_user=responsible_user,
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': responsible_user},
    )
    assert response.status_code == 200
    assert response.json() == {'granted': True}


async def test_approve_role_not_enough_approvers(taxi_bank_idm, pgsql):
    approver1 = 'test_user1'
    approver2 = 'test_user2'
    approver_id1, rolenode_id = db_helpers.prepare_test_data(
        pgsql, approver1, approvers=[[approver1, approver2], [approver2]],
    )
    db_helpers.add_user(pgsql, approver2, 'test@gmail.com')
    role_id = db_helpers.add_role(
        pgsql, approver_id1, rolenode_id, 'requested',
    )

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': approver1},
    )
    assert response.status_code == 200
    assert response.json() == {'granted': False}
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'requested'


async def test_approve_role_get_last_approve(taxi_bank_idm, pgsql):
    approver1 = 'test_user1'
    approver2 = 'test_user2'
    approver_id1, rolenode_id = db_helpers.prepare_test_data(
        pgsql, approver1, approvers=[[approver1], [approver2]],
    )
    approver_id2 = db_helpers.add_user(pgsql, approver2, 'test@gmail.com')
    role_id = db_helpers.add_role(
        pgsql, approver_id1, rolenode_id, 'requested',
    )
    db_helpers.add_approve(pgsql, role_id, approver_id2)

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': approver1},
    )
    assert response.status_code == 200
    assert response.json() == {'granted': True}
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'granted'


async def test_approve_role_old_role_version_approve(taxi_bank_idm, pgsql):
    approver1 = 'test_user1'
    approver2 = 'test_user2'
    approver_id1, rolenode_id = db_helpers.prepare_test_data(
        pgsql, approver1, approvers=[[approver1], [approver2]],
    )
    approver_id2 = db_helpers.add_user(pgsql, approver2, 'test@gmail.com')
    new_role_version = 1
    role_id = db_helpers.add_role(
        pgsql,
        approver_id1,
        rolenode_id,
        'requested',
        version=new_role_version,
    )
    db_helpers.add_approve(pgsql, role_id, approver_id2)

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': approver1},
    )
    assert response.status_code == 200
    assert response.json() == {'granted': False}


async def test_approve_role_reapproved(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    db_helpers.add_approve(pgsql, role_id, user_id, 'declined')
    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'granted'
    assert response.json() == {'granted': True}


async def test_approve_role_declined(taxi_bank_idm, pgsql):
    approver1 = 'test_user1'
    approver2 = 'test_user2'
    approver_id1, rolenode_id = db_helpers.prepare_test_data(
        pgsql, approver1, approvers=[[approver1], [approver2]],
    )
    approver_id2 = db_helpers.add_user(pgsql, approver2, 'test@gmail.com')
    role_id = db_helpers.add_role(
        pgsql, approver_id1, rolenode_id, 'requested',
    )
    db_helpers.add_approve(pgsql, role_id, approver_id2, 'declined')

    response = await taxi_bank_idm.post(
        'v1/approve-role',
        json={'role_id': role_id, 'approver_login': approver1},
    )
    assert response.status_code == 200
    assert response.json() == {'granted': False}
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'requested'
