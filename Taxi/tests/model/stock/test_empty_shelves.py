from stall.model.stock import job_empty_shelves, process_empty_shelves


async def test_success(tap, dataset, cfg):
    with tap.plan(5, 'Успешное удаление остатков'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='store', store=store)
        await dataset.stock(shelf=shelf_one, count=31)
        stock_two = await dataset.stock(shelf=shelf_two, count=33)

        rows = [{'shelf': shelf_one.title}]

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        await job_empty_shelves(stash.stash_id)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('count', '>', 0)
            ],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (stock_two.product_id, stock_two.shelf_id, stock_two.count),
            },
            'Остатки удалились на нужных полках'
        )

        order = await dataset.Order.load(
            [store.store_id, stash.stash_id], by='external')
        tap.ok(order, 'Документ создан')
        tap.eq(order.type, 'manual_correction', 'Тип документа верный')
        tap.eq(order.user_id, user.user_id, 'Правильный пользователь')

        stash = await dataset.Stash.load(stash.stash_id)
        tap.is_ok(stash, None, 'Нет больше стэша')


async def test_errors(tap, dataset, cfg):
    with tap.plan(6, 'Ошибки сохраняются'):
        store = await dataset.store()
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        stock_one = await dataset.stock(shelf=shelf_one, count=31)

        rows = [{'shelf': shelf_one.title}]

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        await job_empty_shelves(stash.stash_id)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('count', '>', 0)
            ],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (stock_one.product_id, stock_one.shelf_id, stock_one.count),
            },
            'Остатки не удалилсь'
        )

        error_stashes = await dataset.Stash.list(
            by='full',
            conditions=('group', f'error:{stash.stash_id}')
        )
        tap.eq(len(error_stashes.list), 1, 'Одну ошибку прикопали')
        single_error = error_stashes.list[0].value
        tap.eq(single_error['code'], 'ER_GONE', 'Правильный код')
        tap.eq(single_error['value'], store.store_id, 'Правильное значение')
        tap.eq(
            single_error['message'],
            'Store must be in "inventory" mode',
            'Правильное сообщение'
        )

        stash = await dataset.Stash.load(stash.stash_id)
        tap.is_ok(stash, None, 'Нет больше стэша')


async def test_no_stash(tap, dataset, cfg, uuid):
    with tap.plan(2, 'Нет стэша для импорта'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        shelf_one = await dataset.shelf(type='store', store=store)
        stock_one = await dataset.stock(shelf=shelf_one, count=31)

        await job_empty_shelves(uuid())

        tap.ok(await stock_one.reload(), 'Остаток перезабрали')
        tap.eq(stock_one.count, 31, 'Остаток остался')


async def test_not_shelf(tap, dataset, cfg):
    with tap.plan(6, 'Кривые полки в удалении'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(
            type='store',
            store=store,
            status='removed'
        )
        stock_one = await dataset.stock(shelf=shelf_one, count=31)

        rows = [
            {'shelf': shelf_one.title},
            {'shelf': 'горностайский сухолимб'},
            {'shelf': shelf_two.title},
        ]

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_empty_shelves(stash)

        tap.eq(len(errors), 2, 'Две ошибки')
        tap.eq(
            {item.code for item in errors},
            {'ER_NOT_FOUND'},
            'Код ошибки верный'
        )
        tap.eq(
            {item.value for item in errors},
            {'горностайский сухолимб', shelf_two.title},
            'Значения те')

        order = await dataset.Order.load(
            [store.store_id, stash.stash_id], by='external')
        tap.ok(order is None, 'Документ не создан')
        tap.ok(await stock_one.reload(), 'Остаток перезабрали')
        tap.eq(stock_one.count, 31, 'Остаток остался')


async def test_idempotency(tap, dataset, cfg):
    with tap.plan(3, 'Успешное удаление остатков идемпотентность'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='store', store=store)
        await dataset.stock(shelf=shelf_one, count=31)
        stock_two = await dataset.stock(shelf=shelf_two, count=33)

        rows = [{'shelf': shelf_one.title}]

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_empty_shelves(stash)
        tap.eq(errors, [], 'Нет ошибок')

        errors = await process_empty_shelves(stash)
        tap.eq(errors, [], 'Снова нет ошибок')

        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('count', '>', 0)
            ],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (stock_two.product_id, stock_two.shelf_id, stock_two.count),
            },
            'Остатки удалились на нужных полках'
        )


async def test_wrong_store(tap, dataset, cfg):
    with tap.plan(5, 'Успешный импорт остатков идемпотентность'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        stock_one = await dataset.stock(shelf=shelf_one, count=31)

        rows = [{'shelf': shelf_one.title}]

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_empty_shelves(stash)

        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(
            errors[0].value,
            store.store_id,
            'Правильное значение в ошибке'
        )
        tap.eq(errors[0].code, 'ER_GONE', 'Правильный код в ошибке')
        tap.ok(await stock_one.reload(), 'Остаток перезабрали')
        tap.eq(stock_one.count, 31, 'Остаток остался')
