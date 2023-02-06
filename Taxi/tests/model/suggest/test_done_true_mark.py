async def test_common_checks(tap, dataset):
    with tap.plan(7, 'Общие проверки закрытия саджеста'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        product = await dataset.product(true_mark=True)
        stock = await dataset.stock(store=store, count=10, product=product)
        order = await dataset.order(
            store=store,
            type='order',
            status='processing',
            estatus='waiting',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                }
            ],
            acks=[user.user_id],
            users=[user.user_id],

        )
        suggest = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )

        with tap.raises(suggest.ErSuggestTrueMarkRequired):
            await suggest.done(
                status='done',
                count=1
            )
        await suggest.reload()

        with tap.raises(suggest.ErSuggestInvalidTrueMark):
            await suggest.done(
                status='done',
                count=1,
                true_mark='123456789',
            )
        await suggest.reload()

        true_mark = '0199999999999999215Qbag!\x1D93Zjqw'
        with tap.raises(suggest.ErSuggestWrongProductTrueMark):
            await suggest.done(
                status='done',
                count=1,
                true_mark=true_mark,
            )
        await suggest.reload()
        correct_true_mark_one = await dataset.true_mark_value(
            product=product)
        tap.ok(
            await suggest.done(
                status='done',
                count=1,
                true_mark=correct_true_mark_one
            ),
            'Саджест успешно закрылся'
        )
        tap.ok(await suggest.reload(), 'Перезабрали саджест')

        tap.eq(
            suggest.vars('true_mark', None),
            correct_true_mark_one,
            'Марка нужная в саджесте',
        )
        refund = await dataset.order(
            type='refund',
            parent=[order.order_id],
            status='processing',
            estatus='waiting',
        )

        suggest = await dataset.suggest(
            type='shelf2box',
            order=refund,
            conditions={'need_true_mark': True, 'all': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        tap.ok(
            await suggest.done(
                status='done',
                count=0,
            ),
            'Саджест можно закрыть без марки с нулем'
        )


async def test_order_checks(tap, dataset):
    with tap.plan(10, 'Заказ проверки марочные'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        product = await dataset.product(true_mark=True)
        stock = await dataset.stock(store=store, count=10, product=product)
        order = await dataset.order(
            store=store,
            type='order',
            status='processing',
            estatus='waiting',
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 2,
                }
            ],
            acks=[user.user_id],
            users=[user.user_id],

        )
        suggest_one = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        suggest_two = await dataset.suggest(
            type='shelf2box',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )
        suggest_back = await dataset.suggest(
            type='box2shelf',
            order=order,
            conditions={'need_true_mark': True},
            product_id=stock.product_id,
            shelf_id=stock.shelf_id,
            count=1,
        )

        correct_mark_one = await dataset.true_mark_value(product=product)
        tap.ok(
            await suggest_one.done(
                status='done',
                count=1,
                true_mark=correct_mark_one,
            ),
            'Успешно закрыли саджест'
        )
        tap.ok(await suggest_one.reload(), 'Перезабрали саджест')

        tap.eq(
            suggest_one.vars('true_mark', None),
            correct_mark_one,
            'Марка нужная в саджесте',
        )

        with tap.raises(suggest_one.ErSuggestTrueMarkDuplicated):
            await suggest_two.done(
                status='done',
                count=1,
                true_mark=correct_mark_one,
            )
        tap.ok(await suggest_two.reload(), 'Перезабрали 2 саджест')

        correct_mark_two = await dataset.true_mark_value(product=product)
        tap.ok(
            await suggest_two.done(
                status='done',
                count=1,
                true_mark=correct_mark_two,
            ),
            'Успешно закрыли саджест'
        )
        tap.ok(await suggest_two.reload(), 'Перезабрали 2 саджест')

        wrong_mark = correct_mark_two[:-1] + '!'
        with tap.raises(suggest_back.ErSuggestTrueMarkNotInCurrentOrder):
            await suggest_back.done(
                status='done',
                count=1,
                true_mark=wrong_mark,
            )
        tap.ok(await suggest_back.reload(), 'Перезабрали 3 саджест')

        tap.ok(
            await suggest_back.done(
                status='done',
                count=1,
                true_mark=correct_mark_two,
            ),
            'Успешно закрыли саджест'
        )
