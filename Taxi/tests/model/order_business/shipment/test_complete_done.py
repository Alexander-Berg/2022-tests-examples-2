# pylint: disable=unused-variable


async def test_done(tap, dataset, now, wait_order_status):
    with tap.plan(16, 'Заказ обработан'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=100)
        stock2 = await dataset.stock(product=product2, store=store, count=200)

        order = await dataset.order(
            store=store,
            type = 'shipment',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10
                },
                {
                    'product_id': product2.product_id,
                    'count': 20
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты получены')

        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 10, 'count')
            tap.eq(suggest.status, 'request', 'status')
            tap.ok(
                await suggest.done('done', count=10),
                'Все нашли'
            )

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 20, 'count')
            tap.eq(suggest.status, 'request', 'status')
            tap.ok(
                await suggest.done('done', count=15),
                'Не все нашли'
            )

        tap.ok(await order.done('complete', user=user), 'Завершаем заказ')

        await wait_order_status(order, ('complete', 'done'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_items(tap, dataset, wait_order_status, now):
    with tap.plan(17, 'Отгрузка посылок'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        item1 = await dataset.item(store=store)
        item2 = await dataset.item(store=store)

        stock1 = await dataset.stock(item=item1, store=store, count=1)
        stock2 = await dataset.stock(item=item2, store=store, count=1)

        order = await dataset.order(
            type='shipment',
            acks=[user.user_id],
            required=[
                {'item_id': item1.item_id, 'count': 1},
                {'item_id': item2.item_id, 'count': 1},
            ],
            store=store,
            approved=now(),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты получены')

        suggests = dict((x.product_id, x) for x in suggests)

        with suggests[item1.item_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 1, 'count')
            tap.eq(suggest.status, 'request', 'status')
            tap.ok(
                await suggest.done('done', count=1),
                'Все нашли'
            )

        with suggests[item2.item_id] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type')
            tap.eq(suggest.count, 1, 'count')
            tap.eq(suggest.status, 'request', 'status')
            tap.ok(
                await suggest.done('done', count=0),
                'Не все нашли'
            )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        with await item1.reload() as item:
            tap.eq(item.status, 'inactive', 'помечен как неактивный')
        with await item2.reload() as item:
            tap.eq(item.status, 'active', 'не изменился')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'отгружен')
            tap.eq(stock.reserve, 0, 'нет резерва')
        with await stock2.reload() as stock:
            tap.eq(stock.count, 1, 'не отгружен')
            tap.eq(stock.reserve, 0, 'нет резерва')
