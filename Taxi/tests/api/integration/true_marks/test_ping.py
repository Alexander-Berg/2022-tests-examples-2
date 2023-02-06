async def test_ping(api, tap):
    with tap.plan(4):
        t = await api(role='admin')
        await t.get_ok('api_integration_true_marks_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')