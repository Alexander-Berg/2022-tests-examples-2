import pytest


# pylint: disable=too-many-statements,too-many-locals
async def test_inventory_make_orders(tap, dataset, wait_order_status, lp):
    with tap.plan(80, 'Тест создания дочек'):
        tap.note('родитель')
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        disabled_shelf = await dataset.shelf(status='disabled', store=store)
        tap.eq(disabled_shelf.store_id, store.store_id, 'отключенная полка')

        lost_shelf = await dataset.shelf(
            store=store,
            type='lost',
        )
        tap.ok(lost_shelf, 'полка lost')

        found_shelf = await dataset.shelf(
            store=store,
            type='found',
        )
        tap.ok(found_shelf, 'полка found')

        kitchen_lost = await dataset.shelf(
            store=store,
            type='kitchen_lost',
        )
        tap.ok(kitchen_lost, 'полка kitchen_lost')

        kitchen_found = await dataset.shelf(
            store=store,
            type='kitchen_found',
        )
        tap.ok(kitchen_found, 'полка kitchen_found')

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')

        usual_shelf = await dataset.shelf(
            store=store, type='store', rack='my_rack'
        )
        tap.ok(usual_shelf, 'Обычная полка со стеллажом')
        kitchen_shelf = await dataset.shelf(
            store=store, type='kitchen_components', title='best kitchen shelf'
        )
        tap.ok(kitchen_shelf, 'Кухонная полка с названием')

        stock = await dataset.stock(shelf=usual_shelf, quants=300)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        kitchen_stock = await dataset.stock(
            shelf=kitchen_shelf,
            count=120,
            quants=123,
        )
        tap.ok(kitchen_stock, 'Остаток на кухне')

        found_stock = await dataset.stock(
            product_id=stock.product_id,
            count=20,
            shelf=found_shelf
        )
        tap.ok(found_stock, 'сток на found полке')

        await wait_order_status(order, ('processing', 'waiting'))

        children = await dataset.Order.list(
            by='full',
            conditions=('order_id', order.vars('child_orders')),
        )
        children = children.list

        tap.eq(
            len(children),
            2,
            'два дочерних ордера'
        )

        tap.note('первый потомок')
        child = next(filter(lambda x: stock.shelf_id in x.shelves, children))
        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(
            child.attr.get('humanized_title'),
            'my_rack',
            'В названии стеллаж',
        )
        tap.eq(child.shelves, [stock.shelf_id], 'полки')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(r.shelf_id, stock.shelf_id, 'инвентаризация полки')
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')
        tap.ok(await suggests[0].done(product_id=product.product_id, count=21),
               'закрыли саджест')
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(child,
                                ('complete', 'wait_child_done'),
                                user_done=user)

        tap.note('Внучёк')
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.eq(
            child2.attr.get('humanized_title'),
            'my_rack',
            'В названии наследовался стеллаж',
        )
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=27), 'завершаем саджест')
        await wait_order_status(child2,
                                ('complete', 'done'),
                                user_done=user)

        tap.note('Снова потомок')
        await wait_order_status(child,
                                ('complete', 'done'),
                                user_done=user)

        tap.note('Второй потомок')
        child = next(filter(
            lambda x: kitchen_stock.shelf_id in x.shelves,
            children
        ))
        tap.eq(
            child.attr.get('humanized_title'),
            'best kitchen shelf',
            'Название полки в тайтле ордера'
        )
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один саджест')

        tap.ok(
            await suggests[0].done(
                product_id=kitchen_stock.product_id, count=37),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')

        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
            user_done=user
        )

        tap.note('Внучёк')
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=27), 'завершаем саджест')
        await wait_order_status(child2,
                                ('complete', 'done'),
                                user_done=user)

        tap.note('Снова потомок')
        await wait_order_status(child,
                                ('complete', 'done'),
                                user_done=user)

        tap.note('основной ордер')
        await wait_order_status(order, ('processing', 'waiting_signal'))

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot=snapshot.list
        res_count = dict((p.product_id, p.result_count) for p in snapshot)
        tap.eq(res_count,
               {
                   stock.product_id: None,
                   kitchen_stock.product_id: None,
               },
               'фин снапшота ещё не было')
        tap.eq(
            {p.quants for p in snapshot},
            {1, 123, 300},
            'Кванты заполнены'
        )
        snapshot_events = [
            event
            for event in lp.pytest_cache
            if event.data['type'] == 'snapshot_generated'
        ]
        tap.eq(
            len(snapshot_events),
            0,
            'Ивентов снапшота к этому моменту не было'
        )
        tap.ok(await order.signal({'type': 'inventory_snapshot'}),
               'сигнал снапшота')
        await wait_order_status(order, ('processing', 'waiting_signal'))

        snapshot_events = [
            event
            for event in lp.pytest_cache
            if event.data['type'] == 'snapshot_generated'
        ]
        tap.eq(
            len(snapshot_events),
            1,
            'Один ивент снапшота'
        )
        event = snapshot_events[0]
        tap.eq(
            (event.key, event.data['order_id']),
            (['order', 'store', store.store_id], order.order_id),
            'Сигнал с нужным ключом и ордером'
        )

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot=snapshot.list

        res_count = {
            (p.shelf_type, p.product_id, p.result_count)
            for p in snapshot
        }
        tap.eq(res_count,
               {
                   ('found', product.product_id, 27),
                   ('store', product.product_id, 27),
                   ('found', stock.product_id, 20),
                   ('store', stock.product_id, 27),
                   ('lost', stock.product_id, 76),
                   ('kitchen_components', kitchen_stock.product_id, 27),
                   ('kitchen_lost', kitchen_stock.product_id, 93),
               },
               'снапшот сгенерился')

        tap.ok(await order.signal({'type': 'inventory_done',
                                   'data': {'user': user.user_id}}),
               'сигнал завершения')
        await wait_order_status(order, ('complete', 'done'))
        tap.eq(order.user_done, user.user_id, 'user_done is set')

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot=snapshot.list
        tap.ok(snapshot, 'снапшот получен')
        tap.eq(
            len(snapshot),
            7,
            '1 товар на полках store и found,'
            '2 товар на полках lost, store и found,'
            '1 на кухне и 1 на потерях кухни'
        )

        res_count = {
            (p.shelf_type, p.product_id, p.result_count)
            for p in snapshot
        }
        tap.eq(
            res_count,
            {
                ('found', product.product_id, 27),
                ('store', product.product_id, 27),
                ('found', stock.product_id, 20),
                ('store', stock.product_id, 27),
                ('lost', stock.product_id, 76),
                ('kitchen_components', kitchen_stock.product_id, 27),
                ('kitchen_lost', kitchen_stock.product_id, 93),
            },
            'товарам поставлено количество'
        )

        counts = {(p.shelf_type, p.product_id, p.count) for p in snapshot}
        tap.eq(
            counts,
            {
                ('store', product.product_id, None),
                ('store', stock.product_id, stock.count),
                ('lost', stock.product_id, None),
                ('found', product.product_id, None),
                ('found', stock.product_id, 20),
                ('kitchen_components', kitchen_stock.product_id, 120),
                ('kitchen_lost', kitchen_stock.product_id, None),
            },
            'начальное количество'
        )

        virtual_stocks = await dataset.Stock.list_by_shelf(
            shelf_id=[
                shelf.shelf_id
                for shelf in (
                    lost_shelf,
                    found_shelf,
                    kitchen_found,
                    kitchen_lost
                )
            ],
            store_id=store.store_id,
            empty=False,
        )
        tap.eq(
            len(virtual_stocks),
            0,
            'Нет непустых остатков на виртуальных полках'
        )


async def test_inventory_trash(tap, dataset, wait_order_status):
    with tap.plan(54, 'Тест инвы с трэшовой полкой'):
        store = await dataset.store(estatus='inventory')
        user = await dataset.user(store=store)
        await dataset.shelf(
            store=store,
            type='kitchen_lost',
        )
        await dataset.shelf(
            store=store,
            type='kitchen_found',
        )
        lost_shelf = await dataset.shelf(
            store=store,
            type='lost',
        )
        found_shelf = await dataset.shelf(
            store=store,
            type='found',
        )
        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        trash_shelf = await dataset.shelf(store=store, type='trash')
        kitchen_trash = await dataset.shelf(store=store, type='kitchen_trash')
        trash_stock = await dataset.stock(shelf=trash_shelf, count=13)
        quant_product = await dataset.product(quants=100)
        kitchen_stock = await dataset.stock(
            product_id=quant_product.product_id,
            shelf=kitchen_trash,
            count=120,
            quants=100,
        )

        await wait_order_status(order, ('processing', 'waiting'))

        children = (await dataset.Order.list(
            by='full',
            conditions=('order_id', order.vars('child_orders')),
        )).list
        tap.eq(len(children), 2, 'два дочерних')
        child = next(filter(
            lambda x: trash_stock.shelf_id in x.shelves,
            children
        ))
        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(child.shelves, [trash_shelf.shelf_id], 'полка')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(r.shelf_id, trash_stock.shelf_id, 'инвентаризация полки')
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
            user_done=user
        )
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=0), 'завершаем саджест')
        await wait_order_status(
            child2,
            ('complete', 'done'),
            user_done=user
        )
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        child = next(filter(
            lambda x: kitchen_stock.shelf_id in x.shelves,
            children
        ))
        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
            user_done=user
        )
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=220), 'завершаем саджест')
        await wait_order_status(
            child2,
            ('complete', 'done'),
            user_done=user
        )
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        await wait_order_status(order, ('processing', 'waiting_signal'))
        tap.ok(
            await order.signal({
                'type': 'inventory_done',
                'data': {'user': user.user_id}
            }),
            'сигнал завершения'
        )
        await wait_order_status(order, ('complete', 'done'))
        snapshot = (await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )).list
        tap.ok(snapshot, 'снапшот получен')
        tap.eq(
            len(snapshot),
            4,
            '1 товар на полках trash и lost,'
            '1 товар кухни на trash и found'
        )
        res_count = {
            (p.shelf_type, p.product_id, p.result_count)
            for p in snapshot
        }
        tap.eq(
            res_count,
            {
                ('lost', trash_stock.product_id, 13),
                ('trash', trash_stock.product_id, 0),
                ('kitchen_found', quant_product.product_id, 100),
                ('kitchen_trash', quant_product.product_id, 220),
            },
            'товарам поставлено количество'
        )

        counts = {(p.shelf_type, p.product_id, p.count) for p in snapshot}
        tap.eq(
            counts,
            {
                ('lost', trash_stock.product_id, None),
                ('trash', trash_stock.product_id, 13),
                ('kitchen_found', quant_product.product_id, None),
                ('kitchen_trash', quant_product.product_id, 120),
            },
            'начальное количество'
        )

        virtual_stocks = await dataset.Stock.list_by_shelf(
            shelf_id=[
                shelf.shelf_id
                for shelf in (
                    lost_shelf,
                    found_shelf,
                )
            ],
            store_id=store.store_id,
            empty=False,
        )
        tap.eq(
            len(virtual_stocks),
            0,
            'Нет непустых остатков на виртуальных полках'
        )
        tap.ok(await trash_stock.reload(), 'Перезабрали остаток')
        tap.eq(trash_stock.count, 0, 'Снесли с остатков')
        tap.ok(await kitchen_stock.reload(), 'Перезабрали остаток')
        tap.eq(kitchen_stock.count, 220, 'Остаток кухни 220')


# pylint: disable=too-many-statements,too-many-locals
@pytest.mark.parametrize('shelf_type', ['markdown', 'repacking'])
async def test_inventory_shelf_types(
    tap, dataset, wait_order_status, shelf_type
):
    with tap.plan(52, 'Тест создания дочек для типов полок'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        lost_shelf = await dataset.shelf(store=store, type='lost')
        tap.ok(lost_shelf, 'полка lost')

        found_shelf = await dataset.shelf(store=store, type='found')
        tap.ok(found_shelf, 'полка found')

        shelf = await dataset.shelf(store=store, type=shelf_type)
        tap.ok(shelf, 'Полка списания создана')

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'shelf_types': ['markdown', 'repacking']}
        )
        tap.eq(
            order.fstatus,
            ('reserving', 'begin'),
            'ордер инвентаризации создан'
        )

        stock = await dataset.stock(store=store, quants=250)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        found_stock = await dataset.stock(
            product_id=stock.product_id,
            count=20,
            shelf=found_shelf
        )
        tap.ok(found_stock, 'сток на found полке')
        shelf_stock = await dataset.stock(
            product_id=stock.product_id,
            count=12,
            shelf=shelf
        )
        tap.ok(shelf_stock, 'сток на уценке')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(
            len(order.vars('child_orders')),
            1,
            'один дочерний ордер создан'
        )

        child = await dataset.Order.load(order.vars('child_orders.0'))
        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(child.shelves, [shelf.shelf_id], 'полки')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(
                r.shelf_id,
                shelf.shelf_id,
                'инвентаризация полки'
            )
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')

        tap.ok(
            await suggests[0].done(
                product_id=stock.product_id,
                count=22
            ),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
            user_done=user
        )

        tap.note('Внучёк')
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=27), 'завершаем саджест')
        await wait_order_status(
            child2,
            ('complete', 'done'),
            user_done=user
        )

        await wait_order_status(
            child,
            ('complete', 'done'),
            user_done=user
        )

        tap.note('основной ордер')
        await wait_order_status(order, ('processing', 'waiting_signal'))

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot = snapshot.list
        res_count = dict((p.product_id, p.result_count) for p in snapshot)
        tap.eq(
            res_count,
            {stock.product_id: None},
            'фин снапшота ещё не было'
        )
        tap.eq({p.quants for p in snapshot}, {1, 250}, 'Кванты заполнены')
        tap.ok(
            await order.signal({'type': 'inventory_snapshot'}),
            'сигнал снапшота'
        )
        await wait_order_status(order, ('processing', 'waiting_signal'))

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot = snapshot.list

        res_count = {
            (p.shelf_type, p.product_id, p.result_count)
            for p in snapshot
        }
        tap.eq(
            res_count,
            {
                ('found', stock.product_id, 35),
                ('store', stock.product_id, 103),
                (shelf_type, stock.product_id, 27),
            },
            'снапшот сгенерился'
        )

        tap.ok(
            await order.signal({
                'type': 'inventory_done',
                'data': {'user': user.user_id}
            }),
            'сигнал завершения'
        )
        await wait_order_status(order, ('complete', 'done'))
        tap.eq(order.user_done, user.user_id, 'user_done is set')

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot = snapshot.list
        tap.ok(snapshot, 'снапшот получен')
        tap.eq(
            len(snapshot),
            3,
            f'1 товар на полках store, found, {shelf_type}'
        )

        res_count = {
            (p.shelf_type, p.product_id, p.result_count)
            for p in snapshot
        }
        tap.eq(
            res_count,
            {
                ('found', stock.product_id, 35),
                ('store', stock.product_id, 103),
                (shelf_type, stock.product_id, 27),
            },
            'товарам поставлено количество'
        )

        counts = {(p.shelf_type, p.product_id, p.count) for p in snapshot}
        tap.eq(
            counts,
            {
                ('store', stock.product_id, stock.count),
                (shelf_type, stock.product_id, shelf_stock.count),
                ('found', stock.product_id, 20),
            },
            'начальное количество'
        )

        lost_stocks = await dataset.Stock.list_by_shelf(
            shelf_id=lost_shelf.shelf_id,
            store_id=store.store_id,
            empty=False,
        )
        tap.eq(len(lost_stocks), 0, 'Нет непустых остатков на lost полке')

        found_stocks = await dataset.Stock.list_by_shelf(
            shelf_id=found_shelf.shelf_id,
            store_id=store.store_id,
            empty=False,
        )
        tap.eq(len(found_stocks), 0, 'Нет непустых остатков на found полке')


async def test_inventory_close_no_count(tap, dataset, wait_order_status):
    with tap.plan(33, 'Тест закрытия пустой полки'):
        tap.note('родитель')
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store)

        lost_shelf = await dataset.shelf(
            store=store,
            type='lost',
        )
        tap.ok(lost_shelf, 'полка lost')

        found_shelf = await dataset.shelf(
            store=store,
            type='found',
        )
        tap.ok(found_shelf, 'полка found')

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.note('первый потомок')
        tap.eq(len(order.vars('child_orders')),
               1,
               'один дочерний ордер создан')

        child = await dataset.Order.load(order.vars('child_orders.0'))
        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(child.shelves, [stock.shelf_id], 'полки')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(r.shelf_id, stock.shelf_id, 'инвентаризация полки')
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'один штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
            user_done=user
        )

        tap.note('Внучёк')
        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=None), 'завершаем саджест')
        await wait_order_status(
            child2,
            ('complete', 'done'),
            user_done=user
        )

        await wait_order_status(
            child,
            ('complete', 'done'),
            user_done=user
        )

        tap.note('основной ордер')
        await wait_order_status(order, ('processing', 'waiting_signal'))

        tap.ok(
            await order.signal({
                'type': 'inventory_done',
                'data': {'user': user.user_id}
            }),
            'сигнал завершения'
        )
        await wait_order_status(order, ('complete', 'done'))
        stocks = await dataset.Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('product_id', stock.product_id),
                ('shelf_type', stock.shelf_type)
            ],
            sort=(),
        )
        tap.eq(
            sum(stock.count for stock in stocks),
            0,
            'Опустошили полку'
        )
