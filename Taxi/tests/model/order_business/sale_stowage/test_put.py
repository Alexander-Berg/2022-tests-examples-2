# pylint: disable=too-many-statements
import asyncio


async def test_put(tap, dataset, wait_order_status):
    with tap.plan(51, 'Зачисление на склад'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            type='sale_stowage',
            store=store,
            acks=[user.user_id],
            status='reserving',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 45,
                    'valid': '2018-01-03',
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.valid.strftime('%F'), '2018-01-03', 'valid')
            tap.eq(s.count, 45, 'count')
            tap.eq(s.product_id, product.product_id, 'product_id')

            tap.ok(await s.done(count=5), 'закрыли')

        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))
        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'один остаток')
        with stocks.list[0] as s:
            tap.eq(s.count, 5, 'зачислено')
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.shelf_type, 'store', 'тип полки')

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.count, 40, 'count')
            tap.ok(await s.done(count=7), 'закрыли')

        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))
        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 2, 'Два остатка (закрывали два раза)')
        for s in stocks:
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.shelf_type, 'store', 'тип полки')
            tap.ok(s.lot.startswith(f'{order.order_id}-'), 'lot')

        tap.eq(sum(s.count for s in stocks), 5 + 7, 'зачислено')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка сгенерирована')

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.count, 33, 'count')
            tap.ok(
                await s.done(
                    status='error',
                    reason={'code': 'LIKE_SHELF', 'shelf_id': shelf.shelf_id},
                ),
                'закрыли в ошибку'
            )
        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.shelf_id, shelf.shelf_id, 'На другую полку')
            tap.eq(s.count, 33, 'count')
            tap.eq(s.product_id, product.product_id, 'product_id')

            tap.ok(await s.done(count=11), 'закрыли')

        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 3, 'Ещё остаток')
        with next(s for s in stocks if s.shelf_id == shelf.shelf_id) as s:
            tap.eq(s.count, 11, 'зачислено')
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.shelf_type, 'store', 'тип полки')
            tap.ok(s.lot.startswith(f'{order.order_id}-'), 'lot')


async def test_disabled_shelf(tap, dataset, wait_order_status):
    with tap:
        store = await dataset.store()
        await asyncio.gather(*[
            dataset.shelf(store_id=store.store_id, type=shelf_type)
            for shelf_type in ['trash', 'lost', 'found']
        ])
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf_1 = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf_1, 'полка для товара создана')

        shelf_2 = await dataset.shelf(store_id=store.store_id,
                                      status='disabled')
        tap.ok(shelf_2, 'отключенная полка создана')
        stock_2 = await dataset.stock(product=product, shelf=shelf_2)
        tap.ok(stock_2, 'остаток на полке создан')

        order = await dataset.order(
            type='sale_stowage',
            store=store,
            acks=[user.user_id],
            status='reserving',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'valid': '2018-01-03',
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.count, 1, 'count')
            tap.ok(await s.done(count=1), 'закрыли')

        # генерирует новый саджест
        await wait_order_status(order, ('processing', 'waiting'))
        # записывает товар на полку
        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'остатки')

        # created stock
        with next(
                stock
                for stock in stocks
                if stock.stock_id != stock_2.stock_id
        ) as s:
            tap.eq(s.count, 1, 'зачислено')
            tap.eq(s.product_id, product.product_id, 'товар')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.shelf_type, 'store', 'тип полки')
            tap.eq(s.shelf_id, shelf_1.shelf_id, 'выбрана пустая полка')
