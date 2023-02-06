from scripts.cron.unknown_eda_status import process


async def test_success(tap, dataset, cfg):
    with tap.plan(6, 'Прошлись по документам и проставили'):
        cfg.set('business.eda.order_timeout', -2)
        store = await dataset.store()
        order_to_update = await dataset.order(
            type='order',
            store=store,
            status='complete',
            estatus='done',
            eda_status='ORDER_TAKEN',
        )
        order_empty_eda = await dataset.order(
            type='order',
            store=store,
            status='complete',
            estatus='done',
        )
        await process(store_id=store.store_id)

        old_lsn = order_empty_eda.lsn
        tap.ok(
            await order_empty_eda.reload(),
            'Перезабрали заказ без едового статуса'
        )
        tap.eq(
            order_empty_eda.lsn,
            old_lsn,
            'Заказ не менялся'
        )
        tap.eq(
            order_empty_eda.eda_status,
            None,
            'Едовый статус не менялся'
        )

        old_lsn = order_to_update.lsn
        tap.ok(
            await order_to_update.reload(),
            'Перезабрали заказ с едовым статусом'
        )
        tap.ne_ok(
            order_to_update.lsn,
            old_lsn,
            'Заказ поменялся'
        )
        tap.eq(
            order_to_update.eda_status,
            'UNKNOWN',
            'Едовый статус поменялся'
        )


async def test_true_mark(tap, dataset, cfg):
    with tap.plan(6, 'ЧЗ флаг выставлен'):
        cfg.set('business.eda.order_timeout', -2)
        store = await dataset.store()
        order = await dataset.order(
            type='order',
            store=store,
            status='complete',
            estatus='done',
            eda_status='ORDER_TAKEN',
        )
        order_true_mark = await dataset.order(
            type='order',
            store=store,
            status='complete',
            estatus='done',
            eda_status='ORDER_TAKEN',
            vars={
                'true_mark_in_order': True
            }
        )
        await process(store_id=store.store_id)

        tap.ok(
            await order.reload(),
            'Перезабрали заказ'
        )
        tap.eq(
            order.eda_status, 'UNKNOWN', 'Статус доставки проставился'
        )
        tap.not_in_ok(
            'need_sell_true_mark',
            order.vars,
            'Нет флага'
        )

        tap.ok(
            await order_true_mark.reload(),
            'Перезабрали заказ ЧЗ'
        )
        tap.eq(
            order_true_mark.eda_status,
            'UNKNOWN',
            'Едовый статус поменялся'
        )
        tap.eq(
            order_true_mark.vars('need_sell_true_mark', False),
            True,
            'Флаг продажи марок выставлен'
        )
