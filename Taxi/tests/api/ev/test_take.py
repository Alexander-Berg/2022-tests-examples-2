import asyncio

import pytest
from stall.model.event import Event


@pytest.mark.parametrize('method', ['take', 'take_timeout'])
async def test_take(method, tap, mongo):  # pylint: disable=unused-argument
    with tap.plan(17):
        tap.note('Run tests for method: ' + method)

        async def _take(method, keys, state):
            if method == 'take':
                return await Event.take(keys, state)
            if method == 'take_timeout':
                return await Event.take_timeout(keys, state, 0)

            raise RuntimeError('что-то странное')

        state, events = await _take(method, [['abc']], None)

        tap.ok(state, 'новый state передан')
        tap.isa_ok(events, list, 'евенты списком')
        tap.eq(state['min_id'], state['last_id'], 'min_id == last_id')
        tap.eq(events, [], 'нет событий при инициализации')


        ev = Event({'key': ['abc'], 'data': {'hello': 'world'}})
        tap.ok(ev, 'event инстанцирован')

        pushed = await ev.push()
        tap.ok(pushed, 'push')
        # ждём пока демон докрутит цикл
        for _ in range(100):
            await asyncio.sleep(.3)
            if pushed in ev.__class__.cache['items']:
                break

        state2, events = await _take(method, [['abc']], None)
        tap.eq(state2['min_id'], state['min_id'] + 1, 'min_id')
        tap.eq(state2['last_id'], state['last_id'] + 1, 'last_id')
        tap.eq(events, [], 'нет событий для данного ключа')

        state2, events = await _take(method, [['cde']], state)
        tap.eq(state2['min_id'], state['min_id'], 'min_id')
        tap.eq(state2['last_id'], state['last_id'] + 1, 'last_id')
        tap.eq(events, [], 'нет событий для данного ключа')

        state2, events = await _take(method, [['cde'], ['abc'], ['def']], state)
        tap.eq(state2['min_id'], state['min_id'], 'min_id')
        tap.eq(state2['last_id'], state['last_id'] + 1, 'last_id')
        tap.eq(len(events), 1, 'события для данного ключа')

        ev = events[0]

        tap.eq(ev.key, ['abc'], 'ключ')
        tap.eq(ev.data, {'hello': 'world'}, 'данные')
