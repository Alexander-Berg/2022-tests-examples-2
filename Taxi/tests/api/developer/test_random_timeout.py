async def test_timeout(http_api, tap, now):
    with tap.plan(6, 'Случайные паузы'):
        t = await http_api()


        started = now()

        await t.get_ok('api_developer_ping',
                       headers={
                           'X-Libstall-Random-Timeout': 2,
                       })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'PONG')
        t.header_has('X-Libstall-Random-Timeout-Result')

        timeout = float(t.res['headers']['X-Libstall-Random-Timeout-Result'])
        real =  now().timestamp() - started.timestamp()

        tap.ok(
            timeout <= real,
            f'Пауза вставлена ({timeout} <= {real})'
        )

