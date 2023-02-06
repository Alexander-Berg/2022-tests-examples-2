from stall.model.order import Order


async def test_repacking(tap, api, dataset, uuid, wait_order_status):
    with tap.plan(26, 'создание ордера перефасовка'):

        store = await dataset.full_store()

        user = await dataset.user(store=store, role='admin')
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(
            store_id=store.store_id,
            type='repacking',
        )
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        stock = await dataset.stock(shelf_id=shelf.shelf_id)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_repacking',
            json={
                'external_id': external_id,
                'repacking':
                    {
                        'shelf_id': stock.shelf_id,
                        'product_id': stock.product_id,
                    }
            })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'repacking')
        t.json_is('order.status', 'reserving')
        t.json_is('order.estatus', 'begin')
        t.json_is('order.products', [stock.product_id])

        order = await Order.load((user.store_id, external_id), by='external')
        tap.ok(order, 'заказ найден')
        t.json_is('order.order_id', order.order_id)
        order.acks = [user.user_id]
        await order.save()

        tap.eq(len(order.required), 1, 'количество в required')

        with order.required[0] as r:
            tap.eq(r.product_id, stock.product_id, 'product_id')
            tap.eq(r.shelf_id, shelf.shelf_id, 'shelf_id')

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggest = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggest), 1, '1 саджест shelf2box')
        await suggest[0].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 2ой саджест')
        await suggests[0].done()

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 3ий саджест')
        await suggests[0].done(count=3)

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order, status='request')

        tap.eq(len(suggests), 1, 'появился 4ый саджест')
        await suggests[0].done()

        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_repacking_low_count(tap, api, dataset, uuid):
    with tap.plan(7, 'создание перефасовки с малым количеством товара'):

        store = await dataset.store()

        user = await dataset.user(store=store, role='admin')
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(
            store_id=store.store_id,
            type='repacking',
        )
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        stock = await dataset.stock(
            shelf_id=shelf.shelf_id,
            count=1,
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_repacking',
            json={
                'external_id': external_id,
                'repacking':
                    {
                        'shelf_id': stock.shelf_id,
                        'product_id': stock.product_id,
                    }
            })

        t.status_is(410, diag=True)
        t.json_is('code', 'ER_COUNT_OR_RESERVE')
        t.json_is('message', 'Too low product or has reserved')
