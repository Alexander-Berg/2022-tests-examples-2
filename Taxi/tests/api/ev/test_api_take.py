import asyncio
import base64

from stall.model.event import Event
from libstall import json_pp as json


async def test_take(mongo, api, tap): # pylint: disable=unused-argument
    with tap.plan(24):
        t = await api()

        loop = asyncio.get_event_loop()

        started = loop.time()

        await t.post_ok('api_ev_take',
                        json={'keys': [[1, 2, 3]], 'timeout': 3},
                        desc='нет state')
        t.status_is(200, diag=True)
        t.content_type_like('^application/json', 'content_type')
        t.json_is('code', 'INIT', 'code')
        t.json_is('events', [], 'events')
        t.json_hasnt('message', 'message отсутствует')

        t.tap.ok(loop.time() - started < 1, 'запрос выполнился сразу')


        started = loop.time()

        state = t.res['json']['state']
        await t.post_ok('api_ev_take',
                        json={
                            'keys': [[1, 2, 3]],
                            'timeout': .5,
                            'state': state
                        },
                        desc='повторяем state')

        t.status_is(200, diag=True)
        t.content_type_like('^application/json', 'content_type')
        t.tap.ok(loop.time() - started >= .5, 'таймаут ждали')
        t.json_is('code', 'OK', 'code')
        t.json_is('events', [], 'events')
        t.json_hasnt('message', 'message отсутствует')

        state2 = t.res['json']['state']

        state_u = json.loads(base64.b64decode(state.encode().decode()))
        state2_u = json.loads(base64.b64decode(state2.encode().decode()))
        for s in state_u, state2_u:
            tap.in_ok('time', s, 'time есть в state')
            del s['time']

        t.tap.eq(state_u, state2_u, 'state не поменялся')


        for _ in range(50):
            await Event({'key': ['cde'], 'data': {}}).push()


        await t.post_ok('api_ev_take',
                        json={
                            'keys': [[1, 2, 3]],
                            'timeout': .5,
                            'state': state
                        },
                        desc='повторяем state')
        t.content_type_like('^application/json', 'content_type')
        t.tap.ok(loop.time() - started >= .5, 'таймаут ждали')
        t.json_is('code', 'OK', 'code')
        t.json_is('events', [], 'events')
        t.json_hasnt('message', 'message отсутствует')

        state2 = t.res['json']['state']
        t.tap.ne(state, state2, 'state поменялся другими событиями')
