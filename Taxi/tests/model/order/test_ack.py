async def test_ack_other_store(tap, dataset):
    with tap.plan(8, 'Согласие исполнять заказ'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user1 = await dataset.user(store=store)
        tap.ok(user1, 'Пользователь 1 создан')
        tap.eq(user1.store_id, store.store_id, 'на складе')

        order = await dataset.order(status='request')
        tap.ok(order, 'Заказ создан')
        tap.ne(order.store_id, user1.store_id, 'на другом складе')

        revision = order.revision

        tap.ok(not await order.ack(user1), 'Согласие не проходит')
        tap.ok(await order.reload(), 'перезагружен из БД')
        tap.eq(order.revision, revision, 'ревизия не изменилась')




async def test_ack(tap, dataset):
    with tap.plan(14, 'Согласие исполнять заказ'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user1 = await dataset.user(store=store)
        tap.ok(user1, 'Пользователь 1 создан')
        tap.eq(user1.store_id, store.store_id, 'на складе')

        user2 = await dataset.user(store=store)
        tap.ok(user2, 'Пользователь 2 создан')
        tap.eq(user2.store_id, store.store_id, 'на складе')

        order = await dataset.order(status='request', store=store)
        tap.ok(order, 'Заказ создан')
        tap.eq(order.store_id, user1.store_id, 'на том же складе')

        revision = order.revision
        lsn = order.lsn

        tap.ok(await order.ack(user1), 'Согласие 1')
        tap.eq(order.acks, [user1.user_id], 'Согласия')
        tap.eq(order.revision, revision + 1, 'ревизия изменилась')
        tap.ok(order.lsn > lsn, 'lsn вырос')

        tap.ok(await order.ack(user2), 'Согласие 2')
        tap.ok(await order.reload(), 'Заказ переполучен')
        tap.eq(order.acks, sorted([user1.user_id, user2.user_id]), 'Согласия')




async def test_duplicates(tap, dataset):
    with tap.plan(15, 'Повторные согласия игнорируются'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user1 = await dataset.user(store=store)
        tap.ok(user1, 'Пользователь 1 создан')

        order = await dataset.order(status='request', store=store)
        tap.ok(order, 'Заказ создан')

        revision = order.revision
        tap.ok(await order.ack(user1), 'Согласие 1')
        tap.ok(await order.reload(), 'Заказ переполучен')
        tap.eq(order.acks, [user1.user_id], 'Согласия')
        tap.eq(order.revision, revision + 1, 'изменения в БД есть')

        revision = order.revision
        tap.ok(await order.ack(user1), 'Согласие 1')
        tap.ok(await order.reload(), 'Заказ переполучен')
        tap.eq(order.acks, [user1.user_id], 'Согласия')
        tap.eq(order.revision, revision, 'изменений в БД нет')

        revision = order.revision
        order.acks = []
        tap.ok(await order.ack(user1), 'Согласие 1')
        tap.ok(await order.reload(), 'Заказ переполучен')
        tap.eq(order.acks, [user1.user_id], 'Согласия')
        tap.eq(order.revision, revision + 1, 'изменения в БД есть, хотя и нет')




async def test_request_only(tap, dataset):
    with tap.plan(7, 'Согласие актуально только в request'):

        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user1 = await dataset.user(store=store)
        tap.ok(user1, 'Пользователь 1 создан')

        order = await dataset.order(status='processing', store=store)
        revision = order.revision
        tap.ok(order, 'Заказ создан')

        tap.ok(not await order.ack(user1), 'Согласие 1')
        tap.ok(await order.reload(), 'Заказ переполучен')
        tap.eq(order.acks, [], 'Согласия')
        tap.eq(order.revision, revision, 'ревизия не поменялась')


