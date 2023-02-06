async def test_json(http_api, tap):
    with tap.plan(4):
        t = await http_api()

        await t.get_ok('api_developer_json')
        t.status_is(200, diag=True)
        t.json_is('code', 'TEST')
        t.json_is('message', 'Test Message')
