async def test_create(tap, queue):
    '''Создаем тестовую очередь'''
    with tap.plan(2):
        tap.ok(await queue.delete('test.fifo'), 'Очередь удалена')
        tap.ok(await queue.create('test.fifo',), 'Очередь создана')


async def test_group(tap, queue):
    '''Работа с FIFO очередью'''
    with tap.plan(11):
        tap.ok(await queue.purge('test.fifo'), 'Очередь очищена')

        task1 = await queue.put(
            'test.fifo',
            {'group': '12345', 'dupl': '98765'},
            foo='bar'
        )
        tap.ok(task1, 'Задание отправлено: %s' % task1.id)

        task2 = await queue.put(
            'test.fifo',
            {'group': '12345', 'dupl': '654321'},
            foo='baz'
        )
        tap.ok(task2, 'Задание отправлено: %s' % task2.id)

        task3 = await queue.take('test.fifo')
        tap.ok(task3, 'Задание получено: %s' % task3.id)
        tap.eq(task3.group, '12345', 'group')
        tap.eq(task3.dupl, '98765', 'dupl')

        task4_1 = await queue.take('test.fifo')
        tap.eq(task4_1, None, 'Параллельно задание не взять')

        task4_2 = await queue.take('test.fifo')
        tap.eq(task4_2, None, 'Параллельно задание все равно не взять')

        task5 = await queue.ack(task3)
        tap.eq(task5, task3, 'Задание подтверждено выполненным: %s' % task5.id)

        task6 = await queue.take('test.fifo')
        tap.ok(task6, 'Задание получено: %s' % task6.id)

        task7 = await queue.ack(task6)
        tap.eq(task7, task6, 'Задание подтверждено выполненным: %s' % task7.id)


async def test_auto_group_id(tap, queue):
    '''Автоматическое проставление атрибутов для .fifo очередей'''
    with tap.plan(5):
        tap.ok(await queue.purge('test.fifo'), 'Очередь очищена')

        task1 = await queue.put('test.fifo', foo='bar')
        tap.ok(task1, 'Задание отправлено: %s' % task1.id)

        task2 = await queue.take('test.fifo')
        tap.ok(task2, 'Задание получено')
        tap.ok(len(task2.group) > 0, 'group')
        tap.ok(len(task2.dupl) > 0, 'dupl')
