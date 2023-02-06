import asyncio


async def test_queue_already_exist(tap, queue, uuid):
    with tap.plan(2, 'Повторное создание игнорируется'):
        tap.ok(queue, 'Объект работы с очередями получен')

        tube = f'test-{uuid()}'

        await asyncio.gather(*[queue.create(tube,) for _ in range(8)])

        tap.ok(await queue.delete(tube), 'Очередь удалена')
