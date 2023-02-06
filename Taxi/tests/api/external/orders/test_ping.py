async def test_ping(api, tap):
    tap.plan(4)

    t = await api()
    await t.set_role('admin')

    await t.get_ok('api_external_orders_ping')
    t.status_is(200, diag=True)

    t.json_is('code', 'OK', 'code')
    t.json_is('message', 'PONG', 'pong')


    tap()