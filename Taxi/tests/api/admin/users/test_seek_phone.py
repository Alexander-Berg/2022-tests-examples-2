async def test_common(tap, dataset, api):
    with tap.plan(9, 'поиск юзеров по телефону'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        seekable = await dataset.user(company_id=admin.company_id,
                                      store_id=None,
                                      provider='internal',
                                      role='executer',
                                      phone='88005553535',
                                      status='active')
        tap.ok(seekable, 'user to seek created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', seekable.user_id)
        t.json_hasnt('users.1')


async def test_wrong_phone(tap, dataset, api):
    with tap.plan(7, 'поиск юзеров по неизвестному телефону'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        seekable = await dataset.user(company_id=admin.company_id,
                                      store_id=None,
                                      provider='internal',
                                      role='executer',
                                      phone='88005553535')
        tap.ok(seekable, 'user to seek created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '800',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_hasnt('users.0')


async def test_inactive(tap, dataset, api):
    with tap.plan(11, 'поиск неактивных пользователей'):
        cur_user = await dataset.user()
        seek_user = await dataset.user(
            company_id=cur_user.company_id,
            store_id=None,
            provider='internal',
            role='executer',
            phone='88005553535',
            status='disabled',
        )

        cur_user.role.remove_permit('users_seek_disabled')
        t = await api(user=cur_user)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_hasnt('users.0')
        cur_user.role.add_permit('users_seek_disabled', True)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_is('users.0.user_id', seek_user.user_id)
        t.json_hasnt('users.1')


async def test_foreign_company(tap, dataset, api):
    with tap.plan(7, 'поиск юзеров из чужой компании'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        company = await dataset.company()

        seekable = await dataset.user(company=company,
                                      store_id=None,
                                      provider='internal',
                                      role='executer',
                                      phone='88005553535')
        tap.ok(seekable, 'user to seek created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_hasnt('users.0')


async def test_not_internal(tap, dataset, api):
    with tap.plan(7, 'поиск юзеров с provider!=internal'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        seekable = await dataset.user(company_id=admin.company_id,
                                      store_id=None,
                                      provider='yandex-team',
                                      phone='88005553535')
        tap.ok(seekable, 'user to seek created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_hasnt('users.0')


async def test_with_store(tap, dataset, api):
    with tap.plan(15, 'поиск юзеров привязанных к складу'):
        admin = await dataset.user()
        tap.ok(admin, 'admin created')

        seekable = await dataset.user(company_id=admin.company_id,
                                      store_id=admin.store_id,
                                      provider='internal',
                                      role='executer',
                                      phone='88005553535')
        tap.ok(seekable, 'user to seek created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_hasnt('users.0')

        await t.post_ok(
            'api_admin_users_seek_phone',
            json={
                'phone': '88005553535',
                'cursor': None,
                'store_empty': False
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', seekable.user_id)
        t.json_hasnt('users.1')
        t.json_has('cursor')
