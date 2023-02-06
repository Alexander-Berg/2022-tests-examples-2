from stall.client.ev import EvClient


async def test_ping(tap, server):
    with tap.plan(4):
        app = await server(spec='doc/api/ev.yaml')
        tap.ok(app, 'сервер событий запущен')

        client = EvClient(base_url =
                          f'http://localhost:{app.port}/api/ev')

        tap.ok(client, 'клиент создан')
        tap.ok(client.base_url, 'Базовый урл назначен')

        res = await client.ping()
        tap.eq(res, {'code': 'OK', 'message': 'PONG'}, 'ответ сервера')

        await client.close()

async def test_take(tap, server):
    with tap.plan(6):
        app = await server(spec='doc/api/ev.yaml')
        tap.ok(app, 'сервер событий запущен')

        client = EvClient(base_url =
                          f'http://localhost:{app.port}/api/ev',
                          timeout = 2)

        tap.ok(client, 'клиент создан')
        tap.ok(client.base_url, 'Базовый урл назначен')

        res = await client.take([['hello']])
        tap.eq(res['code'], 'INIT', 'ответ')
        tap.in_ok('state', res, 'state есть')
        tap.eq(res['events'], [], 'событий пока нет')

        await client.close()
