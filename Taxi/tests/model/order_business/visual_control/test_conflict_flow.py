async def test_two_stocks(tap, dataset, wait_order_status, uuid):
    with tap.plan(
            18, 'не смогли забрать все черные бананы, тк кто-то успел купить',
    ):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3, lot=uuid())
        await dataset.stock(product=banana, shelf=shelf, count=5, lot=uuid())

        stocks = await dataset.Stock.list_by_shelf(
            store_id=shelf.store_id,
            shelf_id=shelf.shelf_id,
            product_id=banana.product_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            8,
            'всего бананов',
        )
        tap.eq(
            sum(s.reserve for s in stocks),
            0,
            'резерва нет',
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
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'появился 1 саджест')
        tap.eq(
            (
                suggests[0].type,
                suggests[0].product_id,
                suggests[0].shelf_id,
                suggests[0].count,
            ),
            (
                'shelf2box',
                banana.product_id,
                shelf.shelf_id,
                8,
            ),
            'проверить 8 бананов',
        )

        await suggests[0].done(count=7)

        order2 = await dataset.order(
            store=store,
            acks=[user.user_id],
            required=[
                {'product_id': banana.product_id, 'count': 2},
            ]
        )
        await wait_order_status(order2, ('approving', 'waiting'))

        stocks = await dataset.Stock.list_by_shelf(
            store_id=shelf.store_id,
            shelf_id=shelf.shelf_id,
            product_id=banana.product_id,
        )
        tap.eq(
            sum(s.reserve for s in stocks),
            2,
            'появился резерв',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, type='box2shelf', status='request',
        )
        tap.eq(len(suggests), 1, '1 саджест на возврат')
        tap.eq(
            (
                suggests[0].product_id,
                suggests[0].shelf_id,
                suggests[0].count,
            ),
            (
                banana.product_id,
                shelf.shelf_id,
                1,
            ),
            'вернем 1 черный банан на полку, тк кому-то он нужнее',
        )

        await suggests[0].done(count=1)

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 1, '1 саджест на перекладку в треш')
        tap.eq(
            (
                suggests[0].product_id,
                suggests[0].shelf_id,
                suggests[0].count,
            ),
            (
                banana.product_id,
                trash.shelf_id,
                6,
            ),
            'в треш пойдет 6 бананов, а не 7',
        )

        stocks = await dataset.Stock.list_by_shelf(
            store_id=shelf.store_id,
            shelf_id=shelf.shelf_id,
            product_id=banana.product_id,
        )
        tap.eq(
            sum(s.reserve for s in stocks),
            8,
            'все наши бананы в резерве',
        )


async def test_multi_products(tap, dataset, wait_order_status, uuid):
    with tap.plan(20, 'несколько товаров на фейсконтроль'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3, lot=uuid())
        await dataset.stock(product=banana, shelf=shelf, count=5, lot=uuid())
        await dataset.stock(product=apple, shelf=shelf, count=7, lot=uuid())

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            3 + 5 + 7,
            'бананы и яблоки в стоке',
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
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': apple.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='shelf2box', status='request',
            )
        }
        tap.eq(len(suggests), 2, '2 саджеста на проверку')

        await suggests[(banana.product_id, shelf.shelf_id)].done(count=8)
        await suggests[(apple.product_id, shelf.shelf_id)].done(count=1)

        order2 = await dataset.order(
            store=store,
            acks=[user.user_id],
            required=[
                {'product_id': banana.product_id, 'count': 2},
            ]
        )
        await wait_order_status(order2, ('approving', 'waiting'))

        stocks = await dataset.Stock.list_by_shelf(
            store_id=shelf.store_id,
            shelf_id=shelf.shelf_id,
            product_id=banana.product_id,
        )
        tap.eq(
            sum(s.reserve for s in stocks),
            2,
            'появился конфликтующий резерв',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='request',
        )
        tap.eq(len(suggests), 1, '1 саджест на возврат')
        tap.eq(
            (
                suggests[0].product_id,
                suggests[0].shelf_id,
                suggests[0].count,
            ),
            (
                banana.product_id,
                shelf.shelf_id,
                2,
            ),
            'вернем 2 черных банана на полку, тк кому-то они нужнее',
        )

        await suggests[0].done(count=2)

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='box2shelf', status='request',
            )
        }
        tap.eq(len(suggests), 2, '2 саджеста на перенос в треш')
        tap.eq(
            suggests[(banana.product_id, trash.shelf_id)].count,
            6,
            'бананов на свалку',
        )
        tap.eq(
            suggests[(apple.product_id, trash.shelf_id)].count,
            1,
            'яблоки на свалку',
        )

        await suggests[(banana.product_id, trash.shelf_id)].done(count=6)
        await suggests[(apple.product_id, trash.shelf_id)].done(count=1)

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(
            sum(s.reserve for s in stocks),
            6 + 2 + 1,
            'бананы и яблоки в резерве',
        )

        suggests = await dataset.Suggest.list_by_order(
            order, types='shelf2box', status='done',
        )
        tap.eq(len(suggests), 2, 'саджеты на проверку')

        suggests = await dataset.Suggest.list_by_order(
            order, types='box2shelf', status='done',
        )
        tap.eq(
            len(suggests), 3, '1 саджест на возврат и 2 на перекладку в треш',
        )

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 0, 'все саджесты закрыли')
