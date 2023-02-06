# pylint: disable=too-many-statements,too-many-locals
async def test_weight(tap, dataset, wait_order_status):
    with tap.plan(29, 'Тесты весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()

        tap.ok(products, 'товар создан')
        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 30,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        for i in range(3):
            with tap.subtest(21, 'цикл генерация-закрытие') as taps:
                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request')
                taps.eq(len(suggests), 1, 'один саджест сгенерирован')
                with suggests[0] as s:
                    taps.eq(s.product_id, parent.product_id, 'product_id')
                    taps.eq(s.type, 'shelf2box', 'type')
                    taps.eq(s.store_id, store.store_id, 'store_id')
                    taps.eq(s.order_id, order.order_id, 'order_id')
                    taps.eq(s.count, 30 - i*10, 'count')
                    taps.eq(s.weight, None, 'weight')

                    taps.eq(s.conditions.all, True, 'all')
                    taps.eq(s.conditions.need_weight, True, 'need_weight')
                    taps.eq(
                        s.conditions.weight_aggregate,
                        True,
                        'weight_aggregate'
                    )
                    taps.ok(
                        await s.done(
                            weight=123,
                            count=10,
                            product_id=products[0].product_id
                        ),
                        'закрыт саджест'
                    )
                    tap.eq(
                        s.product_id,
                        products[0].product_id,
                        'product_id поменялся'
                    )

                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 1, 'один саджест добавился')
                with suggests[0] as s:
                    taps.eq(s.type, 'box2shelf', 'type')
                    taps.eq(s.product_id, products[0].product_id, 'product_id')
                    taps.eq(s.count, 10, 'count')
                    taps.eq(s.weight, 123, 'weight')
                    taps.ok(
                        await s.done(valid='2011-11-12', weight=123),
                        'закрыт и этот саджест'
                    )

                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 0, 'request саждестов нет')
                taps.eq(
                    order.vars('suggest_mode'),
                    'processing',
                    'suggest_mode'
                )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, weight=0), 'закрыли count=0')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 0, 'саджестов нет')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = [
            s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        ]

        tap.eq(len(stocks),  1, 'один сток')
        with next(sl for sl in stocks if sl.shelf_type == 'store') as s:
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 30, 'количество')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.valid.strftime('%F'), '2011-11-12', 'valid')
            tap.eq(s.vars['weight'], 3 * 123, 'weight')

        await order.reload()
        tap.eq(len(order.required), 1, 'один required')
        tap.eq(order.required[0]['result_count'],
               30,
               'result_count в required')
        tap.eq(order.required[0]['result_weight'],
               3 * 123,
               'result_weight в required')


async def test_weight_more_product(tap, dataset, wait_order_status):
    with tap.plan(44, 'Тесты весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products()
        tap.ok(products, 'товар создан')
        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 12,
                    'valid': '2020-05-13',
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with tap.subtest(23, 'цикл генерация-закрытие') as taps:
            await wait_order_status(
                order,
                ('processing', 'waiting'),
                tap=taps
            )
            suggests = await dataset.Suggest.list_by_order(
                order,
                status='request')
            taps.eq(len(suggests), 1, 'один саджест сгенерирован')
            with suggests[0] as s:
                taps.eq(s.product_id, parent.product_id, 'product_id')
                taps.eq(s.type, 'shelf2box', 'type')
                taps.eq(s.store_id, store.store_id, 'store_id')
                taps.eq(s.order_id, order.order_id, 'order_id')
                taps.eq(s.count, 12, 'count')
                taps.eq(s.weight, None, 'weight')
                taps.eq(s.valid.strftime('%F'), '2020-05-13',
                        'Срок годности от родительского ордера')

                taps.eq(s.conditions.all, True, 'all')
                taps.eq(s.conditions.need_weight, True, 'need_weight')
                taps.eq(
                    s.conditions.weight_aggregate,
                    True,
                    'weight_aggregate'
                )
                taps.ok(
                    # Изменим срок годности у весовой группы
                    await s.done(
                        weight=123,
                        count=11,
                        valid='2019-04-05',
                        product_id=products[0].product_id
                    ),
                    'закрыт саджест'
                )
                tap.eq(
                    s.product_id,
                    products[0].product_id,
                    'product_id поменялся'
                )

            await wait_order_status(
                order,
                ('processing', 'waiting'),
                tap=taps
            )
            suggests = await dataset.Suggest.list_by_order(
                order,
                status='request'
            )
            taps.eq(len(suggests), 1, 'один саджест добавился')
            with suggests[0] as s:
                taps.eq(s.type, 'box2shelf', 'type')
                taps.eq(s.product_id, products[0].product_id, 'product_id')
                taps.eq(s.count, 11, 'count')
                taps.eq(s.weight, 123, 'weight')
                taps.eq(s.valid.strftime('%F'), '2019-04-05',
                        'Срок годности от shelf2box')
                taps.ok(
                    await s.done(valid='2011-11-12', weight=123),
                    'закрыт и этот саджест'
                )

            suggests = await dataset.Suggest.list_by_order(
                order,
                status='request'
            )
            taps.eq(len(suggests), 0, 'request саждестов нет')
            taps.eq(
                order.vars('suggest_mode'),
                'processing',
                'suggest_mode'
            )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, weight=0), 'закрыли count=0')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 0, 'саджестов нет')

        tap.ok(await order.signal(
            {
                'type': 'more_product',
                'data': {
                    'product_id': parent.product_id,
                    'count': 1,
                    'weight': 201
                }
            }), 'сигнал more_product')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'саджест сгенерирован')
        tap.eq(suggests[0].valid.strftime('%F'), '2020-05-13',
               'Срок годности от родительского ордера')

        with suggests[0] as s:
            await s.done(count=1, weight=201)

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        # проверки значение
        with suggests[0] as s:
            tap.eq(s.type, 'box2shelf', 'type')
            tap.eq(s.product_id, products[1].product_id, 'product_id')
            tap.eq(s.count, 1, 'count')
            tap.eq(s.weight, 201, 'weight')
            tap.eq(s.valid.strftime('%F'), '2020-05-13',
                   'Срок годности от родительского ордера')

            tap.ok(await s.done(count=1, weight=201), 'закрыли count=5')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')
        with suggests[0] as s:
            await s.done(count=0, weight=0)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = [
            s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        ]

        tap.eq(len(stocks), 2, 'стоки')
        with [s for s in stocks
              if s.product_id == products[0].product_id][0] as s:
            tap.eq(s.shelf_type, 'store', 'остаток на списании')
            tap.eq(s.count, 11, 'количество')
            tap.eq(s.vars['weight'], 123, 'weight')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.valid.strftime('%F'), '2011-11-12',
                   'Срок годности от box2shelf')

        # проверка сигнала
        with [s for s in stocks
              if s.product_id == products[1].product_id][0] as s:
            tap.eq(s.shelf_type, 'store', 'остаток на списании')
            tap.eq(s.count, 1, 'количество')
            tap.eq(s.vars['weight'], 201, 'weight')
            tap.eq(s.reserve, 0, 'нет резерва')
            tap.eq(s.valid.strftime('%F'), '2020-05-13',
                   'Срок годности от родительского ордера')

        await order.reload()

        tap.eq(len(order.required), 1, 'один required')
        tap.eq(order.required[0]['result_count'],
               11 + 1,
               'result_count в required')
        tap.eq(order.required[0]['result_weight'],
               123 + 201,
               'result_weight в required')
        tap.eq(order.required[0]['result_valid'].strftime('%F'),
               '2011-11-12',
               'valid в required')


async def test_two_weight(tap, dataset, wait_order_status):
    with tap.plan(12, 'В ордере два весовых товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product(type_accounting='weight')
        tap.ok(product, 'товар создан')

        wproduct1 = await dataset.product(
            parent_id=product.product_id,
            lower_weight_limit=0,
            upper_weight_limit=100
        )
        tap.eq(wproduct1.parent_id, product.product_id, 'товар-дочка 1')

        wproduct2 = await dataset.product(
            parent_id=product.product_id,
            lower_weight_limit=100,
            upper_weight_limit=200
        )
        tap.eq(wproduct2.parent_id, product.product_id, 'товар-дочка 2')

        wproduct3 = await dataset.product(
            parent_id=product.product_id,
            lower_weight_limit=200,
            upper_weight_limit=10000
        )
        tap.eq(wproduct3.parent_id, product.product_id, 'товар-дочка 3')

        product2 = await dataset.product(type_accounting='weight')
        tap.ok(product, 'товар создан')

        wproduct2_1 = await dataset.product(
            parent_id=product2.product_id,
            lower_weight_limit=0,
            upper_weight_limit=100
        )
        tap.eq(wproduct2_1.parent_id, product2.product_id, 'товар-дочка 1')

        wproduct2_2 = await dataset.product(
            parent_id=product2.product_id,
            lower_weight_limit=100,
            upper_weight_limit=200
        )
        tap.eq(wproduct2_2.parent_id, product2.product_id, 'товар-дочка 2')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'weight': 5000,
                },
                {
                    'product_id': product2.product_id,
                    'weight': 1000,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('failed', 'done'))


async def test_done_another_prod(tap, dataset, wait_order_status):
    with tap.plan(9,
                  'попытка закрыть саджест другим вес товаром'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        products = await dataset.weight_products(
            children=[[4000, 6000],
                      [6000, 8000],
                      [8000, 10000]]
        )
        tap.eq(len(products), 4, 'весовые товары созданы')

        products2 = await dataset.weight_products()
        tap.eq(len(products2), 4, 'весовые товары созданы')

        order = await dataset.order(
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'count': 3,
                    'weight': 6000,
                }
            ],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))
        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with tap.raises(dataset.Suggest.ErSuggestWrongProductId,
                        'нельзя другой продукт'):
            with suggests[0] as s:
                await s.done(
                    count=2,
                    weight=400,
                    product_id=products2[1].product_id
                )


async def test_more_child(tap, dataset, wait_order_status):
    with tap.plan(15, 'Раскладка по разным полкам'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        child_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        products = await dataset.weight_products(children=child_weights)
        tap.eq(len(products), 3+1, '4 детей и родитель')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'weight': 100,
                    'count': 3,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('request', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        used_shelf = []
        len_childs = range(len(child_weights))
        for index in len_childs:
            with tap.subtest(15, 'цикл генерация-закрытие') as taps:
                child_id = products[index+1].product_id
                child_weight = (child_weights[index][0] +
                                child_weights[index][1])//2
                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request')
                taps.eq(len(suggests), 1, 'один саджест сгенерирован')

                with suggests[0] as s:
                    taps.eq(s.type, 'shelf2box', 'type')
                    taps.eq(s.product_id, products[0].product_id, 'product_id')
                    taps.ok(
                        await s.done(
                            weight=child_weight,
                            count=1,
                        ),
                        'закрыт саджест'
                    )

                await wait_order_status(
                    order,
                    ('processing', 'waiting'),
                    tap=taps
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 1, 'один саджест добавился')
                with suggests[0] as s:
                    taps.ok(s.shelf_id not in used_shelf,
                            'новая полка для ребенка вес товара')
                    used_shelf.append(s.shelf_id)
                    taps.eq(s.type, 'box2shelf', 'type')
                    taps.eq(s.product_id,  child_id, 'product_id')
                    taps.eq(s.count, 1, 'count')
                    taps.eq(s.weight, child_weight, 'weight')
                    taps.ok(
                        await s.done(weight=child_weight),
                        'закрыт и этот саджест'
                    )

                suggests = await dataset.Suggest.list_by_order(
                    order,
                    status='request'
                )
                taps.eq(len(suggests), 0, 'request саждестов нет')
                taps.eq(
                    order.vars('suggest_mode'),
                    'processing',
                    'suggest_mode'
                )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request')
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, weight=0), 'закрыли count=0')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = [
            s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        ]

        tap.eq(len(stocks), 3, 'три стока')
