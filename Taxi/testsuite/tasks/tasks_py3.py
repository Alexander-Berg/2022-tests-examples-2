import asyncio


async def setup_worker():
    print('WORKER - setup')


async def stq_sample_task_done(log_extra=None):
    print('WORKER - sample task done')


async def stq_sample_task_failed(log_extra=None):
    print('WORKER - sample task failed')
    raise RuntimeError


async def stq_sample_task_infinite(log_extra=None):
    print('WORKER - sample task failed')
    while True:
        await asyncio.sleep(1)
