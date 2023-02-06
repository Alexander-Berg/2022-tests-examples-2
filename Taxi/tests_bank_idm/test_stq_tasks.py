import tests_bank_idm.db_helpers as db_helpers


async def test_bank_idm_roles_depriving(stq_runner, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, 'test/slug_path', 'Slug Path', system_id, 'disabled',
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    action_id = db_helpers.add_action(pgsql, system_id, 'Mock Action')

    await stq_runner.bank_idm_roles_depriving.call(
        task_id='sample_task',
        kwargs={
            'system_id': system_id,
            'rolenode_id': rolenode_id,
            'action_id': action_id,
        },
        expect_fail=False,
    )
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where rolenode_id = {rolenode_id}
        """,
    )
    rolenode_status = cursor.fetchall()[0][0]
    assert rolenode_status == 'deprived'


async def test_bank_idm_roles_depriving_action_not_found(stq_runner, pgsql):
    user_login = 'test_user'
    system_slug = 'test_slug'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)
    rolenode_id = db_helpers.add_role_nodes(
        pgsql, 'test/slug_path', 'Slug Path', system_id, 'disabled',
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    action_id = 100500  # not existed action_id

    await stq_runner.bank_idm_roles_depriving.call(
        task_id='sample_task',
        kwargs={
            'system_id': system_id,
            'rolenode_id': rolenode_id,
            'action_id': action_id,
        },
        expect_fail=False,
    )
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        select role_status from bank_idm.roles
        where rolenode_id = {rolenode_id}
        """,
    )
    rolenode_status = cursor.fetchall()[0][0]
    assert rolenode_status == 'granted'
