import asyncio

from stall.time_meter import TimeMeter


async def test_time_meter_async(tap):
    with tap.plan(4, 'Тесты измерялки времени: async with'):
        tap.ok(TimeMeter('Test'), 'инстанцирован')
        async with TimeMeter('Test') as tm:
            tap.isa_ok(tm, TimeMeter, 'Инстанцирован и aenter')
            await asyncio.sleep(.001)

        tap.ok(tm.finished > tm.started, 'Время финиша есть')
        tap.in_ok('elapsed', tm.message[1], 'elapsed вычислено')


async def test_time_meter_sync(tap):
    with tap.plan(4, 'Тесты измерялки времени: with'):
        tap.ok(TimeMeter('Test'), 'инстанцирован')
        with TimeMeter('Test') as tm:
            tap.isa_ok(tm, TimeMeter, 'Инстанцирован и aenter')
            await asyncio.sleep(.001)

        tap.ok(tm.finished > tm.started, 'Время финиша есть')
        tap.in_ok('elapsed', tm.message[1], 'elapsed вычислено')

async def test_time_meter_solomon_log(metrics_log_mock, tap):
    with tap.plan(5, 'Тест логирования в соломон'):
        tap.ok(TimeMeter('Test', solomon_signal='test_signal'), 'инстанцирован')
        with TimeMeter('Test', solomon_signal='test_signal') as tm:
            tap.isa_ok(tm, TimeMeter, 'Инстанцирован и aenter')
            await asyncio.sleep(.001)

        tap.ok(tm.finished > tm.started, 'Время финиша есть')
        tap.in_ok('elapsed', tm.message[1], 'elapsed вычислено')
        tap.ok(len(metrics_log_mock) == 1, 'Лог отправлен')

async def test_time_meter_no_solomon(metrics_log_mock, tap):
    with tap.plan(5, 'Тест логирования в соломон без параметра'):
        tap.ok(TimeMeter('Test'), 'инстанцирован')
        with TimeMeter('Test') as tm:
            tap.isa_ok(tm, TimeMeter, 'Инстанцирован и aenter')
            await asyncio.sleep(.001)

        tap.ok(tm.finished > tm.started, 'Время финиша есть')
        tap.in_ok('elapsed', tm.message[1], 'elapsed вычислено')
        tap.ok(len(metrics_log_mock) == 0, 'Лог отправлен')
