async def test_create(tap, queue):
    '''Создаем тестовую очередь'''
    with tap.plan(2):
        tap.ok(await queue.delete('test'), 'Очередь удалена')
        tap.ok(await queue.create('test',), 'Очередь создана')


async def test_attrs(tap, queue):
    '''Атрибуты'''
    with tap.plan(12):
        tap.ok(await queue.purge('test'), 'Очередь очищена')

        task1 = await queue.put(
            'test',
            {'attr1': 'value1', 'attr2': 'value2'},
            foo='bar'
        )
        tap.ok(task1, 'Задание отправлено')

        task2 = await queue.take('test')
        tap.ok(task2, 'Задание получено')
        tap.ok(task2.id, 'Идентификатор задания')
        tap.ok(task2.rid, 'Идентификатор ответа')
        tap.eq(task2.data, {'foo': 'bar'}, 'Данные декодированы')
        tap.ok(task2.host, 'Хост вызова')
        tap.ok(task2.caller, 'Откуда был вызов')
        tap.ok(task2.created, 'Время создания')

        tap.eq(task2.attr1, 'value1', 'Атрибут 1')
        tap.eq(task2.attr2, 'value2', 'Атрибут 2')

        task3 = await queue.ack(task2)
        tap.eq(task3, task2, 'Задание подтверждено выполненным')
