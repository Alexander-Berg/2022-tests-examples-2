async def test_add_parent(tap, dataset, wait_order_status):
    with tap.plan(3, 'Добавился родитель во время инвы'):
        store = await dataset.store(estatus='inventory')
        random_order = await dataset.order(store=store)
        inv_order = await dataset.order(
            type='inventory',
            status='processing',
            estatus='waiting_signal',
            store=store,
        )
        check_order = await dataset.order(
            type='inventory_check_product_on_shelf',
            status='complete',
            estatus='begin',
            store=store,
            parent=[random_order.order_id],
        )
        tap.ok(
            await wait_order_status(check_order, ('complete', 'done')),
            'Докатили до конца документ'
        )
        tap.eq(
            check_order.parent,
            [random_order.order_id, inv_order.order_id],
            'Родитель появился в конце цепочки'
        )


async def test_remove_parent(tap, dataset, wait_order_status):
    with tap.plan(3, 'Удалили родителя инвентаризацию'):
        store = await dataset.store(estatus='processing')
        random_order_1 = await dataset.order(store=store)
        random_order_2 = await dataset.order(store=store)
        inv_order = await dataset.order(
            type='inventory',
            status='complete',
            estatus='done',
            store=store,
        )
        check_order = await dataset.order(
            type='inventory_check_product_on_shelf',
            status='complete',
            estatus='begin',
            store=store,
            parent=[
                random_order_1.order_id,
                inv_order.order_id,
                random_order_2.order_id,
            ]
        )
        tap.ok(
            await wait_order_status(check_order, ('complete', 'done')),
            'Докатили до конца документ'
        )
        tap.eq(
            check_order.parent,
            [random_order_1.order_id, random_order_2.order_id],
            'Родитель удален, порядок остался'
        )


async def test_already_have_parent(tap, dataset, wait_order_status):
    with tap.plan(3, 'Не добавится новый, т.к. уже все есть'):
        store = await dataset.store(estatus='inventory')
        inv_order = await dataset.order(
            type='inventory',
            status='processing',
            estatus='waiting_signal',
            store=store,
        )
        check_order = await dataset.order(
            type='inventory_check_product_on_shelf',
            status='complete',
            estatus='begin',
            store=store,
            parent=[inv_order.order_id],
        )
        tap.ok(
            await wait_order_status(check_order, ('complete', 'done')),
            'Докатили до конца документ'
        )
        tap.eq(
            check_order.parent,
            [inv_order.order_id],
            'Родитель тот же, ничего не поменялось'
        )
