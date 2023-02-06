async def test_ping_auth(api, dataset):
    t = await api()

    t.tap.plan(7)
    user = await dataset.user(role='admin')
    t.tap.ok(user, 'пользователь создан')

    token = user.token(user.device[0])
    t.tap.ok(token, 'токен есть')


    await t.get_ok('api_admin_users_ping',
                   headers={
                       'Authorization': 'Bearer ' + token
                   })


    t.status_is(200, diag=True)

    t.content_type_like(r'^application/json')

    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    t.tap()


async def test_ping_auth_shortcut(api, dataset):
    t = await api()

    t.tap.plan(5)
    user = await dataset.user(role='admin')
    t.set_user(user)

    await t.get_ok('api_admin_users_ping')

    t.status_is(200, diag=True)

    t.content_type_like(r'^application/json')

    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    t.tap()
