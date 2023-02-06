from stall.model.stock import Stock


async def test_instance(tap, uuid):
    tap.plan(2)
    stock = Stock({
        'title': 'тест склад',
        'company_id': uuid(),
        'store_id': uuid(),
        'product_id': uuid(),
        'shelf_id': uuid(),
        'shelf_type': 'store'
    })
    tap.ok(stock, 'склад инстанцирован')
    tap.eq(stock.database, 'main', 'имя базы данных')
    tap()
