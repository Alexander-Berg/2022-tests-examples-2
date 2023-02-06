# pylint: disable=global-statement
import asyncio

from stall.model.stash import Stash
from stall.job import Job


async def sleep_task(delay: int, stash_name: str):
    await asyncio.sleep(delay)
    stash = await Stash.load(stash_name, by='name')
    stash.rehashed(value=True)
    await stash.save()


async def test_prolong(tap, cfg, uuid):
    with tap.plan(6, 'Проверяем пролонгацию'):
        tube_name = f'tube-{uuid()}'
        stash_name = f'test-stash-{uuid()}'

        stash = await Stash.stash(name=stash_name)
        tap.ok(stash, 'stash создан')

        cfg.set('prolong_sqs', 'yes')
        cfg.set('queue.prolong_retries', 10)

        job_instances = [Job(name=tube_name), Job(name=tube_name)]
        job = job_instances[0]

        tube = await job.queue.create(tube_name, ttr='2')
        tap.ok(tube, 'Очередь создали')
        timeout = 5

        task = await job.put(
            sleep_task, delay=3, stash_name=stash_name, tube=tube_name)
        tap.ok(task, 'Задание отправлено')

        workers = [
            asyncio.create_task(instance.process(tube=tube_name))
            for instance in job_instances
        ]
        tap.ok(all(workers), 'Создали двух воркеров')
        await asyncio.sleep(timeout)
        await asyncio.wait(
            [job.stop() for job in job_instances]
        )
        old_revision = stash.revision
        tap.ok(await stash.reload(), 'Перезабрали стэш')
        tap.eq(
            stash.revision - old_revision,
            1,
            'Потрогали его только однажды'
        )
