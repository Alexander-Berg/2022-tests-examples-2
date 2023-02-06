import aiohttp


async def test_server(server, tap):
    with tap.plan(6, 'Проверим работы фикстуры server'):
        app = await server(spec='doc/api/developer.yaml')
        tap.ok(app, 'сервер запущен')

        base_url = f'http://localhost:{app.port}'
        tap.like(base_url, r':\d+$', 'урл: ' + base_url)

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{base_url}/api/developer/ping') as resp:
                tap.eq(resp.status, 200, 'Код ответа сервера')
                rjson = await resp.json()

                tap.ok(rjson, 'json ответа распарсен')
                tap.eq(rjson['code'], 'OK', 'код в ответе')
                tap.eq(rjson['message'], 'PONG', 'сообщение в ответе')
