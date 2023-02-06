async def test_ping_auth(api, tap):
    with tap.plan(5, 'пингуем'):
        t = await api()

        await t.get_ok('api_print_admin_ping')
        t.status_is(200, diag=True)

        t.content_type_like(r'^application/json')

        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')
