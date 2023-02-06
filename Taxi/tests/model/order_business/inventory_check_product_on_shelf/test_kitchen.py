import pytest


@pytest.mark.parametrize(
    'desc',
    [
        {
            'desc': 'нет коррекции склада',
            'count': 10,
            'done_count': 10,
            'found_count': 0,
            'lost_count': 0,
        },

        {
            'desc': 'Уменьшение',
            'count': 10,
            'done_count': 1,
            'found_count': 0,
            'lost_count': 9,
        },

        {
            'desc': 'Уменьшение в ноль',
            'count': 16,
            'done_count': 0,
            'found_count': 0,
            'lost_count': 16,
        },

        {
            'desc': 'Увеличение',
            'count': 10,
            'done_count': 123,
            'found_count': 113,
            'lost_count': 0,
        },
    ]
)
async def test_kitchen(tap, dataset, wait_order_status, desc):
    # pylint: disable=too-many-locals
    with tap.plan(20, desc['desc']):
        store = await dataset.full_store(estatus='inventory')
        tap.ok(store, 'склад создан')
        tap.eq(store.estatus, 'inventory', 'в режиме инвентаризации')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product(quants=15)
        tap.eq(product.quants, 15, 'товар с квантами создан')

        shelf = await dataset.shelf(store=store, type='kitchen_components')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        stock = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=desc['count'],
        )
        tap.eq(stock.store_id, store.store_id, 'остаток на компонентах')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'полка')
        tap.eq(stock.product_id, product.product_id, 'товар')
        tap.eq(stock.count, desc['count'], 'количество')

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            acks=[user.user_id],
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')

        with suggests[0] as s:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.ok(await s.done(count=desc['done_count']), 'закрыт саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('product_id', product.product_id)
            ),
            sort=(),
        )

        tap.eq({s.product_id for s in stocks},
               {product.product_id},
               'все остатки про товар')
        tap.eq(
            sum(s.left for s in stocks if s.shelf_type == shelf.type),
            desc['done_count'],
            'общее количество'
        )
        found_stocks = [
            stock
            for stock in stocks
            if stock.shelf_type == 'kitchen_found'
        ]
        if found_stocks:
            found_count = found_stocks[0].count
        else:
            found_count = 0
        tap.eq(
            found_count,
            desc['found_count'],
            'на полке находок правильные остатки',
        )
        lost_stocks = [
            stock
            for stock in stocks
            if stock.shelf_type == 'kitchen_lost'
        ]
        if lost_stocks:
            lost_count = lost_stocks[0].count
        else:
            lost_count = 0
        tap.eq(
            lost_count,
            desc['lost_count'],
            'на полке потерь правильные остатки',
        )
