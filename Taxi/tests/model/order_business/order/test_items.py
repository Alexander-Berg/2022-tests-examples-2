import pytest


@pytest.mark.parametrize('editable', [False, True])
async def test_items(tap, dataset, now, wait_order_status, editable):
    # pylint: disable=too-many-locals
    with tap.plan(25, 'Работа ордера с посылками'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product(
            vars={'imported': {'netto_weight': 123}})
        tap.ok(product, 'Продукт')

        stock = await dataset.stock(
            store=store, product_id=product.product_id)
        tap.eq(stock.store_id, store.store_id, 'остаток')

        item = await dataset.item(store=store, data={'weight': 321})
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        stock_item = await dataset.stock(store=store,
                                         product_id=item.item_id,
                                         shelf_type='parcel',
                                         count=1)
        tap.eq(stock_item.store_id, store.store_id, 'остаток экземпляра')
        tap.eq(stock_item.shelf_type, 'parcel', 'тип полки')

        order = await dataset.order(
            type='order',
            store=store,
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                }
            ],
            editable=True,
            vars={
                'editable': editable,
            }
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        if not await wait_order_status(order, ('processing', 'waiting')):
            for p in order.problems:
                tap.diag(f'{p.type}: {p.pure_python()}')
        tap.eq(order.vars('total_order_weight', 0), 567, 'Вес посчитали')

        stocks = await dataset.Stock.list_by_order(order, shelf_type='parcel')
        tap.eq(len(stocks), 1, 'один остаток на ордер')
        with stocks[0] as s:
            tap.eq(s.shelf_type, 'parcel', 'тип полки в остатке')
            tap.eq(s.product_id, item.item_id, 'product_id')
            tap.eq(s.reserve, 1, 'зарезервирован')


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

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        with stocks[0] as s:
            tap.ok(await s.reload(), 'перегружен сток')
            tap.eq(s.count, 0, 'на складе нет')

        tap.ok(await item.reload(), 'перегружен экземпляр')
        tap.eq(item.status, 'inactive', 'статус ему проставлен неактивный')

