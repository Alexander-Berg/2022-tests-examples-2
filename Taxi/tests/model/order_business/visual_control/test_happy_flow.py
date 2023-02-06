async def test_one_stock(tap, dataset, wait_order_status):
    with tap.plan(19, 'черные на 1 стоке на полке'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        stock = await dataset.stock(product=banana, store=store, count=300)
        tap.eq(
            (stock.store_id, stock.count, stock.reserve),
            (store.store_id, 300, 0),
            '300 бананов на складе без резерва',
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
                    'shelf_id': stock.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')
        tap.eq(
            order.required[0].product_id,
            banana.product_id,
            'банан на проверку',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'на этапе проверки')

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 1, 'появился 1 саджест')
        tap.eq(
            (
                suggests['shelf2box'].product_id,
                suggests['shelf2box'].shelf_id,
                suggests['shelf2box'].count,
            ),
            (
                stock.product_id,
                stock.shelf_id,
                300,
            ),
            'проверить 300 бананов',
        )

        stocks = await dataset.Stock.list_by_order(order)
        tap.ok(not stocks, 'нет операций по остатку')

        await suggests['shelf2box'].done(count=10)

        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 1, 'есть операции по остатку')
        tap.eq(stocks[0].reserve, 10, 'в резерве 10 бананов')

        await wait_order_status(order, ('processing', 'waiting'))

        # ордер попытались завершить до закрытия всех саджестов
        order.user_done = user.user_id
        await order.save()

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        await order.reload()
        tap.eq(order.vars('stage'), 'trash', 'на этапе перекладки в треш')

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 2, 'теперь 2 саджеста')
        tap.eq(
            (
                suggests['box2shelf'].product_id,
                suggests['box2shelf'].shelf_id,
                suggests['box2shelf'].status,
                suggests['box2shelf'].count,
            ),
            (
                banana.product_id,
                trash.shelf_id,
                'request',
                10,
            ),
            '10 бананов не прошли фейсконтроль',
        )


async def test_two_stocks(tap, dataset, wait_order_status, uuid):
    with tap.plan(15, 'черные бананы на нескольких стоках на полке'):
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
            ]
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 1, 'появился 1 саджест')
        tap.eq(
            (
                suggests['shelf2box'].product_id,
                suggests['shelf2box'].shelf_id,
                suggests['shelf2box'].count,
            ),
            (
                banana.product_id,
                shelf.shelf_id,
                8,
            ),
            'проверить 8 бананов',
        )

        await suggests['shelf2box'].done(count=7)

        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'есть операции по остатку')
        tap.eq(
            sum(s.reserve for s in stocks), 7, 'в резерве 7 бананов'
        )

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 2, 'теперь 2 саджеста')
        tap.eq(
            (
                suggests['box2shelf'].product_id,
                suggests['box2shelf'].shelf_id,
                suggests['box2shelf'].status,
                suggests['box2shelf'].count,
            ),
            (
                banana.product_id,
                trash.shelf_id,
                'request',
                7,
            ),
            '7 бананов почернело',
        )


async def test_no_bad_banana(tap, dataset, wait_order_status, uuid):
    with tap.plan(12, 'при проверке не нашли черных бананов'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'создали полку')

        await dataset.stock(product=banana, shelf=shelf, count=3, lot=uuid())

        stocks = await dataset.Stock.list_by_shelf(
            store_id=shelf.store_id,
            shelf_id=shelf.shelf_id,
            product_id=banana.product_id,
        )
        tap.eq(
            sum(s.count for s in stocks),
            3,
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
            ]
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 1, 'появился 1 саджест')
        tap.eq(
            (
                suggests['shelf2box'].product_id,
                suggests['shelf2box'].shelf_id,
                suggests['shelf2box'].count,
            ),
            (
                banana.product_id,
                shelf.shelf_id,
                3,
            ),
            'проверить 3 банана',
        )

        # закрываем саджест в 0, те нет плохих бананов
        await suggests['shelf2box'].done(count=0)

        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'нет операций по остатку')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.type: s
            for s in await dataset.Suggest.list_by_order(order)
        }

        tap.eq(len(suggests), 1, 'все также 1 саджест')


# pylint: disable=too-many-statements
async def test_multi_products(tap, dataset, wait_order_status, uuid):
    with tap.plan(24, 'несколько товаров на фейсконтроль, только один закроем'):
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

        suggests_s2b = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='shelf2box', status='request',
            )
        }
        tap.eq(len(suggests_s2b), 2, '2 саджеста на проверку')

        await suggests_s2b[(banana.product_id, shelf.shelf_id)].done(count=8)
        # не закрываем яблоки
        # await suggests_s2b[(apple.product_id, shelf.shelf_id)].done(count=1)

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
        )

        await suggests_s2b[(apple.product_id, shelf.shelf_id)].reload()
        tap.eq(
            suggests_s2b[(apple.product_id, shelf.shelf_id)].vars('reserves'),
            {},
            'нет резерва',
        )
        # ОПАЧКИ закроем тут
        await suggests_s2b[(apple.product_id, shelf.shelf_id)].done(count=4)

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )
        await suggests_s2b[(apple.product_id, shelf.shelf_id)].reload()
        tap.eq(
            suggests_s2b[(apple.product_id, shelf.shelf_id)].vars('reserves'),
            {},
            'нет резерва',
        )

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='shelf2box', status='request',
            )
        }

        tap.eq(len(suggests), 0, '0 саджеста на взятие')
        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='box2shelf', status='request',
            )
        }
        tap.eq(len(suggests), 1, '1 саджеста на перенос в треш')
        tap.eq(
            suggests[(banana.product_id, trash.shelf_id)].count,
            6,
            'бананов на свалку',
        )

        await suggests[(banana.product_id, trash.shelf_id)].done(count=6)

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )

        tap.eq(
            sum(s.reserve for s in stocks),
            6 + 2,
            'бананы в резерве',
        )
        # UGLY wait_order_status сам закрывает саджетсы
        order.user_done = user.user_id
        await order.save()

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.fstatus, ('complete', 'begin'), 'статус ок')

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'резервов по ордеру')

        await wait_order_status(
            order, ('complete', 'done')
        )
        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'не резервов по ордеру')

