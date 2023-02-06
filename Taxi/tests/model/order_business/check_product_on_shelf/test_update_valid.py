async def test_update_valid(tap, dataset, wait_order_status):
    with tap.plan(20, 'Простановка СГ всем'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='reserving',
            acks=[user.user_id],
            store=store,

            shelves=[stock.shelf_id],
            products=[stock.product_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'check_product_on_shelf', 'тип ордера')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(order.required, 'required сгенерирован если его не передали')
        order.required[0].update_valids = True
        order.rehashed('required', True)
        tap.ok(await order.save(), 'записали ордер')

        with order.required[0] as r:
            tap.eq(r.product_id, stock.product_id, 'product_id')
            tap.eq(r.shelf_id, stock.shelf_id, 'shelf_id')
            tap.ok(r.update_valids, 'update_valids')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на проверку')
        with suggests[0] as s:
            tap.eq(s.product_id, stock.product_id, 'product_id')
            tap.eq(s.shelf_id, stock.shelf_id, 'shelf_id')
            tap.eq(s.count, stock.count, 'количество')
            tap.eq(s.conditions.need_valid, False, 'need_valid')
            tap.eq(s.conditions.all, True, 'all')

            tap.ok(await s.done(count=stock.count, valid='2019-12-15'),
                   'закрыли саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
            ),
            sort=(),
        )
        tap.eq({s.valid.strftime('%F') for s in stocks},
               {'2019-12-15'},
               'Даты всем стокам проставлены')


async def test_no_valid(tap, dataset, wait_order_status):
    with tap.plan(20, 'Простановка СГ всем'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(
            store=store,
            valid='1996-11-21'
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            type='check_product_on_shelf',
            status='reserving',
            acks=[user.user_id],
            store=store,

            shelves=[stock.shelf_id],
            products=[stock.product_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.type, 'check_product_on_shelf', 'тип ордера')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(order.required, 'required сгенерирован если его не передали')
        order.required[0].update_valids = True
        order.rehashed('required', True)
        tap.ok(await order.save(), 'записали ордер')

        with order.required[0] as r:
            tap.eq(r.product_id, stock.product_id, 'product_id')
            tap.eq(r.shelf_id, stock.shelf_id, 'shelf_id')
            tap.ok(r.update_valids, 'update_valids')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест на проверку')
        with suggests[0] as s:
            tap.eq(s.product_id, stock.product_id, 'product_id')
            tap.eq(s.shelf_id, stock.shelf_id, 'shelf_id')
            tap.eq(s.count, stock.count, 'количество')
            tap.eq(s.conditions.need_valid, False, 'need_valid')
            tap.eq(s.conditions.all, True, 'all')

            tap.ok(await s.done(count=0),
                   'закрыли саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
            ),
            sort=(),
        )
        tap.eq({s.valid.strftime('%F') for s in stocks},
               {'1996-11-21'},
               'Даты остались')
