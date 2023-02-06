async def test_ping(tap, api):
    t = await api()

    tap.plan(4)
    await t.get_ok('api_profile_ping')
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    tap()
