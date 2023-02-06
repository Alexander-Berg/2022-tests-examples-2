async def test_store_lock(tap, dataset, wait_order_status):
    with tap.plan(26, 'Проверяем блокировку склада'):
        store = await dataset.store(estatus='inventory')
        user = await dataset.user(store=store)
        await dataset.shelf(store=store, type='lost')
        await dataset.shelf(store=store, type='found')
        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'shelf_types': ['store']}
        )
        stock = await dataset.stock(store=store, count=11)
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(
            len(order.vars('child_orders')),
            1,
            'один дочерний ордер создан'
        )

        child = await dataset.Order.load(order.vars('child_orders.0'))
        tap.ok(child, 'дочерний ордер загружен')
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(
                product_id=stock.product_id,
                count=11
            ),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('complete', 'done'),
            user_done=user
        )
        await wait_order_status(order, ('processing', 'waiting_signal'))
        tap.ok(
            await order.signal({'type': 'inventory_done'}),
            'сигнал инвы'
        )
        child_check = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            status='reserving',
            estatus='begin',
            parent=[order.order_id]
        )
        await wait_order_status(order, ('processing', 'lock_store'))
        await wait_order_status(order, ('processing', 'waiting_signal'))
        tap.ok(await store.reload(), 'Склад перезабрали')
        tap.eq(store.estatus, 'inventory', 'Режим инвы остался')
        child_check.status = 'complete'
        child_check.estatus = 'done'
        tap.ok(await child_check.save(), 'Закрыли дочерний документ')
        tap.ok(
            await order.signal({'type': 'inventory_done'}),
            'сигнал инвы второй'
        )
        await wait_order_status(order, ('processing', 'snapshot'))
        tap.ok(await store.reload(), 'Склад перезабрали')
        tap.eq(store.estatus, 'inventory_locked', 'Режим инвы изменился')
        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await store.reload(), 'Склад перезабрали')
        tap.eq(store.estatus, 'inventory', 'Режим инвы вернулся')
