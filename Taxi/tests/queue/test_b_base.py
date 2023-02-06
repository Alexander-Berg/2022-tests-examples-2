async def test_create(tap, queue):
    '''Создаем тестовую очередь'''
    with tap.plan(2):
        tap.ok(await queue.delete('test'), 'Очередь удалена')
        tap.ok(await queue.create('test',), 'Очередь создана')


async def test_base(tap, queue):
    '''Базовые функции'''
    with tap.plan(10):
        tap.ok(await queue.purge('test'), 'Очередь очищена')

        task1 = await queue.put('test', foo='bar')
        tap.ok(task1, 'Задание отправлено')

        task2 = await queue.take('test')
        tap.ok(task2, 'Задание получено')
        tap.ok(task2.id, 'Идентификатор задания')
        tap.ok(task2.rid, 'Идентификатор ответа')
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные декодированы')
        tap.ok(task2.host, 'Хост вызова')
        tap.ok(task2.caller, 'Откуда был вызов')

        task3 = await queue.ack(task2)
        tap.eq(task3, task2, 'Задание подтверждено выполненным')

        task4 = await queue.take('test')
        tap.eq(task4, None, 'Заданий больше нет')


async def test_nodata(tap, queue):
    '''Задание без данных'''
    with tap.plan(6):
        tap.ok(await queue.purge('test'), 'Очередь очищена')

        task1 = await queue.put('test')
        tap.ok(task1, 'Задание отправлено')

        task2 = await queue.take('test')
        tap.ok(task2, 'Задание получено')
        tap.eq(task2.data, {}, 'Данные декодированы')

        task3 = await queue.ack(task2)
        tap.eq(task3, task2, 'Задание подтверждено выполненным')

        task4 = await queue.take('test')
        tap.eq(task4, None, 'Заданий больше нет')
