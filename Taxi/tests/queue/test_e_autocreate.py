import uuid


async def test_autocreate(tap, queue):
    '''Автосоздание очереди'''
    with tap.plan(4):
        name = uuid.uuid4().hex

        task1 = await queue.put(name, foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await queue.take(name)
        tap.ok(task2, 'Задание получено')

        task3 = await queue.ack(task2)
        tap.eq(task3, task2, 'Задание подтверждено выполненным')

        task4 = await queue.take(name)
        tap.eq(task4, None, 'Заданий больше нет')
