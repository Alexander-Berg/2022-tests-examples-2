# pylint: disable=unused-variable


async def test_items(tap, dataset, now, wait_order_status):
    with tap.plan(19, 'Генерация саджестов для item'):

        product = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        item = await dataset.item(store=store)
        stock_item = await dataset.stock(store=store, item=item, count=1)

        stock = await dataset.stock(product=product, store=store, count=100)

        order = await dataset.order(
            store=store,
            type = 'shipment',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product.product_id,
                    'count': 10,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('approving', 'begin'))

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 0, 'Проблем нет')

        with await stock.reload() as stock:
            tap.eq(stock.count, 100, 'count')
            tap.eq(stock.reserve, 10, 'reserve')

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'Два резерва')

        suggests = {
            s.shelf_id: s for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests.keys()), 2, 'Два саджеста')

        tap.in_ok(stock_item.shelf_id, suggests, 'саджест по полке посылок')
        tap.in_ok(stock.shelf_id, suggests, 'саджест по полке обычной')

        with suggests[stock_item.shelf_id] as s:
            tap.eq(s.product_id, stock_item.product_id, 'экземпляр')
            tap.eq(s.count, 1, 'количество')
            tap.eq(s.vars('mode'), 'item', 'режим работы саджеста')
            tap.eq(s.conditions.all, True, 'conditions.all')
            tap.eq(s.conditions.max_count, True, 'conditions.max_count')
            tap.eq(s.conditions.editable, False, 'conditions.editable')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
