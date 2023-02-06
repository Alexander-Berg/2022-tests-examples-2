import asyncio

from stall.model.event import Event

async def test_take(mongo, api, tap): # pylint: disable=unused-argument
    with tap.plan(13):
        t = await api()

        loop = asyncio.get_event_loop()

        started = loop.time()

        await t.post_ok('api_ev_take',
                        json={'keys': [["hello"]], 'timeout': 3},
                        desc='нет state')
        t.status_is(200, diag=True)
        t.content_type_like('^application/json', 'content_type')
        t.json_is('code', 'INIT', 'code')
        t.json_is('events', [], 'events')
        t.json_hasnt('message', 'message отсутствует')

        t.tap.ok(loop.time() - started < 1, 'запрос выполнился сразу')


        started = loop.time()

        state = t.res['json']['state']

        ev = Event({'key': ['hello'], 'data': {'a': 'b'}})

        pushed = await ev.push()
        tap.ok(pushed, 'Сообщение отправлено')
        # ждём пока демон докрутит цикл
#         for _ in range(100):
#             await asyncio.sleep(.3)
#             if pushed in ev.__class__.cache['items']:
#                 break

        await t.post_ok('api_ev_take',
                        json={
                            'keys': [["hello"]],
                            'timeout': 3,
                            'state': state,
                        },
                        desc='нет state')
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код ответа')
        t.json_is('events.0.key', ['hello'], 'ключ ответа')
        t.json_is('events.0.data', {'a': 'b'}, 'данные ответа')
