from stall.model.suggest import Suggest


async def test_nocreate_product(tap, dataset, wait_order_status):
    with tap.plan(9, 'нет раскладки, если required получается пустой'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(
            type='acceptance',
            status='reserving',
            estatus='begin',
            required=[{
                'product_id': product.product_id,
                'count': 25,
            }],
            store_id=user.store_id,
            acks=[user.user_id],
        )
        tap.ok(order, 'заказ создан')

        incoming = await dataset.shelf(store_id=order.store_id, type='incoming')
        tap.eq(incoming.store_id, order.store_id, 'полка incoming создана')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')
        tap.ok(await suggests[0].done(count=0), 'закрываем на ноль')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.eq(order.vars('stowage_id'), [], 'нет дочернего ордера')


async def test_nocreate_weight_product(tap, dataset, wait_order_status):
    with tap.plan(10, 'нет раскладки, если required получается пустой'):
        weight_product = await dataset.product(type_accounting='weight')
        tap.ok(weight_product, 'товар весовой создан')

        user = await dataset.user()
        tap.ok(user.store_id, 'пользователь создан')

        order = await dataset.order(
            type='acceptance',
            status='reserving',
            estatus='begin',
            required=[{
                'product_id': weight_product.product_id,
                'count': 25,
                'weight': 2000,
            }],
            store_id=user.store_id,
            acks=[user.user_id],
        )
        tap.ok(order, 'заказ создан')

        incoming = await dataset.shelf(store_id=order.store_id, type='incoming')
        tap.eq(incoming.store_id, order.store_id, 'полка incoming создана')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')
        with tap.raises(Suggest.ErSuggestWeightRequired, 'закрываем на ноль'):
            await suggests[0].done(weight=0)

        tap.is_ok(order.vars('stowage_id', None),
                  None,
                  'выкладки не должно быть')
        tap.ok(await order.cancel(), 'отменяем ордер')

        await wait_order_status(order, ('canceled', 'done'))
