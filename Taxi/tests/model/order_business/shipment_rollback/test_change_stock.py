async def test_change_stock(tap, dataset, wait_order_status, uuid, now):
    # pylint: disable=too-many-locals
    with tap.plan(19, 'реверт отгрузки сменилась полка'):
        store = await dataset.store()
        await dataset.shelf(store=store, type='trash')
        await dataset.shelf(store=store, type='lost')
        user = await dataset.user(role='admin', store=store)
        stock_1 = await dataset.stock(store=store, count=2, lot=uuid())
        stock_2 = await dataset.stock(
            store=store,
            product_id=stock_1.product_id,
            count=4,
        )

        shipment = await dataset.order_done(
            store=store,
            type='shipment',
            approved=now(),
            acks=[user.user_id],
            required=[{
                'product_id': stock_1.product_id,
                'count': 6,
            }],
        )
        tap.eq(shipment.type, 'shipment', 'создали отгрузку')
        tap.eq(shipment.fstatus, ('complete', 'done'), 'отгрузили')

        shelf_1 = await dataset.Shelf.load(stock_1.shelf_id)
        shelf_1.type = 'parcel'
        tap.ok(await shelf_1.save(), 'Тип полки сменил')

        shipment_rollback_required = await shipment.business.refund_required()
        shipment_rollback = await dataset.order(
            store=store,
            type='shipment_rollback',
            approved=now(),
            acks=[user.user_id],
            required=shipment_rollback_required,
            parent=[shipment.order_id]
        )
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
        tap.eq(len(suggests), 1, 'сгенерили саджесты')

        for s in suggests.values():
            await s.done(count=s.count, user=user)

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))
        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'trash'}},
            ),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await wait_order_status(shipment_rollback, ('processing', 'waiting'))
        tap.ok(
            await shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'all_done'}},
            ),
            'сигнал на переход в финальный статус'
        )

        await wait_order_status(
            shipment_rollback, ('complete', 'done'), user_done=user,
        )
        stocks = await dataset.Stock.list(
            by='full',
            conditions=('store_id', store.store_id),
        )
        tap.eq(len(stocks.list), 2, 'Те же два остатка')
        tap.ok(await stock_1.reload(), 'Перезабрали первый остаток')
        tap.eq(stock_1.count, 0, 'Остался ноль на первом')

        tap.ok(await stock_2.reload(), 'Перезабрали второй остаток')
        tap.eq(stock_2.count, 6, 'Все остатки на стоке 2')
