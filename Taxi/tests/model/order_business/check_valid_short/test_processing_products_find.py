# pylint: disable=too-many-locals,too-many-statements

from datetime import timedelta

from libstall.util import now
from stall.model.stock import Stock


# Учитываем 1 день в простановке сроков, который мы даем на процесс списания
async def test_products_find(tap, dataset, uuid):
    with tap.plan(21, 'Резервирование всех продуктов на полке'):

        product1 = await dataset.product(valid=10, write_off_before=1)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        shelf3 = await dataset.shelf(store=store, type='store', order=3)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'processing',
            estatus='products_find',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_find', 'products_find')
        tap.eq(order.target, 'complete', 'target: complete')

        with product1 as product:
            stock1 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=7,
                # Считаем, что срок этого остатка не проконтролировали вчера
                valid=now() + timedelta(product.write_off_before),
                lot=uuid(),
            )
            tap.ok(stock1, f'Остаток 1 на полке 1 просрочен: {stock1.stock_id}')

            stock2 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=18,
                # Учитываем 1 день в простановке сроков,
                # который мы даем на процесс списания
                valid=now() + timedelta(product.write_off_before + 1),
                lot=uuid(),
            )
            tap.ok(stock2, f'Остаток 2 на полке 1 для КСГ: {stock2.stock_id}')

            stock3 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=13,
                # Учитываем 1 день в простановке сроков,
                # который мы даем на процесс списания +  1 день запаса
                valid=now() + timedelta(
                    product.write_off_before + 1 + 1),
                lot=uuid(),
            )
            tap.ok(
                stock3, f'Остаток 3 на полке 1 не просрочен: {stock3.stock_id}')

            stock4 = await dataset.stock(
                store=store,
                shelf=shelf2,
                product=product,
                count=11,
                # Считаем, что срок этого остатка не проконтролировали вчера
                valid=now() + timedelta(product.write_off_before),
                lot=uuid(),
            )
            tap.ok(stock4, f'Остаток 4 на полке 2 просрочен: {stock4.stock_id}')

            stock5 = await dataset.stock(
                store=store,
                shelf=shelf3,
                product=product,
                count=18,
                # Учитываем 1 день в простановке сроков,
                # который мы даем на процесс списания +  1 день запаса
                valid=now() + timedelta(
                    product.write_off_before + 1 + 1),
                lot=uuid(),
            )
            tap.ok(
                stock5, f'Остаток 5 на полке 3 не просрочен: {stock5.stock_id}')

            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
            )
            tap.eq(len(stocks), 5, 'Остатки продукта 1 сохранены')

        with product2 as product:
            stock6 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=28,
                # Учитываем 1 день в простановке сроков,
                # который мы даем на процесс списания
                valid=now() + timedelta(days=1),
                lot=uuid(),
            )
            tap.ok(stock6, f'Остаток 1 на полке 1 просрочен: {stock6.stock_id}')

            stock7 = await dataset.stock(
                store=store,
                shelf=shelf2,
                product=product,
                count=24,
                # Учитываем 1 день в простановке сроков,
                # который мы даем на процесс списания +  1 день запаса
                valid=now() + timedelta(days=(1 + 1)),
                lot=uuid(),
            )
            tap.ok(
                stock7, f'Остаток 2 на полке 2 не просрочен: {stock7.stock_id}')

            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
            )
            tap.eq(len(stocks), 2, 'Остатки сохранены')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.eq(
            sorted(order.vars['write_off'][
                shelf1.shelf_id][product1.product_id]),
            sorted([stock1.stock_id, stock2.stock_id]),
            'Просроченные остатки 1'
        )
        tap.eq(
            sorted(order.vars['write_off'][
                shelf1.shelf_id][product2.product_id]),
            sorted([stock6.stock_id]),
            'Просроченные остатки 2'
        )
        tap.eq(
            sorted(order.vars['write_off'][
                shelf2.shelf_id][product1.product_id]),
            sorted([stock4.stock_id]),
            'Просроченные остатки 3'
        )


async def test_reserve_selected_products(tap, dataset, uuid):
    with tap.plan(25, 'Резервирование выбранных продуктов'
                      ' на выбранных полках'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        shelf3 = await dataset.shelf(store=store, type='store', order=3)

        with product1 as product:
            stock1 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=7,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(
                stock1, f'Товар1(1) на полке 1 просрочен: {stock1.stock_id}')

            stock2 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=18,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(
                stock2, f'Товар1(2) на полке 1 просрочен: {stock2.stock_id}')

            stock3 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=13,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(
                stock3, f'Товар1(3) на полке 1 просрочен: {stock3.stock_id}')

            stock4 = await dataset.stock(
                store=store,
                shelf=shelf2,
                product=product,
                count=11,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(stock4, f'Товар1 на полке 2 просрочен: {stock4.stock_id}')

            stock5 = await dataset.stock(
                store=store,
                shelf=shelf3,
                product=product,
                count=18,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(
                stock5, f'Товар1 на полке 3 просрочен: {stock5.stock_id}')

            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
            )
            tap.eq(len(stocks), 5, 'Остатки сохранены')

        with product2 as product:
            stock6 = await dataset.stock(
                store=store,
                shelf=shelf1,
                product=product,
                count=28,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(stock6, f'Товар2 на полке 1 просрочен: {stock6.stock_id}')

            stock7 = await dataset.stock(
                store=store,
                shelf=shelf2,
                product=product,
                count=24,
                valid=now() - timedelta(days=30),
                lot=uuid(),
            )
            tap.ok(
                stock7, f'Товар2 на полке 2 просрочен: {stock7.stock_id}')

            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
            )
            tap.eq(len(stocks), 2, 'Остатки сохранены')

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='processing',
            estatus='products_find',
            required=[
                {
                    'shelf_id': shelf1.shelf_id,
                    'product_id': product1.product_id
                },
                {
                    'shelf_id': shelf2.shelf_id,
                    'product_id': product2.product_id
                },
                {
                    'shelf_id': shelf1.shelf_id,
                    'product_id': uuid(),
                },
                {
                    'shelf_id': uuid(),
                    'product_id': product1.product_id,
                },
                {
                    'shelf_id': uuid(),
                    'product_id': uuid(),
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_find', 'products_find')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 2, 'Две проблемы')
        tap.eq(order.problems[0].type, 'shelf_not_found',
               'Проблема: не найдена полка')
        tap.eq(order.problems[1].type, 'shelf_not_found',
               'Проблема: не найдена полка')

        write_off = order.vars['write_off']
        tap.eq(
            sorted(write_off[shelf1.shelf_id][product1.product_id]),
            sorted([stock1.stock_id, stock2.stock_id, stock3.stock_id]),
            'Просроченный товар 1 на полке 1'
        )
        tap.eq(
            sorted(write_off[shelf2.shelf_id][product2.product_id]),
            sorted([stock7.stock_id]),
            'Просроченный товар 2 на полке 2'
        )
        tap.ok(product2.product_id not in write_off[shelf1.shelf_id],
               'Просроченный товар 2 на полке 1 не трогаем')
        tap.ok(product1.product_id not in write_off[shelf2.shelf_id],
               'Просроченный товар 1 на полке 2 не трогаем')
        tap.ok(shelf3.shelf_id not in write_off,
               'Полку 3 не трогаем')


async def test_empty_write_off(tap, dataset, uuid, wait_order_status):
    with tap.plan(14, 'Нет ни одного просроченного продукта'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        await dataset.shelf(store=store, type='trash', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=7,
            valid=now() + timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock1,
               f'Остаток на полке 1 не просрочен: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=28,
            valid=now() + timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock2,
               f'Остаток на полке 2 не просрочен: {stock2.stock_id}')

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(
            await wait_order_status(
                order,
                ('processing', 'products_find'),
            ),
            'Готовы к резервированию'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        write_off = order.vars['write_off']
        tap.eq(write_off, {}, 'Пустой список')
