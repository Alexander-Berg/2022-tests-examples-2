async def test_ping(tap, api):
    with tap.plan(3, 'пингуем'):
        t = await api()
        await t.get_ok('api_admin_falcon_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
