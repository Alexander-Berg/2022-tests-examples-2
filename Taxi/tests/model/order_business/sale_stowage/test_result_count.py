# pylint: disable=too-many-statements
async def test_trash(tap, dataset, wait_order_status):
    with tap.plan(35, 'Контроль result_count'):
        product1 = await dataset.product()
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар создан')

        product3 = await dataset.product()
        tap.ok(product3, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item1 = await dataset.item(store=store)
        tap.eq(item1.store_id, store.store_id, 'экземпляр создан')

        item2 = await dataset.item(store=store)
        tap.eq(item2.store_id, store.store_id, 'экземпляр создан')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='reserving',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 123,
                    'maybe_count': True,
                },
                {
                    'product_id': product2.product_id,
                    'count': 234,
                },
                {
                    'item_id': item1.item_id,
                },
                {
                    'item_id': item2.item_id,
                },
            ],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'четыре саджеста')

        with next(s for s in suggests
                  if s.product_id == product1.product_id) as s:
            tap.ok(await s.done(count = s.count + 23),
                   'Закрываем на бОльшее число')

        with next(s for s in suggests
                  if s.product_id == item1.item_id) as s:
            tap.ok(await s.done(count = s.count),
                   'Закрываем экземпляр')

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product3.product_id,
                        'count': 238,
                        'valid': '2019-01-02',
                    },
                }
            ),
            'Отправлен сигнал о ещё одном товаре'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        with next(s for s in suggests
                  if s.product_id == product3.product_id) as s:
            tap.ok(await s.done(count=11),
                   'Закрываем на меньшее число')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал')
        while order.vars('stage') != 'trash':
            await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests),
               3 + 2,
               'число саджестов: на trash не кладём экземпляры')

        with next(s for s in suggests
                  if s.product_id == product2.product_id
                  and s.status == 'request') as s:
            tap.ok(await s.done(count = s.count - 5),
                   'Закрываем на меньшее число товар 2')

        with next(s for s in suggests
                  if s.product_id == product3.product_id
                  and s.status == 'request') as s:
            tap.ok(await s.done(count = 0),
                   'Закрываем на ноль число товар 3')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(len(order.required), 5, 'пять товаров в required')
        for r in order.required:
            if r.product_id == product1.product_id:
                tap.eq(r.result_count, 123 + 23, 'общее количество товар 1')
                tap.eq(r.count, 123, 'начальное значение')
                continue
            if r.item_id == item1.item_id:
                tap.eq(r.result_count, 1, 'экземпляр 1 зачислен')
                tap.eq(r.count, 1, 'начальное значение')
                continue
            if r.item_id == item2.item_id:
                tap.eq(r.result_count, 0, 'экземпляра 2 нет')
                tap.eq(r.count, 1, 'начальное значение')
                continue
            if r.product_id == product2.product_id:
                tap.eq(r.result_count, 234 - 5, 'товар 2 на списание')
                tap.eq(r.count, 234, 'начальное значение')

            if r.product_id == product3.product_id:
                tap.eq(r.result_count, 11, 'товар 3')
                tap.eq(r.count, 0, 'товара 3 в начале не было')


async def test_weight(tap, dataset, wait_order_status):
    with tap.plan(40, 'Передаем весовой товар'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        products = await dataset.weight_products()
        tap.ok(products, 'весовые продукты')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=True,
            type='sale_stowage',
            required=[
                {
                    'product_id': products[1].product_id,
                    'weight': 75,
                    'count': 13,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, products[1].product_id, 'product_id')
            tap.eq(s.weight, 75, 'вес')
            tap.eq(s.count, 13, 'count')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.ok(await s.done(count=13, weight=78), 'завершён')

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': products[1].product_id,
                        'count': 10,
                    }
                }
            ), 'Сигнал о новом товаре отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, products[1].product_id, 'product_id')
            tap.eq(s.weight, None, 'вес')
            tap.eq(s.count, 10, 'count')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.ok(await s.done(
                count=10, weight=10, valid='2020-11-11'), 'завершён')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал')
        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': products[1].product_id,
                        'count': 17,
                    }
                }
            ), 'Сигнал о новом товаре отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, products[1].product_id, 'product_id')
            tap.eq(s.weight, None, 'вес')
            tap.eq(s.count, 17, 'count')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.ok(await s.done(count=17, weight=10, valid='2020-11-11'),
                   'завершён')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 3, 'Остатки')

        stocks = {
            s.stock_id: s
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
        }
        tap.eq(len(stocks), 3, 'всего два остатка')
        tap.eq(
            sum([s.count for s in stocks.values() if
                 s.product_id == products[1].product_id
                 and s.shelf_type == 'store']),
            13+10,
            'остатки товара 1 на полке'
        )
        tap.eq(
            sum([s.vars['weight'] for s in stocks.values() if
                 s.product_id == products[1].product_id
                 and s.shelf_type == 'store']),
            78+10,
            'суммарный вес товара 1 на полке'
        )

        tap.eq(
            sum([s.count for s in stocks.values() if
                 s.product_id == products[1].product_id
                 and s.shelf_type == 'trash']),
            17,
            'остатки товара 1 на списании'
        )
        tap.eq(
            sum([s.vars['weight'] for s in stocks.values() if
                 s.product_id == products[1].product_id
                 and s.shelf_type == 'trash']),
            10,
            'остатки веса товара 1 на списании'
        )
        await order.reload()
        with next(r for r in order.required
                  if r.product_id == products[1].product_id) as r:
            tap.eq(r.result_count, 40, 'количество принятого')
            tap.eq(r.result_weight, 78+10+10, 'вес принятого')
