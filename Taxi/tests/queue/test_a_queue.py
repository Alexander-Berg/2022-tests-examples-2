async def test_queue(tap, queue):
    with tap.plan(13):
        tap.ok(queue, 'Объект работы с очередями получен')

        tap.ok(await queue.delete('test'), 'Очередь удалена')
        tap.ok(await queue.create('test',), 'Очередь создана')
        tap.ok(await queue.purge('test'), 'Очередь очищена')

        queues = await queue.list_all()
        tap.ok(len(queues) >= 1, 'Есть очередь')
        tap.in_ok('test', queues, 'Очередь добавлена в словарь')

        q1 = await queue.connect('test')
        tap.ok(q1, 'Очередь подключена')
        tap.eq(q1.name, 'test', 'Имя очереди')
        tap.ok(q1.url, 'Адрес очереди')
        tap.eq(q1.fifo, False, 'fifo')
        tap.ok(q1.ttr, 'ttr')
        tap.ok(q1.max_size > 0, 'max_size')

        tap.ok(await queue.delete('test'), 'Очередь удалена')
