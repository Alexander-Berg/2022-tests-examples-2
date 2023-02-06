from datetime import date

from stall.model.suggest import Suggest


async def test_suggests_generate(tap, uuid, dataset, wait_order_status):
    with tap.plan(26, 'Генерация новых саджестов'):

        product = await dataset.product(valid=10)

        store = await dataset.store()

        shelf = await dataset.shelf(store=store, type='store')
        trash = await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status = 'processing',
            estatus='products_reserve',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_reserve', 'products_reserve')
        tap.eq(order.target, 'complete', 'target: complete')

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=7,
            lot=uuid(),
        )
        tap.ok(stock1, f'Остаток 1: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product,
            count=18,
            lot=uuid(),
        )
        tap.ok(stock2, f'Остаток 2: {stock2.stock_id}')

        stock3 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product,
            count=13,
            valid=date(2020, 1, 1),
            lot=uuid(),
        )
        tap.ok(stock3, f'Остаток 3: {stock3.stock_id}')

        tap.ok(
            await wait_order_status(
                order,
                ('processing', 'suggests_generate'),
            ),
            'Выполнили резервирование'
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')
        tap.eq(order.shelves, [trash.shelf_id], 'Список полок')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Список саджестов')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'check', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                trash.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.eq(
                suggest.count,
                18 + 13,
                f'count={suggest.count}'
            )
            tap.eq(
                suggest.valid,
                date(2020, 1, 1),
                f'valid={suggest.valid}'
            )
            tap.ok(suggest.conditions.max_count,
                   'Нельзя вводить больше чем указано')
