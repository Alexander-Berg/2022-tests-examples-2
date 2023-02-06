async def test_prolong(tap, queue, uuid):
    with tap.plan(9, 'Проверка пролонгации'):
        queue_name = uuid()
        tap.ok(await queue.delete(queue_name), 'Очередь удалена')
        tap.ok(await queue.create(queue_name), 'Очередь создана')
        tap.ok(await queue.purge(queue_name), 'Очередь очищена')

        task = await queue.put(queue_name, {'message': 'success'})
        tap.ok(task, 'Задачу сделали')

        task = await queue.take(queue_name)
        tap.ok(task, 'Получили задачу')

        prolong = await queue.prolong(task, delay=12)
        tap.ok(prolong, 'Пролонгировали')

        ack = await queue.ack(task)
        tap.ok(ack, 'Удалили сообщение')

        prolong = await queue.prolong(task, delay=12)
        tap.is_ok(prolong, None, 'Пролонгация удаленного сообщения')

        tap.ok(await queue.delete(queue_name), 'Очередь удалена')
