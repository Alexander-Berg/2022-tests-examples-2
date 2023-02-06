# pylint: disable=expression-not-assigned
import pytest


@pytest.mark.parametrize(
    'shelf_type', ('store', 'markdown', 'kitchen_components'),
)
async def test_reserve_shelf_product(
        tap, dataset, wait_order_status, shelf_type,
):
    with tap.plan(14, 'Резервируем конкретный товар на конкретной полке'):
        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type=shelf_type)
        shelf2 = await dataset.shelf(store=store, type=shelf_type)

        vino = await dataset.product()
        pivo = await dataset.product()

        stock_s1_vino = await dataset.stock(
            product=vino, shelf=shelf1, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На первой полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На первой полке вино без резерва'
        )

        stock_s1_pivo = await dataset.stock(
            product=pivo, shelf=shelf1, count=20,
        )
        tap.eq_ok(stock_s1_pivo.count, 20, 'На первой полке пиво 20 шт')
        tap.eq_ok(
            stock_s1_pivo.reserve, 0, 'На первой полке пиво без резерва'
        )

        stock_s2_vino = await dataset.stock(
            product=vino, shelf=shelf2, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На второй полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На второй полке вино без резерва'
        )

        stock_s2_pivo = await dataset.stock(
            product=pivo, shelf=shelf2, count=20,
        )
        tap.eq_ok(stock_s2_pivo.count, 20, 'На второй полке пиво 10 шт')
        tap.eq_ok(
            stock_s2_pivo.reserve, 0, 'На второй полке пиво без резерва'
        )

        stocks = [stock_s1_vino, stock_s1_pivo, stock_s2_vino, stock_s2_pivo]

        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf1.shelf_id,
                    'product_id': vino.product_id,
                },
            ],
        )
        tap.ok(stop_list, 'Создали стоп-лист на все вино на первой полке')

        await wait_order_status(stop_list, ('reserving', 'reserve'))
        await stop_list.business.order_changed()
        [await i.reload() for i in stocks]

        tap.eq(stock_s1_vino.reserve, 10, 'На первой полке все вино в резерве')
        tap.eq(stock_s1_pivo.reserve, 0, 'На первой полке все пиво доступно')
        tap.eq(stock_s2_vino.reserve, 0, 'На второй полке все вино доступно')
        tap.eq(stock_s2_pivo.reserve, 0, 'На второй полке все пиво доступно')


@pytest.mark.parametrize(
    'shelf_type', ('store', 'markdown', 'kitchen_components'),
)
async def test_reserve_shelf(tap, dataset, wait_order_status, shelf_type):
    with tap.plan(14, 'Резервируем весь товар на конкретной полке'):
        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type=shelf_type)
        shelf2 = await dataset.shelf(store=store, type=shelf_type)

        vino = await dataset.product()
        pivo = await dataset.product()

        stock_s1_vino = await dataset.stock(
            product=vino, shelf=shelf1, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На первой полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На первой полке вино без резерва'
        )

        stock_s1_pivo = await dataset.stock(
            product=pivo, shelf=shelf1, count=20,
        )
        tap.eq_ok(stock_s1_pivo.count, 20, 'На первой полке пиво 20 шт')
        tap.eq_ok(
            stock_s1_pivo.reserve, 0, 'На первой полке пиво без резерва'
        )

        stock_s2_vino = await dataset.stock(
            product=vino, shelf=shelf2, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На второй полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На второй полке вино без резерва'
        )

        stock_s2_pivo = await dataset.stock(
            product=pivo, shelf=shelf2, count=20,
        )
        tap.eq_ok(stock_s2_pivo.count, 20, 'На второй полке пиво 10 шт')
        tap.eq_ok(
            stock_s2_pivo.reserve, 0, 'На второй полке пиво без резерва'
        )

        stocks = [stock_s1_vino, stock_s1_pivo, stock_s2_vino, stock_s2_pivo]

        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf1.shelf_id,
                },
            ],
        )
        tap.ok(
            stop_list, 'Создали стоп-лист на все вино и пиво на первой полке',
        )

        await wait_order_status(stop_list, ('reserving', 'reserve'))
        await stop_list.business.order_changed()
        [await i.reload() for i in stocks]

        tap.eq(stock_s1_vino.reserve, 10, 'На первой полке все вино в резерве')
        tap.eq(stock_s1_pivo.reserve, 20, 'На первой полке все пиво в резерве')
        tap.eq(stock_s2_vino.reserve, 0, 'На второй полке все вино доступно')
        tap.eq(stock_s2_pivo.reserve, 0, 'На второй полке все пиво доступно')


@pytest.mark.parametrize(
    'shelf_type', ('store', 'markdown', 'kitchen_components'),
)
async def test_reserve_product(tap, dataset, wait_order_status, shelf_type):
    with tap.plan(14, 'Резервируем конкретный товар на всех полках'):
        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type=shelf_type)
        shelf2 = await dataset.shelf(store=store, type=shelf_type)

        vino = await dataset.product()
        pivo = await dataset.product()

        stock_s1_vino = await dataset.stock(
            product=vino, shelf=shelf1, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На первой полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На первой полке вино без резерва'
        )

        stock_s1_pivo = await dataset.stock(
            product=pivo, shelf=shelf1, count=20,
        )
        tap.eq_ok(stock_s1_pivo.count, 20, 'На первой полке пиво 20 шт')
        tap.eq_ok(
            stock_s1_pivo.reserve, 0, 'На первой полке пиво без резерва'
        )

        stock_s2_vino = await dataset.stock(
            product=vino, shelf=shelf2, count=10,
        )
        tap.eq_ok(stock_s1_vino.count, 10, 'На второй полке вино 10 шт')
        tap.eq_ok(
            stock_s1_vino.reserve, 0, 'На второй полке вино без резерва'
        )

        stock_s2_pivo = await dataset.stock(
            product=pivo, shelf=shelf2, count=20,
        )
        tap.eq_ok(stock_s2_pivo.count, 20, 'На второй полке пиво 10 шт')
        tap.eq_ok(
            stock_s2_pivo.reserve, 0, 'На второй полке пиво без резерва'
        )

        stocks = [stock_s1_vino, stock_s1_pivo, stock_s2_vino, stock_s2_pivo]

        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': vino.product_id,
                },
            ],
        )
        tap.ok(stop_list, 'Создали стоп-лист на все вино на всех полках')

        await wait_order_status(stop_list, ('reserving', 'reserve'))
        await stop_list.business.order_changed()
        [await i.reload() for i in stocks]

        tap.eq(stock_s1_vino.reserve, 10, 'На первой полке все вино в резерве')
        tap.eq(stock_s1_pivo.reserve, 0, 'На первой полке все пиво доступно')
        tap.eq(stock_s2_vino.reserve, 10, 'На второй полке все вино в резерве')
        tap.eq(stock_s2_pivo.reserve, 0, 'На второй полке все пиво доступно')


@pytest.mark.parametrize(
    'shelf_type', ('store', 'markdown', 'kitchen_components'),
)
async def test_reserve_with_reserves(
        tap, dataset, wait_order_status, shelf_type,
):
    with tap.plan(6, 'Резервируем товар, на который есть резерв'):
        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type=shelf_type)
        shelf2 = await dataset.shelf(store=store, type=shelf_type)

        vino = await dataset.product()
        pivo = await dataset.product()

        stock_s1_vino = await dataset.stock(
            product=vino, shelf=shelf1, count=10, reserve=10,
        )
        stock_s1_pivo = await dataset.stock(
            product=pivo, shelf=shelf1, count=20, reserve=20,
        )

        stock_s2_vino = await dataset.stock(
            product=vino, shelf=shelf2, count=10, reserve=1,
        )
        stock_s2_pivo = await dataset.stock(
            product=pivo, shelf=shelf2, count=20, reserve=2,
        )

        stocks = [stock_s1_vino, stock_s1_pivo, stock_s2_vino, stock_s2_pivo]

        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf2.shelf_id,
                },
            ],
        )
        tap.ok(stop_list, 'Создали стоп-лист на первую полку')

        await wait_order_status(stop_list, ('reserving', 'reserve'))
        await stop_list.business.order_changed()
        [await i.reload() for i in stocks]

        tap.eq(
            stock_s1_vino.reserve, 10,
            'Резерв не трогали',
        )
        tap.eq(
            stock_s1_pivo.reserve, 20,
            'Резерв не трогали',
        )
        tap.eq(
            stock_s2_vino.reserve, 10,
            'Зарезервировали остаток',
        )
        tap.eq(
            stock_s2_pivo.reserve, 20,
            'Зарезервировали остаток',
        )
