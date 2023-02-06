import pytest

import tests_bank_idm.db_helpers as db_helpers


async def test_decline_role(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select approve_status from bank_idm.approves
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'declined'


async def test_decline_role_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': 100500, 'approver_login': user_login},
    )
    assert response.status_code == 404


async def test_decline_role_system_disabled(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, system_status='disabled', approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


async def test_decline_role_rolenode_disabled(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql,
        user_login,
        rolenode_status='disabled',
        approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('role_status', ['deprived', 'granted'])
async def test_decline_role_bad_role_status(taxi_bank_idm, pgsql, role_status):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, role_status)
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 400


async def test_decline_role_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'test_user_without_permissions'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 403


async def test_decline_role_already_declined(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')
    db_helpers.add_approve(pgsql, role_id, user_id, 'declined')
    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': user_login},
    )
    assert response.status_code == 409


async def test_decline_role_responsible_fallback(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    responsible_user = 'responsible'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, responsible_user=responsible_user,
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, 'requested')

    response = await taxi_bank_idm.post(
        'v1/decline-role',
        json={'role_id': role_id, 'approver_login': responsible_user},
    )
    assert response.status_code == 200
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select approve_status from bank_idm.approves
        where role_id = {role_id}
        """,
    )
    role = cursor.fetchall()[0]
    assert role[0] == 'declined'
