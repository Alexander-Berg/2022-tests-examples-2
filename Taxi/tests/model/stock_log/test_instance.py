from stall.model.stock_log import StockLog


def test_instance(tap, uuid):
    tap.plan(2)
    record = StockLog({
        'order_type': 'order',
        'type': 'put',

        'delta_count': 10,
        'delta_reserve': -10,

        'stock_id': uuid(),
        'order_id': uuid(),
        'company_id': uuid(),
        'store_id': uuid(),
        'product_id': uuid(),
        'shelf_id': uuid(),
    })
    tap.ok(record, 'запись лога инстанцирована')
    tap.eq(record.database, 'main', 'имя базы данных')
    tap()
