import pytest

import tests_bank_idm.db_helpers as db_helpers


# TODO: Use db_helpers to create system and use that system instead IDM (self)
async def test_create_role_simple_role(taxi_bank_idm, pgsql):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(f'select * from bank_idm.actions where system_id = 1')
    actions_count = len(cursor.fetchall())
    db_helpers.add_user(pgsql, 'approver1_1', 'test@gmail.com')
    db_helpers.add_user(pgsql, 'approver1_2', 'test@gmail.com')
    db_helpers.add_user(pgsql, 'approver2', 'test@gmail.com')
    db_helpers.add_user(pgsql, 'approver3', 'test@gmail.com')

    approvers = {
        'logins': [
            ['approver1_1', 'approver1_2'],
            ['approver2'],
            ['approver3'],
        ],
    }
    request = {
        'system_slug': 'idm',
        'user_login': 'kalievoral',
        'role_name': 'Test Role',
        'slug_path': 'test_role',
        'approvers': approvers,
        'hide': False,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 200

    cursor.execute(
        'select slug_path, role_name, is_leaf, is_hidden '
        'from bank_idm.role_nodes '
        'where system_id = 1 and role_name = \'Test Role\'',
    )
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0][0] == 'test_role'
    assert result[0][1] == 'Test Role'
    assert result[0][2]
    assert not result[0][3]
    cursor.execute(f'select * from bank_idm.actions where system_id = 1')
    assert len(cursor.fetchall()) - actions_count == 1


async def test_create_role_not_existed_approver(taxi_bank_idm, pgsql):
    approvers = {'logins': [['not_existed_user1']]}
    db_helpers.prepare_test_data(pgsql, 'test_user')
    request = {
        'system_slug': 'idm',
        'user_login': 'responsible',
        'role_name': 'Test Role',
        'slug_path': 'test_role',
        'approvers': approvers,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'slug_path', ['/a', 'a/', 'a/b/', '@a/b', 'a@/b', 'a/@b'],
)
async def test_create_role_bad_slug_path(taxi_bank_idm, pgsql, slug_path):
    request = {
        'system_slug': 'idm',
        'user_login': 'kalievoral',
        'role_name': 'Test Role',
        'slug_path': slug_path,
        'hide': False,
    }
    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 400


async def test_create_role_nested_role(taxi_bank_idm, pgsql):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(f'select * from bank_idm.actions where system_id = 1')
    actions_count = len(cursor.fetchall())

    request = {
        'system_slug': 'idm',
        'user_login': 'kalievoral',
        'role_name': 'Test Role',
        'slug_path': 'test_role/nested_part',
        'hide': False,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 200

    cursor.execute(
        'select slug_path, role_name, is_leaf, is_hidden, '
        'rolenode_id, parent_rolenode_id '
        'from bank_idm.role_nodes '
        'where system_id = 1 and role_name = \'Test Role\'',
    )
    result = cursor.fetchall()
    assert len(result) == 2
    print(result)
    assert result[0][0] == 'test_role'
    assert result[0][1] == 'Test Role'
    assert not result[0][2]
    assert not result[0][3]
    rolenode_id = result[0][4]
    assert not result[0][5]

    assert result[1][0] == 'test_role/nested_part'
    assert result[1][1] == 'Test Role'
    assert result[1][2]
    assert not result[1][3]
    assert result[1][5] == rolenode_id

    cursor.execute(f'select * from bank_idm.actions where system_id = 1')
    assert len(cursor.fetchall()) - actions_count == 2


async def test_create_role_no_root_rolenode(taxi_bank_idm):
    request = {
        'system_slug': 'not_existed_system_slug',
        'user_login': 'kalievoral',
        'role_name': 'Test Role',
        'slug_path': 'test_role/nested_part',
        'hide': False,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 404


async def test_create_role_add_to_leaf_error(taxi_bank_idm):
    request = {
        'system_slug': 'idm',
        'user_login': 'kalievoral',
        'role_name': 'Test Role',
        'slug_path': 'systems/idm/responsible/another_leaf_role',
        'hide': False,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 400


async def test_create_role_not_allowed_to_create_role(taxi_bank_idm, pgsql):
    user_login = 'user_without_permission'
    db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    request = {
        'system_slug': 'idm',
        'user_login': user_login,
        'role_name': 'Test Role',
        'slug_path': 'test_role',
        'hide': False,
    }

    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 403
