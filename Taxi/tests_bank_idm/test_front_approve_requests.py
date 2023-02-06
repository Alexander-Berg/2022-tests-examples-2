import tests_bank_idm.db_helpers as db_helpers


async def test_front_approve_requests(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    receiver_user_login = 'user_who_gets_role_1'
    _, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    test_user_id_1 = db_helpers.add_user(
        pgsql, user_login=receiver_user_login, user_email='@',
    )
    db_helpers.add_role(pgsql, test_user_id_1, rolenode_id)
    request = {'user_login': user_login}

    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json=request,
    )
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
    assert role['receiver_login'] == receiver_user_login
    assert role['requester_login'] == receiver_user_login


async def test_front_approve_requests_few_roles(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    _, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login, approvers=[[user_login]],
    )
    test_user_id_1 = db_helpers.add_user(
        pgsql, user_login='user_who_gets_role_1', user_email='@',
    )
    test_user_id_2 = db_helpers.add_user(
        pgsql, user_login='user_who_gets_role_2', user_email='@',
    )
    db_helpers.add_role(pgsql, test_user_id_1, rolenode_id)
    db_helpers.add_role(pgsql, test_user_id_2, rolenode_id)
    request = {'user_login': user_login}

    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json=request,
    )
    assert response.status_code == 200
    assert len(response.json()['roles']) == 2


async def test_front_approve_requests_user_not_found(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests',
        json={'user_login': 'not_existed_user'},
    )
    assert response.status_code == 404


async def test_front_approve_requests_after_set(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    receiver_user_login_1 = 'user_who_gets_role_1'
    receiver_user_login_2 = 'user_who_gets_role_2'
    slug_path = 'test/slug_path'
    _, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    test_user_id_1 = db_helpers.add_user(
        pgsql, user_login=receiver_user_login_1, user_email='@',
    )
    test_user_id_2 = db_helpers.add_user(
        pgsql, user_login=receiver_user_login_2, user_email='@',
    )
    db_helpers.add_user(pgsql, 'approver1', 'test@gmail.com')
    db_helpers.add_role(pgsql, test_user_id_1, rolenode_id)

    approvers = {'logins': [['approver1']]}
    request = {
        'system_slug': 'test_slug',
        'user_login': 'responsible',
        'slug_path': slug_path,
        'approvers': approvers,
    }

    await taxi_bank_idm.post('v1/set-approvers', json=request)
    await taxi_bank_idm.post('v1/set-approvers', json=request)

    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json={'user_login': 'approver1'},
    )

    assert len(response.json()['roles']) == 1

    db_helpers.add_role(pgsql, test_user_id_2, rolenode_id)

    await taxi_bank_idm.post('v1/set-approvers', json=request)

    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json={'user_login': 'approver1'},
    )

    assert len(response.json()['roles']) == 2


async def test_front_approve_requests_after_drop(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    receiver_user_login_1 = 'user_who_gets_role_1'
    slug_path = 'test/slug_path'
    _, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)
    test_user_id_1 = db_helpers.add_user(
        pgsql, user_login=receiver_user_login_1, user_email='@',
    )
    db_helpers.add_user(pgsql, 'approver1', 'test@gmail.com')
    db_helpers.add_user(pgsql, 'approver2', 'test@gmail.com')
    db_helpers.add_role(pgsql, test_user_id_1, rolenode_id)

    approvers = {'logins': [['approver1'], ['approver2']]}
    request = {
        'system_slug': 'test_slug',
        'user_login': 'responsible',
        'slug_path': slug_path,
        'approvers': approvers,
    }

    await taxi_bank_idm.post('v1/set-approvers', json=request)

    response_first = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json={'user_login': 'approver1'},
    )
    assert len(response_first.json()['roles']) == 1

    response_second = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json={'user_login': 'approver2'},
    )
    assert len(response_second.json()['roles']) == 1

    request['approvers'] = {'logins': [['approver1']]}

    await taxi_bank_idm.post('v1/set-approvers', json=request)

    response = await taxi_bank_idm.post(
        'v1/front/v1/approve-requests', json={'user_login': 'approver2'},
    )

    assert not response.json()['roles']
