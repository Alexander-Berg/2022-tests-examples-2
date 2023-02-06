async def test_ping(api, mongo): # pylint: disable=unused-argument
    t = await api()
    t.tap.plan(5)
    await t.get_ok('api_ev_ping')
    t.status_is(200, diag=True)

    t.content_type_like(r'^application/json')

    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    t.tap()
