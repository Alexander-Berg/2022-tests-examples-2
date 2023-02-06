from stall.model.stock import job_import_data, process_import


async def test_success(tap, dataset, cfg):
    with tap.plan(6, 'Успешный импорт остатков'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='store', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 11,
            },
            {
                'shelf': shelf_two.title,
                'product': product.external_id,
                'count': 112,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        await job_import_data(stash.stash_id)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (product.product_id, shelf_one.shelf_id, 11),
                (product.product_id, shelf_two.shelf_id, 112)
            },
            'Остатки появились на нужных полках'
        )

        order = await dataset.Order.load(
            [store.store_id, stash.stash_id], by='external')
        tap.ok(order, 'Документ создан')
        tap.eq(order.type, 'stowage', 'Тип раскладка')
        tap.eq(order.user_id, user.user_id, 'Правильный пользователь')

        stash = await dataset.Stash.load(stash.stash_id)
        tap.is_ok(stash, None, 'Нет больше стэша')


async def test_errors(tap, dataset, cfg):
    with tap.plan(7, 'Ошибки сохраняются'):
        store = await dataset.store()
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 11,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        await job_import_data(stash.stash_id)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

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

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        await job_import_data(uuid())

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')


async def test_not_shelf(tap, dataset, cfg):
    with tap.plan(6, 'Кривые полки в импорте'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='lost', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 11,
            },
            {
                'shelf': 'горностайский сухолимб',
                'product': product.external_id,
                'count': 112,
            },
            {
                'shelf': shelf_two.title,
                'product': product.external_id,
                'count': 123,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_import(stash)

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
        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков все еще нет')


async def test_not_product(tap, dataset, cfg, uuid):
    with tap.plan(6, 'Кривой продукт'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')
        fake_product_external = uuid()

        rows = [
            {
                'shelf': shelf_one.title,
                'product': fake_product_external,
                'count': 11,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        result = await process_import(stash)

        tap.eq(len(result), 1, 'Одна ошибка')
        tap.eq(result[0].code, 'ER_NOT_FOUND', 'Код ошибки верный')
        tap.eq(result[0].value, fake_product_external, 'Значение то')

        order = await dataset.Order.load(
            [store.store_id, stash.stash_id], by='external')
        tap.ok(order is None, 'Документ не создан')
        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков все еще нет')


async def test_idempotency(tap, dataset, cfg):
    with tap.plan(7, 'Успешный импорт остатков идемпотентность'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='store', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 11,
            },
            {
                'shelf': shelf_two.title,
                'product': product.external_id,
                'count': 112,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_import(stash)
        tap.eq(errors, [], 'Нет ошибок')

        errors = await process_import(stash)
        tap.eq(errors, [], 'Снова нет ошибок')

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (product.product_id, shelf_one.shelf_id, 11),
                (product.product_id, shelf_two.shelf_id, 112)
            },
            'Остатки появились на нужных полках'
        )

        order = await dataset.Order.load(
            [store.store_id, stash.stash_id], by='external')
        tap.ok(order, 'Документ создан')
        tap.eq(order.type, 'stowage', 'Тип раскладка')
        tap.eq(order.user_id, user.user_id, 'Правильный пользователь')


async def test_wrong_store(tap, dataset, cfg):
    with tap.plan(5, 'Склад не в списке разрешенных для операции'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 11,
            }
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_import(stash)

        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(
            errors[0].value,
            store.store_id,
            'Правильное значение в ошибке'
        )
        tap.eq(errors[0].code, 'ER_GONE', 'Правильный код в ошибке')
        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков все еще нет')


async def test_stock_already(tap, dataset, cfg):
    with tap.plan(3, 'На той же полке был остаток'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed',
                [store.external_id])
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(type='store', store=store)
        product = await dataset.product()
        await dataset.stock(shelf=shelf, product=product, count=666)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 1, 'Один остаток был')

        rows = [
            {
                'shelf': shelf.title,
                'product': product.external_id,
                'count': 33,
            },
        ]

        stash_name = f'stocks_import_data-{store.store_id}'

        stash = await dataset.Stash.stash(
            name=stash_name,
            user_id=user.user_id,
            store_id=store.store_id,
            rows=rows,
        )

        errors = await process_import(stash)
        tap.eq(errors, [], 'Нет ошибок, загрузили')

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (product.product_id, shelf.shelf_id, 666),
                (product.product_id, shelf.shelf_id, 33),
            },
            'Два остатка, новый отдельно от старого'
        )
