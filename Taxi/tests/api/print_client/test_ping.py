async def test_ping(api, tap):

    tap.plan(4)
    t = await api(spec='doc/api/print-client.yaml')

    await t.get_ok('api_print_client_ping')
    t.status_is(200, diag=True)

    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    tap()

