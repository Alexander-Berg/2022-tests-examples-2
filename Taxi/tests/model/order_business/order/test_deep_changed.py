async def clean_order_events(dataset, order):
    events = await dataset.EventCache.list(
        tbl='orders',
        pk=order.order_id,
        by='object',
        db={'shard': order.shardno},
        full=True)
    for e in events:
        await e.rm()


async def test_deep_changed(tap, dataset, cfg, now):
    with tap.plan(11, 'Склеивание обработчиков в одном job'):
        cfg.set('business.order_changed.deep', 1000)
        cfg.set('business.order_changed.timeout', 1000)

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 1,
                }
            ],
            approved=now(),
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'начало')
        await clean_order_events(dataset, order)

        tap.ok(await dataset.Order.job_save(order_id=order.order_id),
               'вызвали changed')

        tap.ok(await order.reload(), 'перегружен ордер')
        tap.eq(order.fstatus,
               ('processing', 'waiting'),
               'Статус доскакал аж до ожидания')

        events = await dataset.EventCache.list(
            tbl='orders',
            pk=order.order_id,
            by='object',
            db={'shard': order.shardno},
            full=True)

        job_events = []

        for ea in events:
            for e in ea.events:
                if e['type'] == 'queue':
                    job_events.append(e)

        tap.eq(len(job_events), 1, 'только одно событие в кеше на job')

        logs = (await dataset.OrderLog.list_by_order(order)).list
        tap.ok(logs, 'Логи заказа получены')
        tap.ok(logs[-1].delay, 'Время выполнения сохранено')


async def test_deep_changed_timeout(tap, dataset, cfg, now):
    with tap.plan(9, 'Склеивание обработчиков в одном job'):
        cfg.set('business.order_changed.deep', 1000)
        cfg.set('business.order_changed.timeout', 0)

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 1,
                }
            ],
            approved=now(),
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'начало')
        await clean_order_events(dataset, order)

        tap.ok(await dataset.Order.job_save(order_id=order.order_id),
               'вызвали changed')

        tap.ok(await order.reload(), 'перегружен ордер')
        tap.ne(order.fstatus,
               ('processing', 'waiting'),
               'Статус не смог дойти до processing')

        events = await dataset.EventCache.list(
            tbl='orders',
            pk=order.order_id,
            by='object',
            db={'shard': order.shardno},
            full=True)

        job_events = []

        for ea in events:
            for e in ea.events:
                if e['type'] == 'queue':
                    job_events.append(e)

        tap.eq(len(job_events), 1, 'только одно событие в кеше на job')
