from stall.model.suggest import Suggest


async def test_waiting_suggests_write_off(tap, uuid, dataset):
    with tap.plan(22, 'Генерация саджестов положить на полку списания'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

        trash  = await dataset.shelf(store=store, type='trash', order=3)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='processing',
            estatus='suggests_write_off',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_write_off', 'suggests_write_off')
        tap.eq(order.target, 'complete', 'target: complete')

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf2,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        suggest1 = await dataset.suggest(
            order,
            type='shelf2box',
            shelf_id=shelf1.shelf_id,
            product_id=product1.product_id,
            count=10,
            result_count=10,
            status='done',
        )
        tap.ok(suggest1, 'Саджест 1')
#         tap.ok(await suggest1.done(status='done'), 'Закрыли саджест')

        suggest2 = await dataset.suggest(
            order,
            type='shelf2box',
            shelf_id=shelf2.shelf_id,
            product_id=product2.product_id,
            count=20,
            result_count=20,
            status='done',
        )
        tap.ok(suggest2, 'Саджест 2')
#         tap.ok(await suggest2.done(status='done'), 'Закрыли саджест')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(
            order,
            types=['box2shelf'],
        )
        suggests = dict((s.product_id, s) for s in suggests)
        tap.eq(len(suggests), 2, 'Саджесты на полку списания')

        with suggests[product1.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'box2shelf')
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product1.product_id, 'product_id')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf_id')
            tap.eq(suggest.count, 10, 'count')

        with suggests[product2.product_id] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'box2shelf')
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product2.product_id, 'product_id')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf_id')
            tap.eq(suggest.count, 20, 'count')
