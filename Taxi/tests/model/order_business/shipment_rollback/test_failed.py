# pylint: disable=too-many-locals,too-many-statements


async def test_failed(tap, dataset, wait_order_status, now):
    with tap.plan(10, 'если нет полок падаем на старте, но можем оживить'):
        store = await dataset.store()

        user = await dataset.user(role='admin', store=store)

        p1_stock1 = await dataset.stock(store=store, count=2)
        p2_stock1 = await dataset.stock(store=store, count=3)

        shipment = await dataset.order_done(
            store=store,
            type='shipment',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': p1_stock1.product_id,
                    'count': 2,
                },
                {
                    'product_id': p2_stock1.product_id,
                    'count': 2,
                },
            ]
        )
        tap.eq(shipment.type, 'shipment', 'создали отгрузку')
        tap.eq(shipment.fstatus, ('complete', 'done'), 'отгрузили')

        shipment_rollback_required = await shipment.business.refund_required()

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

        await wait_order_status(shipment_rollback, ('failed', 'done'))

        tap.ok(shipment_rollback.problems, 'есть ошибки из-за полок')

        trash = await dataset.shelf(store=store, type='trash')
        tap.ok(trash, 'полка для списаний')

        lost = await dataset.shelf(store=store, type='lost')
        tap.ok(lost, 'полка для потерь')

        tap.ok(
            await shipment_rollback.signal({'type': 'order_defibrillation'}),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await shipment_rollback.business.order_changed()

        tap.eq(
            shipment_rollback.fstatus,
            ('reserving', 'begin'),
            'начали с начала',
        )
