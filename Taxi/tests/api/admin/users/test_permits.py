async def test_permits(tap, api, dataset):
    with tap:
        user = await dataset.user()
        tap.ok(user, 'пользователь создан')

        t = await api(user=user)

        await t.post_ok('api_admin_users_permits', json={})
        t.status_is(200, diag=True)
        t.json_has('roles.1')


        await t.post_ok('api_admin_users_permits', json={'roles': ['admin']})
        t.status_is(200, diag=True)
        t.json_has('roles.0')
        t.json_hasnt('roles.1')

        t.json_is('roles.0.role', 'admin')
        t.json_has('roles.0.permits.5.name')
        t.json_has('roles.0.permits.5.value')
