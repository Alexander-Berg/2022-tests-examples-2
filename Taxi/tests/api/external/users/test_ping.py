async def test_ping(tap, api):
    with tap:
        t = await api(role='admin')
        await t.get_ok('api_external_users_ping')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('message', 'PONG', 'pong')
