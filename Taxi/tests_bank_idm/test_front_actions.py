import tests_bank_idm.db_helpers as db_helpers


async def test_front_actions_by_user_login(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, _ = db_helpers.prepare_test_data(pgsql, user_login)
    request = {'user_login': user_login}
    db_helpers.add_action(pgsql, 1, 'Mock Action', user_id=user_id)
    db_helpers.add_action(pgsql, 1, 'Mock Action 2', user_id=user_id)

    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 200
    actions = response.json()['actions']
    assert len(actions) == 2


async def test_front_actions_by_system_slug(taxi_bank_idm, pgsql):
    system_slug = 'test_system'
    user_id = db_helpers.add_user(pgsql, 'test_user', 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    request = {'system_slug': system_slug}
    db_helpers.add_action(pgsql, system_id, 'Mock Action')
    db_helpers.add_action(pgsql, system_id, 'Mock Action 2')

    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 200
    actions = response.json()['actions']
    assert len(actions) == 2


async def test_front_actions_by_role_id(taxi_bank_idm, pgsql):
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login='test_user',
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id)
    request = {'role_id': role_id}
    db_helpers.add_action(pgsql, 1, 'Mock Action', role_id=role_id)
    db_helpers.add_action(pgsql, 1, 'Mock Action 2', role_id=role_id)

    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 200
    actions = response.json()['actions']
    assert len(actions) == 2


async def test_front_actions_by_multiple_fields(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    user_id, rolenode_id = db_helpers.prepare_test_data(pgsql, user_login)

    system_slug = 'test_system'
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id)

    request = {
        'user_login': user_login,
        'system_slug': system_slug,
        'role_id': role_id,
    }
    db_helpers.add_action(
        pgsql, system_id, 'Mock Action', user_id=user_id, role_id=role_id,
    )
    db_helpers.add_action(
        pgsql, system_id, 'Mock Action 2', user_id=user_id, role_id=role_id,
    )

    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 200
    actions = response.json()['actions']
    assert len(actions) == 2


async def test_front_actions_bad_input(taxi_bank_idm, pgsql):
    db_helpers.prepare_test_data(pgsql, user_login='test_user')
    response = await taxi_bank_idm.post('v1/front/v1/actions', json={})
    assert response.status_code == 400


async def test_front_actions_user_not_found(taxi_bank_idm, pgsql):
    db_helpers.prepare_test_data(pgsql, user_login='test_user')
    request = {'user_login': 'not_existed_user'}
    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 404


async def test_front_actions_system_not_found(taxi_bank_idm, pgsql):
    db_helpers.prepare_test_data(pgsql, user_login='test_user')
    request = {'system_slug': 'not_existed_system'}
    response = await taxi_bank_idm.post('v1/front/v1/actions', json=request)
    assert response.status_code == 404
