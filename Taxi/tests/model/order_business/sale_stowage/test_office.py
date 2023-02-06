from stall.model.shelf import Shelf


async def test_office(dataset, tap, wait_order_status):
    with tap.plan(17, 'Раскладка на полку office'):
        store = await dataset.full_store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product(vars={
            'imported': {
                'nomenclature_type': 'consumable',
            }
        })
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 77,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'sale_stowage', 'тип')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            shelf = await Shelf.load(s.shelf_id)
            tap.eq(shelf.type, 'office', 'тип office')
            tap.eq(s.status, 'request', 'предлагается')
            tap.ok(not s.conditions.need_valid, 'не требуется вводить СГ')
            done = await s.done()
            tap.ok(done, 'завершаем саджест')

        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')

        with stocks.list[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'на полке')
            tap.eq(s.shelf_type, 'office', 'тип')
            tap.eq(s.count, 77, 'количество')
            tap.eq(s.reserve, 0, 'резерв')
