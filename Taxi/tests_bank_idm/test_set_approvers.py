import tests_bank_idm.db_helpers as db_helpers


async def test_set_approvers(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    slug_path = 'test/slug_path'
    _, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
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
        'system_slug': 'test_slug',
        'user_login': 'responsible',
        'slug_path': slug_path,
        'approvers': approvers,
    }

    response = await taxi_bank_idm.post('v1/set-approvers', json=request)
    assert response.status_code == 200
    approvers_from_db = db_helpers.get_approvers(pgsql, rolenode_id, 1)
    assert approvers_from_db == approvers


async def test_set_approvers_not_existed_approver(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    slug_path = 'test/slug_path'
    db_helpers.prepare_test_data(pgsql, user_login)
    approvers = {'logins': [['not_existed_user1']]}
    request = {
        'system_slug': 'test_slug',
        'user_login': 'responsible',
        'slug_path': slug_path,
        'approvers': approvers,
    }

    response = await taxi_bank_idm.post('v1/set-approvers', json=request)
    assert response.status_code == 404


async def test_set_approvers_slug_path_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {
        'system_slug': 'test_slug',
        'user_login': 'responsible',
        'slug_path': 'not_existed_slug_path',
        'approvers': {'logins': []},
    }

    response = await taxi_bank_idm.post('v1/set-approvers', json=request)
    assert response.status_code == 404


async def test_set_approvers_system_not_found(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {
        'system_slug': 'not_existed_system',
        'user_login': 'responsible',
        'slug_path': 'test/slug_path',
        'approvers': {'logins': []},
    }

    response = await taxi_bank_idm.post('v1/set-approvers', json=request)
    assert response.status_code == 404


async def test_set_approvers_not_allowed(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    request = {
        'system_slug': 'test_slug',
        'user_login': user_login,
        'slug_path': 'test/slug_path',
        'approvers': {'logins': []},
    }

    response = await taxi_bank_idm.post('v1/set-approvers', json=request)
    assert response.status_code == 403
