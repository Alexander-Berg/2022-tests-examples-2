from stall.model.stock import Stock


async def test_simple(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'при отмене списываем порции кофе, которые уже сделали'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelves, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
                ('lost', 'lost'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 100),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 10,
                },
            ],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'trash_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'canceled', 'target: canceled')

        stocks_on_demand = await Stock.list_by_order(
            order, shelf_type='kitchen_on_demand',
        )
        tap.eq(len(stocks_on_demand), 0, 'на полке готовой еды нет кофе')

        stocks_trash = await Stock.list_by_shelf(
            shelf_id=shelves['trash'].shelf_id, store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 2, '2 типа кофе есть в треше')
        tap.eq(
            sum(s.count for s in stocks_trash),
            10 + 10,
            'все порции в треше',
        )
        tap.eq(
            sum(s.reserve for s in stocks_trash),
            0,
            'резерва нет',
        )

