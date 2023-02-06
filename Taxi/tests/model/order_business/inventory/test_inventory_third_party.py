# pylint: disable=too-many-statements,too-many-locals
async def test_inventory_make_orders(tap, dataset, wait_order_status):
    with tap.plan(121, 'Тест создания дочек'):
        async def send_report(order, rows):
            stash_name = f'inventory_report-{order.order_id}'
            tap.ok(
                await dataset.Stash.stash(name=stash_name, rows=rows),
                'Сохранили отчет'
            )
            tap.ok(
                await order.signal(
                    {'type': 'inventory_report_imported'},
                    user=user
                ),
                'Сигнал отправлен'
            )

        tap.note('Родитель')
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

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'third_party_assistance': True}
        )
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')

        stock_one = await dataset.stock(store=store, quants=300, count=102)
        tap.eq(stock_one.store_id, store.store_id, 'остаток создан')

        stock_two = await dataset.stock(store=store, quants=222, count=34)
        tap.eq(stock_two.store_id, store.store_id, 'второй остаток создан')

        stock_three = await dataset.stock(
            store=store,
            shelf_id=stock_two.shelf_id,
            product_id=stock_one.product_id,
            count=111,
            quants=300,
        )
        tap.eq(stock_three.store_id, store.store_id, 'третий остаток создан')

        product = await dataset.product()
        empty_stock = await dataset.stock(
            store=store,
            shelf_id=stock_two.shelf_id,
            product_id=product.product_id,
            count=0,
        )
        tap.ok(empty_stock, 'Создали пустой остаток')

        found_stock = await dataset.stock(
            product_id=stock_one.product_id,
            count=20,
            shelf=found_shelf,
            quants=300,
        )
        tap.ok(found_stock, 'сток на found полке')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.note('первый потомок')
        tap.eq(
            len(order.vars('child_orders')),
            2,
            'два дочерних ордера создано'
        )

        for child_id in order.vars('child_orders'):
            child = await dataset.Order.load(child_id)
            if stock_one.shelf_id in child.shelves:
                break

        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(child.shelves, [stock_one.shelf_id], 'полки')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(r.shelf_id, stock_one.shelf_id, 'инвентаризация полки')
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'одна штука')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')
        tap.ok(
            await suggests[0].done(product_id=stock_one.product_id, count=102),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'одна штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('processing', 'waiting_signal'),
        )
        tap.eq(
            child.vars('report', None),
            {
                stock_one.shelf_id: {
                    stock_one.product_id: {
                        'count': 102,
                        'result_count': 102
                    }
                }
            },
            'Отчет по начальным данным'
        )

        stock_product = await dataset.Product.load(stock_one.product_id)
        stock_shelf = await dataset.Shelf.load(stock_one.shelf_id)
        await send_report(
            child,
            [{
                'product': stock_product.external_id,
                'shelf': stock_shelf.title,
                'count': 10
            }]
        )
        tap.ok(
            await wait_order_status(child, ('processing', 'waiting_signal')),
            'В статусе ожидания сигнала'
        )
        # повторно загрузим отчет
        await send_report(
            child,
            [{
                'product': stock_product.external_id,
                'shelf': stock_shelf.title,
                'count': 102
            }]
        )
        tap.ok(
            await wait_order_status(child, ('processing', 'waiting_signal')),
            'В статусе ожидания сигнала'
        )
        tap.eq(
            child.vars('report', None),
            {
                stock_one.shelf_id: {
                    stock_one.product_id: {
                        'count': 102,
                        'result_count': 102,
                        'tp_count': 102
                    }
                }
            },
            'Итоговый отчет'
        )

        tap.ok(
            await child.signal({'type': 'inventory_recount'}),
            'Сигнал на пересчет без расхождений'
        )
        tap.ok(
            await wait_order_status(child, ('processing', 'waiting_signal')),
            'В статусе ожидания сигнала'
        )
        tap.ok(
            await child.signal({'type': 'inventory_approve'}),
            'Сигнал на подтверждение отчета'
        )
        tap.ok(
            await wait_order_status(
                child,
                ('complete', 'done'),
            ),
            'Закрылся первый дочерний ордер'
        )
        tap.not_in_ok(
            'child_order_id',
            child.vars,
            'Нет внука'
        )

        tap.note('Второй дочерний')

        for child_id in order.vars('child_orders'):
            child = await dataset.Order.load(child_id)
            if stock_two.shelf_id in child.shelves:
                break

        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        tap.eq(child.type, 'inventory_check_more', 'тип ордера')
        tap.eq(child.shelves, [stock_two.shelf_id], 'полки')
        tap.eq(len(child.required), 1, 'длина required')
        tap.eq(child.store_id, order.store_id, 'на том же складе')
        with child.required[0] as r:
            tap.eq(r.shelf_id, stock_two.shelf_id, 'инвентаризация полки')
            tap.eq(r.product_id, None, 'product_id не заполнен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'одна штука')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')
        tap.ok(
            await suggests[0].done(product_id=stock_two.product_id, count=34),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.eq(len(suggests), 1, 'одна штука')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(
            child,
            ('processing', 'waiting_signal'),
        )
        tap.eq(
            child.vars('report', None),
            {
                stock_two.shelf_id: {
                    stock_two.product_id: {
                        'count': 34,
                        'result_count': 34,
                    },
                    stock_three.product_id: {
                        'count': 111,
                    }
                }
            },
            'Отчет по начальным данным'
        )
        tap.ok(
            await child.signal({'type': 'inventory_approve'}),
            'Сигнал на подтверждение отчета'
        )
        await wait_order_status(child, ('processing', 'waiting_signal'))
        tap.ok(
            await child.signal({'type': 'inventory_recount'}),
            'Сигнал на контрольный пересчет'
        )
        await wait_order_status(
            child,
            ('complete', 'wait_child_done'),
        )
        tap.note('Дочерний второго дочернего')
        child2 = await dataset.Order.load(child.vars['child_order_id'])
        tap.ok(child2, 'Внук создан')

        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=27), 'завершаем саджест')

        await wait_order_status(
            child2,
            ('processing', 'waiting_signal'),
        )

        tap.eq(
            child2.vars('report', None),
            {
                stock_two.shelf_id: {
                    stock_two.product_id: {
                        'count': 34,
                        'result_count': 27
                    },
                    stock_three.product_id: {
                        'count': 111,
                        'result_count': 27,
                    }
                }
            },
            'Отчет по начальным данным'
        )

        stock_product = await dataset.Product.load(stock_two.product_id)
        stock_product_two = await dataset.Product.load(stock_three.product_id)
        stock_shelf = await dataset.Shelf.load(stock_two.shelf_id)
        await send_report(
            child2,
            [
                {
                    'product': stock_product.external_id,
                    'shelf': stock_shelf.title,
                    'count': 27
                },
                {
                    'product': stock_product_two.external_id,
                    'shelf': stock_shelf.title,
                    'count': 28
                },
            ]
        )
        await wait_order_status(child2, ('processing', 'waiting_signal'))

        tap.eq(
            child2.vars('report', None),
            {
                stock_two.shelf_id: {
                    stock_two.product_id: {
                        'count': 34,
                        'result_count': 27,
                        'tp_count': 27,
                    },
                    stock_three.product_id: {
                        'count': 111,
                        'result_count': 27,
                        'tp_count': 28,
                    }
                }
            },
            'Отчет по итоговый'
        )

        tap.ok(
            await child2.signal({'type': 'inventory_recount'}),
            'Сигнал на контрольный пересчет'
        )
        await wait_order_status(
            child2,
            ('complete', 'wait_child_done'),
        )
        tap.note('Правнук')
        child3 = await dataset.Order.load(child2.vars['child_order_id'])
        tap.ok(child3, 'Правнук создан')

        await wait_order_status(child3, ('request', 'waiting'))
        tap.ok(await child3.ack(user), 'берём заказ')
        await wait_order_status(child3, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child3)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=10), 'завершаем саджест')
        await wait_order_status(
            child3,
            ('processing', 'waiting_signal'),
        )
        tap.ok(
            await child3.signal({'type': 'inventory_approve'}),
            'Сигнал на применение пересчета с расхождением'
        )
        await wait_order_status(child3, ('processing', 'waiting_signal'))
        await send_report(
            child3,
            [
                {
                    'product': stock_product.external_id,
                    'shelf': stock_shelf.title,
                    'count': 12
                },
                {
                    'product': stock_product_two.external_id,
                    'shelf': stock_shelf.title,
                    'count': 10
                },
            ]
        )
        await wait_order_status(child3, ('processing', 'waiting_signal'))
        tap.ok(
            await child3.signal({'type': 'inventory_approve'}),
            'Сигнал на применение пересчета без расхождений'
        )

        tap.ok(
            await wait_order_status(child3, ('complete', 'done')),
            'Правнук закрыт'
        )
        tap.ok(
            await wait_order_status(child2, ('complete', 'done')),
            'Внук закрыт'
        )
        tap.ok(
            await wait_order_status(child, ('complete', 'done')),
            'Второй дочерний закрыт'
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
            {
                stock_one.product_id: None,
                stock_two.product_id: None
            },
            'фин снапшота ещё не было'
        )
        tap.eq({p.quants for p in snapshot}, {300, 222}, 'Кванты заполнены')
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
                ('lost', stock_two.product_id, 7),
                ('lost', stock_three.product_id, 101),
                ('store', stock_two.product_id, 27),
                ('store', stock_one.product_id, 112),
                ('found', found_stock.product_id, 20),
            },
            'снапшот сгенерился'
        )

        tap.ok(
            await order.signal(
                {'type': 'inventory_done', 'data': {'user': user.user_id}}),
            'сигнал завершения'
        )
        await wait_order_status(
            order, ('complete', 'done'))
        tap.eq(order.user_done, user.user_id, 'user_done is set')

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot = snapshot.list
        tap.ok(snapshot, 'снапшот получен')
        tap.eq(
            len(snapshot),
            5,
            '1 товар на полках found,'
            '2 товара на полках store, '
            '2 товара на полке lost'
        )

        counts = {(p.shelf_type, p.product_id, p.count) for p in snapshot}
        tap.eq(
            counts,
            {
                ('store', stock_one.product_id, 213),
                ('lost', stock_two.product_id, None),
                ('found', found_stock.product_id, 20),
                ('store', stock_two.product_id, 34),
                ('lost', stock_three.product_id, None)
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
