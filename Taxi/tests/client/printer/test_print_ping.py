from stall.client.print import PrintClient

async def test_ping(tap, server):
    with tap.plan(4):
        app = await server(spec='doc/api/print.yaml')
        tap.ok(app, 'сервер печати запущен')

        client = PrintClient(base_url =
                             f'http://localhost:{app.port}/api/print')

        tap.ok(client, 'клиент создан')
        tap.ok(client.base_url, 'Базовый урл назначен')

        res = await client.ping()
        tap.eq(res, {'code': 'OK', 'message': 'PONG'}, 'ответ сервера')

        await client.close()
