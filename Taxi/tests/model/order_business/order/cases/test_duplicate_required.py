# pylint: disable=too-many-statements,too-many-locals

from stall.model.stock import Stock


async def test_required_duplicate(tap, dataset, now, wait_order_status):
    with tap.plan(9, 'Повторяющиеся требования'):

        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        shelf_store = await dataset.shelf(store=store, type='store')
        shelf_md    = await dataset.shelf(store=store, type='markdown')

        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf_store,
            count=100,
        )
        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf_md,
            count=100,
        )
        await dataset.stock(product=product2, store=store, count=200)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 10,
                    'price': 100,
                },
                {
                    'product_id': product2.product_id,
                    'count': 20,
                    'price': 200,
                },
                {
                    'product_id': product1.product_id,
                    'count': 11,
                    'price': 110,
                },
                {
                    'product_id': product1.product_id,
                    'count': 16,
                    'price': 11.11,
                    'price_type': 'markdown',
                },

            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        stocks = await Stock.list_by_order(order)
        stocks = dict(((x.product_id, x.shelf_type), x) for x in stocks)
        tap.eq(len(stocks), 3, 'Остатки')

        with stocks[(product1.product_id, 'store')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 10 + 11, 'Зарезервировано')

        with stocks[(product1.product_id, 'markdown')] as stock:
            tap.eq(stock.count, 100, 'Остаток')
            tap.eq(stock.reserve, 16, 'Зарезервировано')

        with stocks[(product2.product_id, 'store')] as stock:
            tap.eq(stock.count, 200, 'Остаток')
            tap.eq(stock.reserve, 20, 'Зарезервировано')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
