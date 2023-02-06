from stall.backend_version import version

async def test_ping(tap, api):
    with tap.plan(4, 'пингуем'):
        t = await api()
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')


async def test_ping_version_header(tap, api):
    with tap.plan(4, 'пингуем'):
        t = await api()
        await t.get_ok('api_developer_ping')
        t.status_is(200, diag=True)
        t.header_has('X-Stall-Version')
        t.header_is('X-Stall-Version', version)
