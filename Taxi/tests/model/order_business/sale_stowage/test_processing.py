import pytest


# pylint: disable=too-many-statements, too-many-locals
@pytest.mark.parametrize('exp_baden', [
    {
        'options': {'exp_baden_baden': True},
        'need_valid': True
    },
    {
        'options': {},
        'need_valid': False
    }
])
async def test_reserving(tap, dataset, wait_order_status, exp_baden):
    with tap.plan(63, 'Стадия раскладки'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store(options=exp_baden['options'])
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'посылка создана')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            status='reserving',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 7,
                },
                {
                    'item_id': item.item_id,
                    'count': 1,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')


        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста на раскладку')

        isuggest = next(
            (s for s in suggests if s.product_id == item.item_id),
            None
        )
        tap.ok(isuggest, 'саджест по посылке есть')
        tap.eq(isuggest.count, 1, 'количество')
        tap.eq(isuggest.conditions.all, True, 'Можно указать меньше')
        tap.eq(isuggest.conditions.max_count, True, 'Но не больше')
        tap.eq(isuggest.conditions.need_valid, False, 'СГ не требуется')

        psuggest = next(
            (s for s in suggests if s.product_id == product.product_id),
            None
        )
        tap.eq(psuggest.conditions['need_valid'],
               exp_baden['need_valid'],
               'СГ у обычного саджеста')
        tap.ok(psuggest, 'саджест по товару есть')
        tap.eq(psuggest.count, 7, 'количество')


        tap.ok(await psuggest.done(
            count=1,
            valid='2021-01-01',
        ), 'Закрываем продуктовый саджест')

        count = 7
        for _ in range(3):
            count -= 1
            await wait_order_status(order, ('processing', 'waiting'))

            suggests = await dataset.Suggest.list_by_order(order,
                                                           status='request')
            tap.eq(len(suggests), 2, 'два саджеста на раскладку')

            suggest = next(
                (s for s in suggests if s.product_id == product.product_id),
                None
            )
            tap.ok(suggest, 'саджест по товару есть')
            tap.eq(suggest.count, count, 'количество')
            tap.eq(suggest.vars('parent'), psuggest.suggest_id, 'parent')

            tap.ok(await suggest.done(
                count=1,
                valid='2021-01-01',
            ), 'Закрываем продуктовый саджест')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'stowage', 'стадия')

        product2 = await dataset.product()
        tap.ok(product2, 'товар создан')

        tap.ok(
            await order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product2.product_id,
                        'count': 17,
                    }
                }
            ), 'Сигнал о новом товаре отправлен'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.signals[order.vars['signo']].type,
            'more_product',
            'сигнал more_product'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал закрыт'
        )

        suggests = await dataset.Suggest.list_by_order(order,
                                                       status='request')
        psuggest = next(
            (s for s in suggests if s.product_id == product2.product_id),
            None
        )
        tap.ok(psuggest, 'саджест по товару есть')
        tap.eq(psuggest.vars('source', None), 'signal', 'Источник поставили')
        tap.ok(await psuggest.done(count=2, valid='2012-01-02'), 'закрыли')


        count = 17
        for _ in range(3):
            count -= 2
            await wait_order_status(order, ('processing', 'waiting'))

            suggests = await dataset.Suggest.list_by_order(order,
                                                           status='request')
            tap.eq(len(suggests), 3, 'Ещё саджесты на раскладку')

            suggest = next(
                (s for s in suggests if s.product_id == product2.product_id),
                None
            )
            tap.ok(suggest, 'саджест по товару есть')
            tap.eq(suggest.count, count, 'количество')
            tap.eq(suggest.vars('parent'), psuggest.suggest_id, 'parent')

            tap.ok(await suggest.done(count=2, valid='2071-09-08'),
                   'Закрываем продуктовый саджест')

