async def test_order(tap, dataset):
    with tap.plan(6, 'Обновляем марки в заказе'):
        order = await dataset.order(
            type='order',
            status='complete',
            estatus='done',
        )
        true_mark_in_order = await dataset.true_mark_object(
            order=order,
            status='in_order',
        )
        true_mark_missing = await dataset.true_mark_object(
            order=order,
            status='for_sale',
        )
        true_mark_redundant = await dataset.true_mark_object(
            order=order,
            status='in_order',
        )
        expected_marks = [
            true_mark_in_order.value,
            true_mark_missing.value,
        ]
        order.vars['assembled_products'] = [
            {'true_mark': expected_mark}
            for expected_mark in expected_marks
        ]
        await order.save(store_lp_event=False, store_job_event=False)

        await dataset.TrueMark.update_order_true_marks(
            order=order,
            target_status='sold',
            return_status='for_sale',
        )

        tap.ok(await true_mark_redundant.reload(), 'Перезабрали лишнюю марку')
        tap.eq(
            true_mark_redundant.status,
            'for_sale',
            'Лишняя вернулась в продажу'
        )
        tap.ok(await true_mark_missing.reload(), 'Забрали недостающую марку')
        tap.eq(
            true_mark_missing.status,
            'sold',
            'Недостающая вернулась в заказ'
        )
        order_marks = await dataset.TrueMark.list(
            by='full',
            conditions=[
                ('order_id', order.order_id),
                ('status', 'sold'),
            ]
        )
        tap.eq(len(order_marks.list), 2, 'Две марки продали в заказе')
        tap.eq(
            {mark.value for mark in order_marks},
            {true_mark_in_order.value, true_mark_missing.value},
            'Значения марок правильные'
        )


async def test_idempotency(tap, dataset):
    with tap.plan(8, 'Проверим идемпотентность обновления марок'):
        order = await dataset.order(
            type='order',
            status='complete',
            estatus='done',
        )
        true_mark_in_order = await dataset.true_mark_object(
            order=order,
            status='in_order',
        )
        true_mark_missing = await dataset.true_mark_object(
            order=order,
            status='for_sale',
        )
        true_mark_redundant = await dataset.true_mark_object(
            order=order,
            status='in_order',
        )
        all_marks = [
            true_mark_in_order,
            true_mark_missing,
            true_mark_redundant,
        ]
        expected_marks = [
            true_mark_in_order.value,
            true_mark_missing.value,
        ]
        current_lsns = [mark.lsn for mark in all_marks]
        order.vars['assembled_products'] = [
            {'true_mark': expected_mark}
            for expected_mark in expected_marks
        ]
        await order.save(store_lp_event=False, store_job_event=False)

        await dataset.TrueMark.update_order_true_marks(
            order=order,
            target_status='sold',
            return_status='for_sale',
        )
        for mark in all_marks:
            tap.ok(await mark.reload(), 'Перезабрали марку')

        new_lsns = [mark.lsn for mark in all_marks]
        tap.ne_ok(
            new_lsns,
            current_lsns,
            'Все записи изменились'
        )
        current_lsns = new_lsns

        await dataset.TrueMark.update_order_true_marks(
            order=order,
            target_status='sold',
            return_status='for_sale',
        )
        for mark in all_marks:
            tap.ok(await mark.reload(), 'Перезабрали марку')

        new_lsns = [mark.lsn for mark in all_marks]

        tap.eq(
            new_lsns,
            current_lsns,
            'Марки не поменялись'
        )
