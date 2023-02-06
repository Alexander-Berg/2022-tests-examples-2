# pylint: disable=global-statement

import asyncio

PROCESSED = []


async def mytest(**kwargs):
    global PROCESSED
    PROCESSED.append(kwargs['foo'])
    return kwargs


async def test_process(tap, job):
    '''С передачей параметров'''
    global PROCESSED

    with tap.plan(4):
        task1 = await job.put(mytest, foo=111)
        tap.ok(task1, 'Задание отправлено')

        task2 = await job.put(mytest, foo=222)
        tap.ok(task2, 'Задание отправлено')

        async def _process():
            await job.process()

        async def _stop():
            await asyncio.sleep(0.2)
            await job.stop()

        result = await asyncio.wait([_process(), _stop()], timeout=1)
        tap.ok(result, 'Все задачи запущены')

        tap.eq(PROCESSED, [111, 222], 'Задачи выполнены')
