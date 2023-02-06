import asyncio
import pytest

from stall.model.event import Event


@pytest.mark.non_parallel
async def test_empty(tap, mongo): # pylint: disable=unused-argument
    with tap.plan(17):
        loop = asyncio.get_event_loop()

        started = loop.time()

        state, events = await Event.take_timeout([['abc']], None, 1)

        tap.ok(loop.time() - started < 0.3,
               'таймаут не выдерживается перв запрос')

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

        started = loop.time()

        state2, events = await Event.take_timeout([['cde']], state, .3)
        tap.in_ok(state2['min_id'],
                  (state['min_id'], state['min_id'] + 1),
                  'min_id не поменялся')
        tap.in_ok(state2['last_id'],
                  # если не успеет - первое значение
                  (state['last_id'], state['last_id'] + 1),
                  'last_id')
        tap.eq(events, [], 'нет событий для данного ключа')

        tap.ok(loop.time() - started >= 0.3,
               'таймаут выдерживается - нет данных')


        started = loop.time()
        state2, events = await Event.take_timeout([['cde'], ['abc'], ['def']],
                                                  state,
                                                  10)
        tap.eq(state2['min_id'], state['min_id'], 'min_id')
        tap.eq(state2['last_id'], state['last_id'] + 1, 'last_id')
        tap.eq(len(events), 1, 'события для данного ключа')
        tap.ok(loop.time() - started < 0.3, 'таймаут не раб: есть данные')

        ev = events[0]

        tap.eq(ev.key, ['abc'], 'ключ')
        tap.eq(ev.data, {'hello': 'world'}, 'данные')
