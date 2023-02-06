import time

import aiohttp

from stall import maintenance


async def test_ping(tap, server, cfg):
    with tap.plan(10):
        app = await server(spec='doc/api/developer.yaml')
        tap.ok(app, 'сервер запущен')

        base_url = f'http://localhost:{app.port}'

        async with aiohttp.ClientSession() as session:
            cfg.set(
                'maintenance.schedule',
                [{'from': time.time() - 15, 'to': time.time() + 60}],
            )
            maintenance.SCHEDULE = None

            async with session.get(f'{base_url}/api/developer/ping') as resp:
                tap.eq(resp.status, 503, 'статус остановки')
                tap.ok(
                    'X-Stall-Version' in resp.headers,
                    'отработали вышестоящие миддлварю',
                )

                rjson = await resp.json()

                tap.ok(rjson, 'json ответа распарсен')
                tap.eq(
                    rjson['code'],
                    'ER_SERVICE_UNAVAILABLE',
                    'код остновки в ответе',
                )
                tap.eq(
                    rjson['message'],
                    'Service maintenance in progress',
                    'сообщение в ответе',
                )

            cfg.set(
                'maintenance.schedule',
                [{'from': time.time() - 15, 'to':  time.time() - 10}],
            )
            maintenance.SCHEDULE = None

            async with session.get(f'{base_url}/api/developer/ping') as resp:
                tap.eq(resp.status, 200, 'остановка завершена')

                rjson = await resp.json()

                tap.ok(rjson, 'json ответа распарсен')
                tap.eq(rjson['code'], 'OK', 'код успеха в ответе')
                tap.eq(rjson['message'], 'PONG', 'сообщение в ответе')
