async def test_exception(http_api, tap):
    with tap.plan(8):
        t = await http_api()

        await t.get_ok('api_developer_exception')
        t.status_is(500, diag=True)
        t.json_is('code', 'ER_INTERNAL')
        t.json_is('message', 'Internal Error')

        t.json_has('details.stack')
        t.json_is('details.type', 'EXCEPTION')
        t.json_is('details.exception_type', "<class 'RuntimeError'>")
        t.json_is('details.message', 'hello')
