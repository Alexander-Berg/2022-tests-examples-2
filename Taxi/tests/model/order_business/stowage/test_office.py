from stall.model.shelf import Shelf


async def test_office(dataset, tap, wait_order_status):
    with tap.plan(23, 'Раскладка на полку office'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf = await dataset.shelf(type='office', store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.type, 'office', 'тип офис')

        order = await dataset.order(
            type='stowage',
            acks=[user.user_id],
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 34,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'stowage', 'тип')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.ne(s.shelf_id, shelf.shelf_id, 'саджест НЕ на полку office')
            tap.eq(s.status, 'request', 'предлагается')
            done = await s.done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': shelf.shelf_id,
                }
            )
            tap.ok(done, 'саджест закрыт с указанием на office')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'саджест на полку office')
            tap.eq(s.status, 'request', 'предлагается')
            tap.ok(not s.conditions.need_valid, 'не требуется вводить СГ')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')

        with stocks.list[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'на полке')
            tap.eq(s.shelf_type, 'office', 'тип')
            tap.eq(s.count, 34, 'количество')
            tap.eq(s.reserve, 0, 'резерв')


async def test_office_exp(dataset, tap, wait_order_status):
    with tap.plan(22, 'Раскладка на полку officeпод экспериментом'):
        store = await dataset.full_store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        shelf_store = await dataset.shelf(store=store)

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='stowage',
            acks=[user.user_id],
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 34,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'stowage', 'тип')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            shelf = await Shelf.load(s.shelf_id)
            tap.eq(shelf.type, 'office', 'тип office')
            tap.eq(s.status, 'request', 'предлагается')
            tap.ok(not s.conditions.need_valid, 'не требуется вводить СГ')
            done = await s.done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': shelf_store.shelf_id,
                }
            )
            tap.ok(done, 'саджест закрыт с указанием на store')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.ne(
                s.shelf_id,
                shelf_store.shelf_id,
                'саджест НЕ на полку store'
            )
            tap.eq(s.status, 'request', 'предлагается')
            done = await s.done()
            tap.ok(done, 'завершаем саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')

        with stocks.list[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'на полке')
            tap.eq(s.shelf_type, 'office', 'тип')
            tap.eq(s.count, 34, 'количество')
            tap.eq(s.reserve, 0, 'резерв')


async def test_office_fail(dataset, tap, wait_order_status):
    with tap.plan(22, 'Раскладка на полку office'):
        store = await dataset.full_store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product(vars={
            'imported': {
                'nomenclature_type': 'product',
                }
        })
        tap.ok(product, 'товар создан')

        shelf = await dataset.shelf(type='office', store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.type, 'office', 'тип офис')

        order = await dataset.order(
            type='stowage',
            acks=[user.user_id],
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 34,
                    'valid': '2011-01-02',
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'stowage', 'тип')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.ne(s.shelf_id, shelf.shelf_id, 'саджест НЕ на полку office')
            tap.eq(s.status, 'request', 'предлагается')
            done = await s.done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': shelf.shelf_id,
                }
            )
            tap.ok(done, 'саджест закрыт с указанием на office')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.ne(s.shelf_id, shelf.shelf_id, 'саджест НЕ на полку office')
            tap.eq(s.status, 'request', 'предлагается')

        await wait_order_status(order, ('processing', 'waiting'))

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')

        with stocks.list[0] as s:
            tap.ne(s.shelf_type, 'office', 'тип не office')
            tap.eq(s.count, 34, 'количество')
            tap.eq(s.reserve, 0, 'резерв')
