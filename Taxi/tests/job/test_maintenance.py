import asyncio
import time

from stall import maintenance

PROCESSED = []


async def mytest(**kwargs):
    PROCESSED.append(kwargs['foo'])
    return kwargs


async def test_process(tap, job, cfg):
    with tap:
        task1 = await job.put(mytest, foo=111)
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.put(mytest, foo=222)
        tap.ok(task2, 'Задание отправлено')

        async def _process():
            await job.process()

        async def _stop():
            await asyncio.sleep(0.2)
            await job.stop()

        cfg.set(
            'maintenance.schedule',
            [{'from': time.time() - 15, 'to': time.time() + 60}],
        )
        maintenance.SCHEDULE = None

        result = await asyncio.wait([_process()], timeout=1)
        tap.ok(result, 'обработка запущена')

        tap.eq(PROCESSED, [], 'ничего не выполнилось')

        cfg.set(
            'maintenance.schedule',
            [{'from': time.time() - 15, 'to': time.time() - 10}],
        )
        maintenance.SCHEDULE = None

        result = await asyncio.wait([_process(), _stop()], timeout=1)
        tap.ok(result, 'обработка запущена')

        tap.eq(set(PROCESSED), {111, 222}, 'все выполнилось')
