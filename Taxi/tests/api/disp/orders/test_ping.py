async def test_ping(tap, api):
    with tap.plan(4):
        t = await api(role='admin')

        await t.get_ok('api_disp_orders_ping')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')
