async def test_no_required(tap, dataset, wait_order_status):
    with tap.plan(
            17, 'генерация саджестов по стоку и флагу фейсконтроля',
    ):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(banana.vars('imported.visual_control'), 'флаг фейсконтроля')

        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(apple.vars('imported.visual_control'), 'флаг фейсконтроля')

        coca = await dataset.product()
        tap.ok(
            coca.vars('imported.visual_control', False) is False,
            'флаг фейсконтроля отсуствует',
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=0)
        await dataset.stock(product=coca, shelf=shelf, count=5)

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            3 + 0 + 5,
            'есть остаток',
        )

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.eq(order.required, [], 'реквайред пустой')

        await wait_order_status(order, ('processing', 'suggests_generate'))

        tap.ok(await order.reload(), 'перегружаем ордер')
        tap.eq(
            len(order.vars('stat')), 1, 'есть данные для создания саджестов',
        )
        tap.eq(
            order.vars('stat.0'),
            {
                'shelf_id': shelf.shelf_id,
                'product_id': banana.product_id,
                'count': 3,
                'order': shelf.order,
            },
            'данные корректные',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перегружаем ордер')
        tap.eq(len(order.vars('stat')), 0, 'снесли стату')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'создался только 1 саджест')
        tap.eq(
            (suggests[0].product_id, suggests[0].count),
            (banana.product_id, 3),
            'проверяем только бананы',
        )


async def test_correct_suggest_reserves(tap, dataset, wait_order_status):
    with tap.plan(14, 'правильный резерв в генерируемых саджестах'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(banana.vars('imported.visual_control'), 'флаг фейсконтроля')

        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(apple.vars('imported.visual_control'), 'флаг фейсконтроля')

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=23)

        stocks = {
            stock.product_id: stock
            for stock in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
        }
        tap.eq(len(stocks), 2, 'Два остатка')

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.ok(order, 'ордер пустой')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            suggest.product_id: suggest
            for suggest in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 2, 'создано 2 саджеста')

        await suggests[banana.product_id].done(count=2)

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            suggest.product_id: suggest
            for suggest in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 2, 'создано 2 саджеста')
        tap.eq(
            {
                suggest.product_id: suggest.vars('reserves', None)
                for suggest in suggests.values()
            },
            {
                banana.product_id: {stocks[banana.product_id].stock_id: 2},
                apple.product_id: None
            },
            'резерв в одном саджесте'
        )

        await suggests[apple.product_id].done(count=20)

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            suggest.product_id: suggest
            for suggest in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(
            {
                suggest.product_id: suggest.vars('reserves', None)
                for suggest in suggests.values()
            },
            {
                banana.product_id: {stocks[banana.product_id].stock_id: 2},
                apple.product_id: {stocks[apple.product_id].stock_id: 20}
            },
            'резервы в оба саджеста'
        )


async def test_required(tap, dataset, wait_order_status):
    with tap.plan(
            14, 'генерация саджестов по переданным '
                'продуктам и флагу фейсконтроля',
    ):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(banana.vars('imported.visual_control'), 'флаг фейсконтроля')

        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        tap.ok(apple.vars('imported.visual_control'), 'флаг фейсконтроля')

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3)
        await dataset.stock(product=apple, shelf=shelf, count=0)

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            3 + 0,
            'есть остаток',
        )

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': banana.product_id,
                },
                {
                    'product_id': apple.product_id,
                },
            ],
        )
        await wait_order_status(order, ('processing', 'suggests_generate'))

        tap.ok(await order.reload(), 'перегружаем ордер')

        tap.eq(
            len(order.vars('stat')), 1, 'есть данные для создания саджестов',
        )

        tap.eq(
            order.vars('stat.0'),
            {
                'shelf_id': shelf.shelf_id,
                'product_id': banana.product_id,
                'count': 3,
                'order': shelf.order,
            },
            'данные корректные',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перегружаем ордер')
        tap.eq(len(order.vars('stat')), 0, 'снесли стату')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'создался только 1 саджест')
        tap.eq(
            (suggests[0].product_id, suggests[0].count),
            (banana.product_id, 3),
            'проверяем только бананы',
        )
