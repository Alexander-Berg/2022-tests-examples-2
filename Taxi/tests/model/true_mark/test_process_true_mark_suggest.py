async def test_refund_b2s(tap, dataset):
    with tap.plan(5, 'Возврат на полку'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
        )
        await dataset.TrueMark.process_true_mark_suggest(
            refund,
            suggest,
            true_mark.value,
        )
        tap.ok(await true_mark.reload(), 'Перезабрали марку')

        tap.eq(true_mark.order_id, order.order_id, 'Заказ верный')
        tap.eq(true_mark.status, 'sold', 'Марка в заказе')
        tap.eq(
            true_mark.vars('refund_order', None),
            refund.order_id,
            'Ордер прикопали'
        )
        tap.eq(
            true_mark.vars('refund_suggest', None),
            suggest.suggest_id,
            'Саджест прикопали'
        )


async def test_refund_b2s_return(tap, dataset):
    with tap.plan(5, 'Возврат на полку (после неудачи)'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
        )
        true_mark_old = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={
                'refund_order': refund.order_id,
                'refund_suggest': suggest.suggest_id,
            },
        )
        await dataset.TrueMark.process_true_mark_suggest(
            refund,
            suggest,
            true_mark.value,
        )
        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(
            true_mark.vars('refund_order', None),
            refund.order_id,
            'Ордер прикопали'
        )
        tap.eq(
            true_mark.vars('refund_suggest', None),
            suggest.suggest_id,
            'Саджест прикопали'
        )

        tap.ok(await true_mark_old.reload(), 'Перезабрали марку')
        tap.eq(true_mark_old.vars, {}, 'Почистили флаги')


async def test_refund_b2s_return_zero(tap, dataset):
    with tap.plan(2, 'Закрыли в ноль после неудачи'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='box2shelf',
            product_id=product.product_id,
            count=1,
            result_count=0,
        )
        true_mark_old = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={
                'refund_order': refund.order_id,
                'refund_suggest': suggest.suggest_id,
            },
        )
        await dataset.TrueMark.process_true_mark_suggest(
            refund,
            suggest,
            None,
        )
        tap.ok(await true_mark_old.reload(), 'Перезабрали марку')
        tap.eq(true_mark_old.vars, {}, 'Почистили флаги')


async def test_refund_s2b(tap, dataset, uuid):
    with tap.plan(5, 'Возврат с полки на корзину'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={
                'refund_order': refund.order_id,
                'refund_suggest': uuid(),
            }
        )
        await dataset.TrueMark.process_true_mark_suggest(
            refund,
            suggest,
            true_mark.value,
        )
        tap.ok(await true_mark.reload(), 'Перезабрали марку')

        tap.eq(true_mark.order_id, order.order_id, 'Заказ верный')
        tap.eq(true_mark.status, 'sold', 'Марка в заказе')
        tap.not_in_ok(
            'refund_order',
            true_mark.vars,
            'Удалили ордер'
        )
        tap.eq(
            true_mark.vars('refund_suggest', None),
            suggest.suggest_id,
            'Саджест прикопали'
        )


async def test_refund_s2b_return(tap, dataset, uuid):
    with tap.plan(6, 'Возврат в корзину (после неудачи)'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={
                'refund_order': refund.order_id,
                'refund_suggest': uuid(),
            }
        )
        true_mark_old = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={'refund_suggest': suggest.suggest_id},
        )
        await dataset.TrueMark.process_true_mark_suggest(
            refund,
            suggest,
            true_mark.value,
        )
        tap.ok(await true_mark.reload(), 'Перезабрали марку')

        tap.not_in_ok(
            'refund_order',
            true_mark.vars,
            'Удалили ордер'
        )
        tap.eq(
            true_mark.vars('refund_suggest', None),
            suggest.suggest_id,
            'Саджест прикопали'
        )
        tap.ok(await true_mark_old.reload(), 'Перезабрали марку старую')

        tap.eq(
            true_mark_old.vars('refund_order', None),
            refund.order_id,
            'Ордер прикопали снова'
        )

        tap.not_in_ok(
            'refund_suggest',
            true_mark_old.vars,
            'Удалили саджест'
        )


async def test_refund_duplicate(tap, dataset):
    with tap.plan(1, 'Марку уже использовали в заказе'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )
        another_suggest = await dataset.suggest(order=refund)
        true_mark = await dataset.true_mark_object(
            order=order,
            status='sold',
            product=product,
            vars={
                'refund_order': refund.order_id,
                'refund_suggest': another_suggest.suggest_id,
            },
        )
        with tap.raises(suggest.ErSuggestTrueMarkDuplicated):
            await dataset.TrueMark.process_true_mark_suggest(
                refund,
                suggest,
                true_mark.value,
            )


async def test_refund_no_mark(tap, dataset):
    with tap.plan(1, 'Марка неизвестная реестру'):
        order = await dataset.order(type='order', status='complete')
        refund = await dataset.order(type='refund', parent=[order.order_id])
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=refund,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )

        with tap.raises(suggest.ErSuggestWrongTrueMark):
            await dataset.TrueMark.process_true_mark_suggest(
                refund,
                suggest,
                await dataset.true_mark_value(product=product),
            )


async def test_idempotency(tap, dataset):
    with tap.plan(4, 'Проверим идемпотентность'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=order,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            suggest=suggest,
            status='for_sale'
        )

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark.value,
        )
        old_lsn = true_mark.lsn
        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.ok(true_mark.lsn != old_lsn, 'Марка изменилась')

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark.value,
        )
        old_lsn = true_mark.lsn
        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(true_mark.lsn, old_lsn, 'Марка не изменилась')


async def test_order_shelf2box(tap, dataset):
    with tap.plan(6, 'Положить в коробку несуществующую марку'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=order,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        true_mark_value = await dataset.true_mark_value(product=product)

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark_value,
        )

        true_mark = await dataset.TrueMark.load(true_mark_value, by='value')
        tap.ok(true_mark, 'Есть марка')
        tap.eq(true_mark.order_id, order.order_id, 'Заказ верный')
        tap.eq(true_mark.suggest_id, suggest.suggest_id, 'Саджест тот')
        tap.eq(true_mark.value, true_mark_value, 'Марка та')
        tap.eq(true_mark.status, 'in_order', 'Марка в заказе')
        tap.ok('order_created' in true_mark.vars, 'Дату заказа прикопали')


async def test_order_shelf2box_return(tap, dataset):
    with tap.plan(4, 'Второй раз закрываем саджест s2b, старую марку вернем'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=order,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        old_true_mark = await dataset.true_mark_object(
            order=order,
            suggest=suggest,
            product=product,
            status='in_order',
        )
        true_mark_value = await dataset.true_mark_value(product=product)

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark_value,
        )

        true_mark = await dataset.TrueMark.load(true_mark_value, by='value')
        tap.ok(true_mark, 'Есть марка')
        tap.eq(true_mark.status, 'in_order', 'Марка в заказе')

        tap.ok(await old_true_mark.reload(), 'Перезабрали старую марку')
        tap.eq(old_true_mark.status, 'for_sale', 'Сменился статус')


async def test_order_box2shelf(tap, dataset):
    with tap.plan(4, 'Вернуть на полку марочный товар'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        true_mark = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )
        suggest = await dataset.suggest(
            order=order,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark.value,
        )

        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(true_mark.order_id, order.order_id, 'Заказ верный')
        tap.eq(true_mark.suggest_id, suggest.suggest_id, 'Саджест тот')
        tap.eq(true_mark.status, 'for_sale', 'Марка в продаже')


async def test_order_box2shelf_return(tap, dataset):
    with tap.plan(4, 'Второй раз закрываем саджест b2s, старую марку вернем'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        suggest = await dataset.suggest(
            order=order,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )
        old_true_mark = await dataset.true_mark_object(
            order=order,
            suggest=suggest,
            product=product,
            status='for_sale',
        )
        true_mark = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )

        await dataset.TrueMark.process_true_mark_suggest(
            order,
            suggest,
            true_mark.value,
        )

        tap.ok(await true_mark.reload(), 'Перезабрали марку новую')
        tap.eq(true_mark.status, 'for_sale', 'Марка в заказе')

        tap.ok(await old_true_mark.reload(), 'Перезабрали старую марку')
        tap.eq(old_true_mark.status, 'in_order', 'Сменился статус')


async def test_order_shelf2box_duplicate(tap, dataset):
    with tap.plan(3, 'Положить дважды одну марку в корзину'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        true_mark = await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )
        suggest = await dataset.suggest(
            order=order,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        old_lsn = true_mark.lsn

        with tap.raises(suggest.ErSuggestTrueMarkDuplicated):
            await dataset.TrueMark.process_true_mark_suggest(
                order,
                suggest,
                true_mark.value,
            )

        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(true_mark.lsn, old_lsn, 'Марка не поменялась')


async def test_order_box2shelf_wrong_mark(tap, dataset):
    with tap.plan(3, 'Вернуть на полку не ту марку'):
        order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        await dataset.true_mark_object(
            order=order,
            product=product,
            status='in_order',
        )
        suggest = await dataset.suggest(
            order=order,
            type='box2shelf',
            product_id=product.product_id,
            result_count=1,
        )
        another_order = await dataset.order(type='order')
        another_true_mark = await dataset.true_mark_object(
            order=another_order,
            product=product,
            status='for_sale',
        )
        old_lsn = another_true_mark.lsn

        with tap.raises(suggest.ErSuggestTrueMarkNotInCurrentOrder):
            await dataset.TrueMark.process_true_mark_suggest(
                order,
                suggest,
                another_true_mark.value,
            )
        tap.ok(await another_true_mark.reload(), 'Перезабрали марку')
        tap.eq(another_true_mark.lsn, old_lsn, 'Марка не поменялась')


async def test_order_s2b_another_order(tap, dataset):
    with tap.plan(3, 'Положить марку из другого заказа'):
        order = await dataset.order(type='order')
        another_order = await dataset.order(type='order')
        product = await dataset.product(true_mark=True)
        true_mark = await dataset.true_mark_object(
            order=another_order,
            product=product,
            status='in_order',
        )
        suggest = await dataset.suggest(
            order=order,
            type='shelf2box',
            product_id=product.product_id,
            result_count=1,
        )
        old_lsn = true_mark.lsn

        with tap.raises(suggest.ErSuggestTrueMarkInAnotherOrder):
            await dataset.TrueMark.process_true_mark_suggest(
                order,
                suggest,
                true_mark.value,
            )

        tap.ok(await true_mark.reload(), 'Перезабрали марку')
        tap.eq(true_mark.lsn, old_lsn, 'Марка не поменялась')
