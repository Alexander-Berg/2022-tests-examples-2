from stall.model.suggest import Suggest


async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(9, 'Обновление required после успешного выполнения'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'count': 5,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_count=4,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')
        tap.eq(order.required[0].result_weight, None, 'Вес до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, 4, 'Итоговое количество')
        tap.eq(order.required[0].result_weight, None, 'Итоговый вес')

async def test_double_product_in_suggests(tap, dataset, wait_order_status):
    with tap.plan(7, 'Обновление required с нескольких полок'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf1 = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'count': 10,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf1.shelf_id,
            product_id=product.product_id,
            result_count=5,
        )
        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf2.shelf_id,
            product_id=product.product_id,
            result_count=2,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, 7, 'Итоговое количество')

async def test_double_required(tap, dataset, wait_order_status):
    with tap.plan(9, 'Обновление required с повторным продуктом'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'count': 5,
            }, {
                'product_id': product.product_id,
                'count': 2,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_count=7,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')
        tap.eq(order.required[1].result_count, None, 'Количество до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, 5, 'Итоговое required 1')
        tap.eq(order.required[1].result_count, 2, 'Итоговое required 2')

async def test_many_required_many_suggest(tap, dataset, wait_order_status):
    with tap.plan(11, 'С повторными продуктами и разбросом по полкам'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf1 = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)
        shelf3 = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'count': 5,
            }, {
                'product_id': product.product_id,
                'count': 2,
            }, {
                'product_id': product.product_id,
                'count': 0,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf1.shelf_id,
            product_id=product.product_id,
            result_count=3,
        )
        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf2.shelf_id,
            product_id=product.product_id,
            result_count=3,
        )
        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf3.shelf_id,
            product_id=product.product_id,
            result_count=0,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')
        tap.eq(order.required[1].result_count, None, 'Количество до')
        tap.eq(order.required[2].result_count, None, 'Количество до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, 5, 'Итоговое required 1')
        tap.eq(order.required[1].result_count, 1, 'Итоговое required 2')
        tap.eq(order.required[2].result_count, 0, 'Итоговое required 3')

async def test_order_changes(tap, dataset, wait_order_status):
    with tap.plan(7, 'С изменением запрашиваемого количества'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'count': 3,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_count=3,
        )
        await dataset.suggest(
            order,
            status='done',
            type='box2shelf',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_count=2,
        )
        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_count=1,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, 2, 'Итоговое количество товара')

async def test_weight(tap, dataset, wait_order_status):
    with tap.plan(9, 'Обновление required после успешного выполнения'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store)

        order = await dataset.order(
            store=store,
            type='order',
            status='complete',
            estatus='unreserve',
            required = [{
                'product_id': product.product_id,
                'weight': 100,
            }],
        )
        tap.ok(order, 'Заказ создан')

        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_weight=90,
        )
        await dataset.suggest(
            order,
            status='done',
            type='box2shelf',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_weight=90,
        )
        await dataset.suggest(
            order,
            status='done',
            type='shelf2box',
            shelf_id=shelf.shelf_id,
            product_id=product.product_id,
            result_weight=80,
        )
        suggests = await Suggest.list_by_order(order, status=['done'])
        tap.ok(len(suggests), "Саджесты созданы")

        await wait_order_status(
            order,
            ('complete', 'update_required'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Количество до')
        tap.eq(order.required[0].result_weight, None, 'Вес до')

        await wait_order_status(
            order,
            ('complete', 'suggests_drop'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(order.required[0].result_count, None, 'Итоговое количество')
        tap.eq(order.required[0].result_weight, 80, 'Итоговый вес')
