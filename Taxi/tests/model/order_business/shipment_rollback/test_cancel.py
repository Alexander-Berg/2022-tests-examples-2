# pylint: disable=too-many-locals,too-many-statements

async def test_cancel(tap, dataset, wait_order_status, uuid, now):
    with tap.plan(46, 'отменяем возврат отгрузки'):
        store = await dataset.store()

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списаний')

        lost = await dataset.shelf(store=store, type='lost')
        tap.ok(lost, 'полка для потерь')

        user = await dataset.user(role='admin', store=store)

        p1_stock1 = await dataset.stock(store=store, count=2)
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
            lot=uuid(),
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
                    'product_id': p1_stock1.product_id,
                    'count': 2 + 2,
                },
                {
                    'product_id': p2_stock1.product_id,
                    'count': 3 + 3,
                },
                {
                    'item_id': i1.item_id,
                    'count': 1,
                },
                {
                    'item_id': i2.item_id,
                    'count': 1,
                },
            ],
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

        p2_stock_counts = {
            s.count
            for s in await dataset.Stock.list_by_product(
                product_id=p2_stock1.product_id,
                store_id=store.store_id,
            )
        }
        tap.eq(
            sum(p2_stock_counts),
            (3 + 6) - (3 + 3),
            'уменьшились остатки для второго товара',
        )

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
        tap.eq(len(shipment_rollback_required), 6, 'полный возврат')
        tap.eq(
            {r['stock_id'] for r in shipment_rollback_required},
            {
                p1_stock1.stock_id,
                p1_stock2.stock_id,
                p2_stock1.stock_id,
                p2_stock2.stock_id,
                i1_stock.stock_id,
                i2_stock.stock_id,
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
        tap.eq(len(suggests), 5, 'сгенерили саджесты')
        tap.eq(
            shipment_rollback.vars('gen_suggests_store'),
            True,
            'флажок поставили',
        )

        for s in suggests.values():
            if s.product_id == p2_stock1.product_id:
                count = s.count - 3
            else:
                count = s.count
            await s.done(count=count, user=user)

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='done',
            ) if s.vars('stage') == 'store'
        }
        tap.eq(len(suggests), 5, 'саджесты на раскладку закрыли')

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

        suggests = [
            s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='request',
            ) if s.vars('stage') == 'trash'
        ]
        tap.eq(len(suggests), 1, 'есть саджесты на мусорку')
        tap.eq(
            suggests[0].product_id,
            p2_stock1.product_id,
            'корректный товар на списание'
        )

        await suggests[0].done(count=1, user=user)

        suggests = [
            s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='box2shelf',
                status='done',
            ) if s.vars('stage') == 'trash'
        ]
        tap.eq(len(suggests), 1, 'закрыли саджесты на мусорку')

        shipment_rollback.target = 'canceled'
        await shipment_rollback.save()

        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'all_done'}},
            ),
            'сигнал на переход в финальный статус'
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))

        tap.eq(
            shipment_rollback.vars('stage'),
            'canceling',
            'отменяем взад',
        )

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                shipment_rollback,
                types='shelf2box',
                status='request',
            ) if s.vars('stage') == 'canceling'
        }
        tap.eq(len(suggests), 6, 'саджесты "вернуть в корзинку"')

        tap.eq(
            suggests[(p1_stock1.product_id, p1_stock1.shelf_id)].count,
            2,
            'первый товар с обычной полки',
        )
        tap.eq(
            suggests[(p1_stock2.product_id, p1_stock2.shelf_id)].count,
            2,
            'первый товар с обычной полки еще раз (да)',
        )

        tap.eq(
            suggests[(p2_stock1.product_id, p2_stock1.shelf_id)].count,
            3,
            'второй товар с обычной полки',
        )
        tap.eq(
            suggests[(p2_stock1.product_id, trash.shelf_id)].count,
            1,
            'второй товар с трешовой полки',
        )

        tap.eq(
            suggests[(i1_stock.product_id, i1_stock.shelf_id)].count,
            1,
            'первая посылка',
        )
        tap.eq(
            suggests[(i2_stock.product_id, i2_stock.shelf_id)].count,
            1,
            'вторая посылка',
        )

        await wait_order_status(
            shipment_rollback, ('canceled', 'done'), user_done=user,
        )

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
            'не изменились остатки для первого товара',
        )

        p2_stock_counts = {
            s.count
            for s in await dataset.Stock.list_by_product(
                product_id=p2_stock1.product_id,
                store_id=store.store_id,
            )
        }
        tap.eq(
            sum(p2_stock_counts),
            (3 + 6) - (3 + 3),
            'не изменились остатки для второго товара',
        )

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
