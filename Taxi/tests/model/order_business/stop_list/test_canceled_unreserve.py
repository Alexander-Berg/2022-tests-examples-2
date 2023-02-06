import pytest


@pytest.mark.parametrize(
    'shelf_type', ('store', 'markdown', 'kitchen_components'),
)
async def test_unreserve(tap, dataset, wait_order_status, shelf_type):
    with tap.plan(8, 'Отменяем резерв на товар на полке'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type=shelf_type)
        product = await dataset.product()

        stock = await dataset.stock(product=product, shelf=shelf, count=10)
        tap.eq_ok(stock.count, 10, 'Остаток 10')
        tap.eq_ok(stock.reserve, 0, 'Резерв 0')

        stop_list = await dataset.order(
            store=store,
            type='stop_list',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                },
            ],
        )
        tap.ok(stop_list, 'Создали стоп-лист на весь продукт на полке')

        await wait_order_status(stop_list, ('processing', 'waiting'))
        await stop_list.business.order_changed()

        await stock.reload()
        tap.eq(stock.reserve, 10, 'Товар на полке в резерве')

        tap.ok(await stop_list.cancel(), 'Отменили стоп-лист')

        await wait_order_status(stop_list, ('canceled', 'unreserve'))
        await stop_list.business.order_changed()

        await stock.reload()
        tap.eq(stock.reserve, 0, 'Товар на полке доступен')
