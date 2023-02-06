# pylint: disable=too-many-locals,too-many-statements


async def test_product_only(tap, dataset, wait_order_status, uuid, now):
    with tap.plan(
            33, 'реверт отгрузки только с товарами без списаний и потерь'
    ):
        store = await dataset.store()

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списаний')

        lost = await dataset.shelf(store=store, type='lost')
        tap.ok(lost, 'полка для потерь')

        user = await dataset.user(role='admin', store=store)

        p1_stock1 = await dataset.stock(store=store, count=2, lot=uuid())
        p1_stock2 = await dataset.stock(
            store=store,
            product_id=p1_stock1.product_id,
            count=4,
        )
        tap.eq(p1_stock1.product_id, p1_stock1.product_id, 'первый товар')
        tap.ne(p1_stock1.shelf_id, p1_stock2.shelf_id, 'на разных полках')

        p2_stock1 = await dataset.stock(
            store=store,
            count=3,
        )
        p2_stock2 = await dataset.stock(
            store=store,
            product_id=p2_stock1.product_id,
            shelf_id=p2_stock1.shelf_id,
            count=6,
            lot=uuid(),
        )
        tap.eq(p2_stock1.product_id, p2_stock2.product_id, 'второй товар')
        tap.eq(p2_stock1.shelf_id, p2_stock2.shelf_id, 'на одной полке')

        shipment = await dataset.order_done(
            store=store,
            type='shipment',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': p1_stock1.product_id,
                    'count': 2 + 2,
                },
                {
                    'product_id': p2_stock1.product_id,
                    'count': 3 + 3,
                },
            ]
        )
        tap.eq(shipment.type, 'shipment', 'создали отгрузку')
        tap.eq(shipment.fstatus, ('complete', 'done'), 'отгрузили')

        p1_stock_counts = [
            s.count
            for s in await dataset.Stock.list_by_product(
                product_id=p1_stock1.product_id,
                store_id=store.store_id,
            )
        ]
        tap.eq(
            sum(p1_stock_counts),
            (2 + 4) - (2 + 2),
            'уменьшились остатки для первого товара',
        )

        p2_stock_counts = [
            s.count
            for s in await dataset.Stock.list_by_product(
                product_id=p2_stock1.product_id,
                store_id=store.store_id,
            )
        ]
        tap.eq(
            sum(p2_stock_counts),
            (3 + 6) - (3 + 3),
            'уменьшились остатки для второго товара',
        )

        shipment_rollback_required = await shipment.business.refund_required()
        tap.eq(len(shipment_rollback_required), 4, 'полный возврат')
        tap.eq(
            {r['stock_id'] for r in shipment_rollback_required},
            {
                p1_stock1.stock_id,
                p1_stock2.stock_id,
                p2_stock1.stock_id,
                p2_stock2.stock_id,
            },
            'все стоки из родителя на месте',
        )

        shipment_rollback = await dataset.order(
            store=store,
            type='shipment_rollback',
            approved=now(),
            acks=[user.user_id],
            required=shipment_rollback_required,
        )
        tap.eq(shipment_rollback.type, 'shipment_rollback', 'создали возврат')
        tap.eq(
            shipment_rollback.fstatus,
            ('reserving', 'begin'),
            'в начальном статусе',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        tap.eq(
            shipment_rollback.fstatus,
            ('processing', 'waiting'),
            'двигаем ордер',
        )
        tap.eq(
            shipment_rollback.vars('stage'),
            'store',
            'этап раскладки на полки',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='request',
            ) if s.vars('stage') == 'store'
        }
        tap.eq(len(suggests), 3, 'сгенерили саджесты')
        tap.eq(
            shipment_rollback.vars('gen_suggests_store'),
            True,
            'флажок поставили',
        )

        for s in suggests.values():
            await s.done(count=s.count, user=user)

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='done',
            ) if s.vars('stage') == 'store'
        }
        tap.eq(len(suggests), 3, 'саджесты на раскладку закрыли')

        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'trash'}},
            ),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        tap.eq(
            shipment_rollback.vars('stage'),
            'trash',
            'на этапе раскладки в мусорку',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='request',
            ) if s.vars('stage') == 'trash'
        }
        tap.eq(len(suggests), 0, 'нет саджестов на мусорку')

        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'all_done'}},
            ),
            'сигнал на переход в финальный статус'
        )

        await wait_order_status(
            shipment_rollback, ('complete', 'done'), user_done=user,
        )

        p1_stock_counts = {
            s.stock_id: s
            for s in await dataset.Stock.list_by_product(
                product_id=p1_stock1.product_id,
                store_id=store.store_id,
            )
        }
        await p1_stock1.reload()
        tap.eq(p1_stock1.count, 2, 'первый товар - первый сток')

        await p1_stock2.reload()
        tap.eq(p1_stock2.count, 4, 'первый товар - второй сток')

        await p2_stock1.reload()
        tap.eq(p2_stock1.count, 3, 'второй товар - первый сток')

        await p2_stock2.reload()
        tap.eq(p2_stock2.count, 6, 'второй товар - второй сток')


async def test_item_only(tap, dataset, wait_order_status, now):
    with tap.plan(27, 'простой кейс с посылками'):
        store = await dataset.store()

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списаний')

        lost = await dataset.shelf(store=store, type='lost')
        tap.ok(lost, 'полка для потерь')

        user = await dataset.user(role='admin', store=store)

        i1 = await dataset.item(store=store)
        i1_stock = await dataset.stock(item=i1, store=store, count=1)
        i2 = await dataset.item(store=store)
        i2_stock = await dataset.stock(item=i2, store=store, count=1)

        shipment = await dataset.order_done(
            store=store,
            type='shipment',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'item_id': i1.item_id,
                    'count': 1,
                },
                {
                    'item_id': i2.item_id,
                    'count': 1,
                },
            ]
        )
        tap.eq(shipment.type, 'shipment', 'создали отгрузку')
        tap.eq(shipment.fstatus, ('complete', 'done'), 'отгрузили')

        await i1.reload()
        await i1_stock.reload()
        tap.eq(
            (i1.status, i1_stock.count),
            ('inactive', 0),
            'нет посылки на остатке',
        )

        await i2.reload()
        await i2_stock.reload()
        tap.eq(
            (i2.status, i2_stock.count),
            ('inactive', 0),
            'нет посылки на остатке',
        )

        shipment_rollback_required = await shipment.business.refund_required()
        tap.eq(len(shipment_rollback_required), 2, 'полный возврат')
        tap.eq(
            {r['stock_id'] for r in shipment_rollback_required},
            {i1_stock.stock_id, i2_stock.stock_id},
            'все стоки из родителя на месте',
        )

        shipment_rollback = await dataset.order(
            store=store,
            type='shipment_rollback',
            approved=now(),
            acks=[user.user_id],
            required=shipment_rollback_required,
        )
        tap.eq(shipment_rollback.type, 'shipment_rollback', 'создали возврат')
        tap.eq(
            shipment_rollback.fstatus,
            ('reserving', 'begin'),
            'в начальном статусе',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        tap.eq(
            shipment_rollback.fstatus,
            ('processing', 'waiting'),
            'двигаем ордер',
        )
        tap.eq(
            shipment_rollback.vars('stage'),
            'store',
            'этап раскладки на полки',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='request',
            ) if s.vars('stage') == 'store'
        }
        tap.eq(len(suggests), 2, 'сгенерили саджесты')
        tap.eq(
            shipment_rollback.vars('gen_suggests_store'),
            True,
            'флажок поставили',
        )

        for s in suggests.values():
            await s.done(count=s.count, user=user)

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='done',
            ) if s.vars('stage') == 'store'
        }
        tap.eq(len(suggests), 2, 'саджесты на раскладку закрыли')

        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'trash'}},
            ),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        tap.eq(
            shipment_rollback.vars('stage'),
            'trash',
            'на этапе раскладки в мусорку',
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='request',
            ) if s.vars('stage') == 'trash'
        }
        tap.eq(len(suggests), 0, 'нет саджестов на мусорку')

        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'all_done'}},
            ),
            'сигнал на переход в финальный статус'
        )

        await wait_order_status(
            shipment_rollback, ('complete', 'done'), user_done=user,
        )

        await i1.reload()
        await i1_stock.reload()
        tap.eq(
            (i1.status, i1_stock.count),
            ('active', 1),
            'есть посылка на остатке',
        )

        await i2.reload()
        await i2_stock.reload()
        tap.eq(
            (i2.status, i2_stock.count),
            ('active', 1),
            'есть посылка на остатке',
        )
