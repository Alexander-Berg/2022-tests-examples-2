async def test_ping(api, tap):
    with tap.plan(4, 'пингуем'):
        t = await api()
        await t.get_ok('api_external_assortments_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')

