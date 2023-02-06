async def test_ping(tap, api):
    with tap.plan(4):
        t = await api()

        await t.get_ok('api_tsd_stock_ping')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')
