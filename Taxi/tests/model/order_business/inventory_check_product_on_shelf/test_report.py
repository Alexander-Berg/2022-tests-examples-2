async def test_inventory(tap, dataset, wait_order_status):
    with tap.plan(20, 'отчет в контрольке'):
        store = await dataset.full_store(estatus='inventory')
        user = await dataset.user(store=store)
        stock = await dataset.stock(store=store, count=4)
        stock2 = await dataset.stock(
            store=store,
            shelf_id=stock.shelf_id,
            count=3
        )
        await dataset.assortment_contractor_product(
            store=store,
            product_id=stock.product_id,
            price=72.72
        )

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[{'shelf_id': stock.shelf_id}],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на полку')

        with suggests[0] as suggest:

            tap.eq(suggest.shelf_id, stock.shelf_id, 'полка')
            tap.ok(
                await suggest.done(
                    product_id=stock.product_id,
                    count=8
                ),
                'саджест закрыт'
            )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order, status='request')
        tap.eq(len(suggests), 1, 'ещё один саджест на полку')
        suggest = suggests[0]
        tap.ok(
            await suggest.done(status='error'),
            'работу с саджестами завершаем'
        )

        await wait_order_status(
            order,
            ('complete', 'wait_child_done'),
            user_done=user
        )

        child = await dataset.Order.load(order.vars('child_order_id'))
        tap.ok(child, 'дочерний ордер создан')
        tap.eq(child.type, 'inventory_check_product_on_shelf', 'тип ордера')
        tap.eq(child.store_id, order.store_id, 'на складе')
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'ack')
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child)
        for s in suggests:
            tap.ok(await s.done(count=20), f'завершаем саджест {s.type}')
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        tap.eq(
            child.vars('report', None),
            {
                stock.shelf_id:
                    {
                        stock.product_id: {
                            'count': 4,
                            'price': '72.72',
                            'result_count': 20,
                            'quants': 1,
                        },
                        stock2.product_id: {
                            'count': 3,
                            'result_count': 20,
                            'quants': 1,
                        }
                    }
            },
            'Отчет нужного вида'
        )


async def test_kitchen(tap, dataset, wait_order_status):
    with tap.plan(7, 'отчет в контрольке с кухней'):
        store = await dataset.full_store(estatus='inventory')
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store, type='kitchen_components')
        shelf2 = await dataset.shelf(store=store, type='kitchen_components')
        product = await dataset.product(quants=99)
        stock = await dataset.stock(
            store=store,
            count=4,
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
        )
        await dataset.assortment_contractor_product(
            store=store,
            product_id=stock.product_id,
            price=72.72
        )

        order = await dataset.order(
            type='inventory_check_product_on_shelf',
            store=store,
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                    'count': 10,
                },
                {
                    'shelf_id': shelf2.shelf_id,
                    'product_id': product.product_id,
                    'count': 9,
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        for suggest in suggests:
            tap.ok(await suggest.done(), 'саджест закрыт')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user
        )

        tap.eq(
            order.vars('report', None),
            {
                shelf.shelf_id: {
                    product.product_id: {
                        'count': 4,
                        'price': '72.72',
                        'result_count': 10,
                        'quants': 99,
                    },
                },
                shelf2.shelf_id: {
                    product.product_id: {
                        'count': 0,
                        'price': '72.72',
                        'result_count': 9,
                        'quants': 99,
                    },
                },
            },
            'Отчет нужного вида'
        )
