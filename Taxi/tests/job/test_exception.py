# pylint: disable=global-statement

import asyncio
from stall.job import ErrorJobRetryDelay

PROCESSED = []
RETRY = True


async def mytest(**kwargs):
    global PROCESSED
    PROCESSED.append(kwargs['foo'])
    raise RuntimeError('Тест')


async def error_job_retry(**kw):
    global PROCESSED, RETRY
    PROCESSED.append(kw['foo'])
    if RETRY:
        RETRY = False
        raise ErrorJobRetryDelay(delay=kw.get('delay'))
    return


async def test_process(tap, job):
    '''Возврат упавшей таски'''
    global PROCESSED
    PROCESSED = []

    with tap.plan(6):
        task = await job.put(mytest, foo=111)
        tap.ok(task, 'Задание отправлено')

        queue = job.queue.queues[job.name]

        queue.delay_error = [1]
        tap.eq(queue.delay_error, [1],
               f'Возвращаем таску через {queue.delay_error[0]} сек')

        await asyncio.wait([job.process()], timeout=0.5)

        tap.ok(PROCESSED, 'Задача выполнялась')

        PROCESSED = []
        await asyncio.sleep(0.4)

        tap.ok(not PROCESSED, 'Задача ожидает повтора')

        await asyncio.sleep(0.5)

        tap.ok(PROCESSED, 'Задача выполнялась')

        PROCESSED = []
        await asyncio.sleep(0.4)

        tap.ok(not PROCESSED, 'Задача ожидает повтора')

        await asyncio.wait([job.stop()], timeout=0.5)
        await asyncio.sleep(0.6)


async def test_process_bad_task(tap, job):
    '''Не возвращаем таску неправильного формата'''
    global PROCESSED
    PROCESSED = []

    with tap.plan(6):
        task = await job.queue.put(job.name, None, aaa=111)
        tap.ok(task, 'Задание отправлено')

        queue = job.queue.queues[job.name]

        queue.delay_error = [1]
        tap.eq(queue.delay_error, [1],
               f'Возвращаем таску через {queue.delay_error[0]} сек')

        await asyncio.wait([job.process()], timeout=0.5)

        tap.ok(not PROCESSED, 'Задача не выполнялась')

        await asyncio.sleep(0.5)

        tap.ok(not PROCESSED, 'Задача не выполнялась')

        await asyncio.sleep(0.4)

        tap.ok(not PROCESSED, 'Задача ожидает повтора')

        tap.ok(not await job.queue.take(job.name), 'Заданий нет')

        await asyncio.wait([job.stop()], timeout=0.5)
        await asyncio.sleep(0.6)


async def test_retry_delay(tap, job):
    global PROCESSED
    PROCESSED = []

    with tap.plan(4, 'Повторяем задачу при ошибке retry'):
        await job.put(error_job_retry, foo=111, delay=2)

        await asyncio.wait([job.process()], timeout=0.5)

        tap.ok(PROCESSED, 'Задача выполнялась')

        PROCESSED = []
        await asyncio.sleep(0.5)

        tap.ok(not PROCESSED, 'Задача ожидает повтора')

        await asyncio.sleep(2)

        tap.ok(PROCESSED, 'Задача выполнялась')

        PROCESSED = []
        await asyncio.sleep(3)

        tap.ok(not PROCESSED, 'Задача не выполнялась')

        await asyncio.wait([job.stop()], timeout=0.5)
        await asyncio.sleep(0.6)
