from stall.model.true_mark import TrueMark


async def test_unsold(tap, dataset):
    with tap.plan(11, 'Родительский заказ не продан'):
        order = await dataset.order(
            type='order',
            status='complete',
            estatus='done',
        )
        product = await dataset.product(true_mark=True)
        true_mark_in_order = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )
        true_mark_for_trash = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )

        refund = await dataset.order(
            type='refund',
            parent=[order.order_id],
            status='complete',
            estatus='done',
            vars={'parent_marks_sold': False}
        )
        suggest_store = await dataset.suggest(
            order=refund,
            product_id=product.product_id,
            status='done',
            conditions={'need_true_mark': True},
            vars={
                'true_mark': true_mark_in_order.value,
                'stage': 'store',
            }
        )
        true_mark_in_order.vars['refund_order'] = refund.order_id
        true_mark_in_order.vars['refund_suggest'] = suggest_store.suggest_id
        tap.ok(
            await true_mark_in_order.save(),
            'Сохранили марку store'
        )
        suggest_trash = await dataset.suggest(
            order=refund,
            product_id=product.product_id,
            status='done',
            conditions={'need_true_mark': True},
            vars={
                'true_mark': true_mark_for_trash.value,
                'stage': 'trash',
            }
        )
        true_mark_for_trash.vars['refund_order'] = refund.order_id
        true_mark_for_trash.vars['refund_suggest'] = suggest_trash.suggest_id
        tap.ok(
            await true_mark_for_trash.save(),
            'Сохранили марку trash'
        )
        await TrueMark.update_refund_true_marks(refund)

        tap.ok(await true_mark_in_order.reload(), 'Перезабрали марку')
        tap.not_in_ok(
            'refund_order',
            true_mark_in_order.vars,
            'Удалился из марки рефанд'
        )
        tap.not_in_ok(
            'refund_suggest',
            true_mark_in_order.vars,
            'Удалился из марки саджест'
        )
        tap.eq(
            true_mark_in_order.status,
            'for_sale',
            'Марка вернулась в продажу'
        )

        old_lsn = true_mark_for_trash.lsn
        tap.ok(await true_mark_for_trash.reload(), 'Перезабрали марку трэш')
        tap.eq(
            true_mark_for_trash.vars('refund_order', False),
            refund.order_id,
            'Рефанд в марке остался тот же'
        )
        tap.eq(
            true_mark_for_trash.vars('refund_suggest', False),
            suggest_trash.suggest_id,
            'Саджест в марке остался тот же'
        )
        tap.eq(
            true_mark_for_trash.status,
            'in_order',
            'Статус остался sold'
        )
        tap.eq(old_lsn, true_mark_for_trash.lsn, 'Марка не поменялась')


async def test_sold_parent(tap, dataset):
    with tap.plan(6, 'Родительский заказ продан'):
        order = await dataset.order(
            type='order',
            status='complete',
            estatus='done',
        )
        true_mark_in_order = await dataset.true_mark_object(
            order=order,
            status='sold',
        )
        refund = await dataset.order(
            type='refund',
            parent=[order.order_id],
            status='complete',
            estatus='done',
            vars={'parent_marks_sold': True}
        )
        suggest = await dataset.suggest(
            order=refund,
            status='done',
            conditions={'need_true_mark': True},
            vars={
                'true_mark': true_mark_in_order.value,
                'stage': 'store',
            }
        )
        true_mark_in_order.vars['refund_order'] = refund.order_id
        true_mark_in_order.vars['refund_suggest'] = suggest.suggest_id
        tap.ok(
            await true_mark_in_order.save(),
            'Сохранили марку'
        )
        await TrueMark.update_refund_true_marks(refund)

        old_lsn = true_mark_in_order.lsn
        tap.ok(await true_mark_in_order.reload(), 'Перезабрали марку')
        tap.eq(
            true_mark_in_order.vars('refund_order', False),
            refund.order_id,
            'Рефанд в марке остался тот же'
        )
        tap.eq(
            true_mark_in_order.vars('refund_suggest', False),
            suggest.suggest_id,
            'Саджест в марке остался тот же'
        )
        tap.eq(
            true_mark_in_order.status,
            'sold',
            'Статус остался sold'
        )
        tap.eq(old_lsn, true_mark_in_order.lsn, 'Марка не поменялась')


async def test_idempotency(tap, dataset):
    with tap.plan(7, 'Идемпотентность'):
        order = await dataset.order(
            type='order',
            status='complete',
            estatus='done',
        )
        product = await dataset.product(true_mark=True)
        true_mark_in_order = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )
        refund = await dataset.order(
            type='refund',
            parent=[order.order_id],
            status='complete',
            estatus='done',
            vars={'parent_marks_sold': False}
        )
        suggest_store = await dataset.suggest(
            order=refund,
            product_id=product.product_id,
            status='done',
            conditions={'need_true_mark': True},
            vars={
                'true_mark': true_mark_in_order.value,
                'stage': 'store',
            }
        )
        true_mark_in_order.vars['refund_order'] = refund.order_id
        true_mark_in_order.vars['refund_suggest'] = suggest_store.suggest_id
        tap.ok(
            await true_mark_in_order.save(),
            'Сохранили марку store'
        )
        await TrueMark.update_refund_true_marks(refund)
        tap.ok(await true_mark_in_order.reload(), 'Перезабрали марку')
        tap.not_in_ok(
            'refund_order',
            true_mark_in_order.vars,
            'Удалился из марки рефанд'
        )
        tap.not_in_ok(
            'refund_suggest',
            true_mark_in_order.vars,
            'Удалился из марки саджест'
        )
        tap.eq(
            true_mark_in_order.status,
            'for_sale',
            'Марка вернулась в продажу'
        )
        old_lsn = true_mark_in_order.lsn
        await TrueMark.update_refund_true_marks(refund)
        tap.ok(await true_mark_in_order.reload(), 'Перезабрали еще раз')
        tap.eq(old_lsn, true_mark_in_order.lsn, 'Марка не поменялась')
