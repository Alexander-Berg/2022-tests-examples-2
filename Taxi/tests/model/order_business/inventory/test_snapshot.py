# pylint: disable=too-many-statements,too-many-locals,unused-argument
import asyncio


async def test_empty_after_double_recount(tap, dataset, wait_order_status, job):
    with tap.plan(48, 'Тест обнуления полки'):
        tap.note('родитель')
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

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

        stock = await dataset.stock(store=store, count=31)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        empty_stock = await dataset.stock(
            store=store,
            count=0,
            shelf_id=stock.shelf_id
        )
        tap.eq(empty_stock.store_id, store.store_id, 'пустой остаток создан')

        assortment_contractor = await dataset.assortment_contractor(store=store)
        for pid in (stock.product_id, empty_stock.product_id):
            await dataset.assortment_contractor_product(
                assortment=assortment_contractor,
                product_id=pid,
                price=69,
            )

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        tap.eq(
            order.fstatus,
            ('reserving', 'begin'),
            'ордер инвентаризации создан'
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.note('пересчитаем в двойное количество')
        child = await dataset.Order.load(order.vars('child_orders.0'))
        tap.eq(child.store_id, store.store_id, 'дочерний ордер загружен')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'берём заказ')
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child)
        tap.ok(suggests, 'саджесты сгенерированы')

        tap.ok(
            await suggests[0].done(product_id=stock.product_id, count=37),
            'закрыли саджест'
        )
        await wait_order_status(child, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(child, status='request')
        tap.ok(suggests, 'саджесты сгенерированы')
        tap.ok(await suggests[0].done(status='error'), 'закрыли саджест')
        await wait_order_status(child,
                                ('complete', 'wait_child_done'),
                                user_done=user)

        child2 = await dataset.Order.load(child.vars('child_order_id'))
        tap.ok(child2, 'внук загружен')
        await wait_order_status(child2, ('request', 'waiting'))
        tap.ok(await child2.ack(user), 'берём заказ')
        await wait_order_status(child2, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(child2)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=67), 'завершаем саджест')
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
        tap.eq(
            len(snapshot),
            1,
            'Только одна запись'
        )
        record = snapshot[0]
        tap.eq(
            record.updated,
            record.created,
            'Запись только создали'
        )
        saved_updated = record.updated
        tap.eq(
            record.count,
            31,
            'Правильное количество'
        )
        tap.eq(
            record.result_count,
            None,
            'Факта еще нет'
        )
        tap.eq(record.price, 69, 'цена nice')
        await asyncio.sleep(1)

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
        tap.eq(
            len(snapshot),
            2,
            'Новые данные в снапшоте'
        )
        tap.eq(
            sorted(
                [
                    record.shelf_type,
                    record.count,
                    record.result_count,
                    record.price,
                ]
                for record in snapshot
            ),
            [['found', None, 36, 69], ['store', 31, 67, 69]],
            'Данные в снапшоте'
        )
        store_record = next(
            filter(lambda a: a.shelf_type == 'store', snapshot))
        tap.ne(
            store_record.updated,
            saved_updated,
            'Изменилось время обновления'
        )
        tap.note('Пересчетаем полку в ноль')
        new_order = await dataset.order(
            type='inventory_check_product_on_shelf',
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            required=[{
                'shelf_id': stock.shelf_id,
                'product_id': stock.product_id,
                'count': 22,
            }]
        )
        tap.ok(new_order, 'Пересчетный ордер бесхозный')
        await wait_order_status(new_order, ('request', 'waiting'))
        tap.ok(await new_order.ack(user), 'берём заказ')
        await wait_order_status(new_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(new_order)
        tap.ok(suggests, 'саджесты сгенерированы')
        for s in suggests:
            tap.ok(await s.done(count=0), 'завершаем саджест')
        await wait_order_status(
            new_order,
            ('complete', 'done'),
            user_done=user
        )
        tap.ok(
            await order.signal({
                'type': 'inventory_done',
                'data': {'user': user.user_id}
            }),
            'сигнал завершения'
        )
        await wait_order_status(order, ('complete', 'done'))
        tap.note('проверим снапшот')
        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        snapshot = snapshot.list
        tap.eq(
            len(snapshot),
            3,
            'Добавилась lost полка в снапшот'
        )
        tap.eq(
            sorted(
                [
                    record.shelf_type,
                    record.count,
                    record.result_count,
                    record.price
                ]
                for record in snapshot
            ),
            [
                ['found', None, 36, 69],
                ['lost', None, 67, 69],
                ['store', 31, 0, 69]
            ],
            'Не потеряли опустошение полки'
        )


async def test_snapshot_many_assortments(tap, dataset, wait_order_status):
    with tap.plan(4, 'один товар во многих ассортиментах при инве'):
        store = await dataset.store(estatus='inventory')

        stock = await dataset.stock(
            store=store, count=100,
        )

        ass1 = await dataset.assortment_contractor(store=store)
        ass2 = await dataset.assortment_contractor(store=store)
        await dataset.assortment_contractor_product(
            assortment=ass1,
            product_id=stock.product_id,
            price=None,
        )
        await dataset.assortment_contractor_product(
            assortment=ass2,
            product_id=stock.product_id,
            price=69,
        )

        order = await dataset.order(
            store=store,
            type='inventory',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        snapshot = (await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )).list

        tap.eq(snapshot[0].product_id, stock.product_id, 'тот продукт')
        tap.eq(snapshot[0].price, 69, 'цена nice')
        tap.eq(snapshot[0].count, 100, 'count')
