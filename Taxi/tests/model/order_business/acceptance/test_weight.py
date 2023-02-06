import pytest

from stall.model.suggest import Suggest


async def test_weight(tap, dataset, wait_order_status):
    with tap.plan(35, 'тестирование создания раскладки весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(type_accounting='weight')
        tap.ok(product1, 'товар создан')
        tap.eq(product1.type_accounting, 'weight', 'тип - весовой')

        product2 = await dataset.product(
            upper_weight_limit=150,
            lower_weight_limit=0,
            parent_id=product1.product_id,
        )
        tap.ok(product2, 'товар 2 создан')
        tap.eq(product2.parent_id, product1.product_id, 'parent_id')
        tap.eq(product2.upper_weight_limit, 150, 'upper_weight_limit')
        tap.eq(product2.lower_weight_limit, 0, 'lower_weight_limit')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=True,
            type='acceptance',
            required=[
                {
                    'product_id': product1.product_id,
                    'weight': 75,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(order.vars.get('dont_trust'), True, 'не доверяем приемку')
        tap.eq(order.vars.get('has_weight_products'),
               True,
               'есть весовой товар')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product1.product_id, 'product_id')
            tap.eq(s.weight, 75, 'вес')
            tap.eq(s.count, None, 'count')
            tap.eq(s.conditions.editable, True, 'editable')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.ok(await s.done(count=5, weight=78), 'завершён')

        with suggests[0] as s:
            tap.ok(await s.done(
                count=4,
                weight=60,
                reason={
                    'code': 'CHANGE_WEIGHT'
                }
            ), 'завершён')

        suggests = await dataset.Suggest.list_by_order(order, status='done')
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product1.product_id, 'product_id')
            tap.eq(s.result_weight, 60, 'вес')
            tap.eq(s.result_count, 4, 'count')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars('stowage_id', None), list, 'список дочек')
        tap.eq(len(order.vars('stowage_id')), 1, 'одна дочка')

        stowage = await dataset.Order.load(order.vars('stowage_id.0'))
        tap.ok(stowage, 'ордер раскладки есть')
        tap.eq(stowage.type, 'weight_stowage', 'тип ордера')

        tap.eq(len(stowage.required), 1, 'требования')

        with stowage.required[0] as r:
            tap.eq(r.product_id, product1.product_id, 'товар')
            tap.eq(r.count, 4, 'count')
            tap.eq(r.weight, 60, 'weight')
            tap.eq(r.result_weight, None, 'result_weight')
            tap.eq(r.result_count, None, 'result_count')


@pytest.mark.parametrize(
    'count,weight,exc',
    [
        [0, 78, Suggest.ErSuggestCount],
        [0, None, Suggest.ErSuggestCount],
        [3, 0, Suggest.ErSuggestWeightRequired],
        [None, 0, Suggest.ErSuggestWeightRequired],
    ]
)
async def test_no_stowage(tap, dataset, wait_order_status, count, weight, exc):
    with tap.plan(19, 'тестирование создания раскладки весового товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(type_accounting='weight')
        tap.ok(product1, 'товар создан')
        tap.eq(product1.type_accounting, 'weight', 'тип - весовой')

        product2 = await dataset.product(
            upper_weight_limit=150,
            lower_weight_limit=0,
            parent_id=product1.product_id,
        )
        tap.ok(product2, 'товар 2 создан')
        tap.eq(product2.parent_id, product1.product_id, 'parent_id')
        tap.eq(product2.upper_weight_limit, 150, 'upper_weight_limit')
        tap.eq(product2.lower_weight_limit, 0, 'lower_weight_limit')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=True,
            type='acceptance',
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 75,
                    'weight': 75,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product1.product_id, 'product_id')
            tap.eq(s.weight, 75, 'вес')
            tap.eq(s.count, 75, 'count')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            with tap.raises(exc, 'нельзя положить 0 товара.'):
                await s.done(count=count, weight=weight)

        tap.is_ok(order.vars('stowage_id', None),
                  None,
                  'выкладки не должно быть')
        tap.ok(await order.cancel(), 'отменяем ордер')

        await wait_order_status(order, ('canceled', 'done'))


async def test_weight_agree(tap, dataset, wait_order_status):
    with tap.plan(16, 'Доверительная приёмка с проверкой вес товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        weight = await dataset.weight_products()

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],

            required=[
                {
                    'product_id': weight[0].product_id,
                    'count': 27,
                }
            ]
        )

        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.type, 'acceptance', 'тип')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        with suggests[0] as s:
            tap.eq(s.conditions['need_weight'], True, 'need_weight')
            tap.ok(await s.done(count=10, weight=1000),
                   'закрыли саджест')

        tap.ok(await order.signal({'type': 'acceptance_agree'}),
               'сигнал отправлен')
        await wait_order_status(order, ('complete', 'done'))

        stowage = await dataset.Order.load(order.vars('stowage_id'))
        tap.ok(stowage, 'раскладка сгенерирована')
        tap.eq(len(stowage.required), 1, 'Одна запись required')
        required = stowage.required[0]

        tap.eq(required.count, 10, 'число по закрытому')
        tap.eq(required.weight, 1000, 'вес по закрытому')
        tap.eq(required.product_id, weight[0].product_id, 'продукт')


async def test_weight_prod_in_stowage(tap, dataset, wait_order_status):
    with tap.plan(29, 'тестирование создания раскладки весового товара '
                      'как просто раскладки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product1 = await dataset.product(type_accounting='weight')
        tap.ok(product1, 'товар создан')
        tap.eq(product1.type_accounting, 'weight', 'тип - весовой')

        product2 = await dataset.product(
            upper_weight_limit=150,
            lower_weight_limit=0,
            parent_id=product1.product_id,
            type_accounting='weight'
        )

        tap.ok(product2, 'товар 2 создан')
        tap.eq(product2.parent_id, product1.product_id, 'parent_id')
        tap.eq(product2.upper_weight_limit, 150, 'upper_weight_limit')
        tap.eq(product2.lower_weight_limit, 0, 'lower_weight_limit')
        tap.eq(product2.type_accounting, 'weight', 'тип - весовой')

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            approved=True,
            type='acceptance',
            required=[
                {
                    'product_id': product2.product_id,
                    'weight': 75,
                    'count': 13,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        with suggests[0] as s:
            tap.eq(s.product_id, product2.product_id, 'product_id')
            tap.eq(s.weight, 75, 'вес')
            tap.eq(s.count, 13, 'count')
            tap.eq(s.conditions.editable, True, 'editable')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.ok(await s.done(count=5, weight=78), 'завершён')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.isa_ok(order.vars('stowage_id', None), list, 'список дочек')
        tap.eq(len(order.vars('stowage_id')), 1, 'одна дочка')

        stowage = await dataset.Order.load(order.vars('stowage_id.0'))
        tap.ok(stowage, 'ордер раскладки есть')
        tap.eq(stowage.type, 'sale_stowage', 'тип ордера')

        tap.eq(len(stowage.required), 1, 'требования')

        with stowage.required[0] as r:
            tap.eq(r.product_id, product2.product_id, 'товар')
            tap.eq(r.count, 5, 'count')
            tap.eq(r.weight, 78, 'weight')
            tap.eq(r.result_weight, None, 'result_weight')
            tap.eq(r.result_count, None, 'result_count')
