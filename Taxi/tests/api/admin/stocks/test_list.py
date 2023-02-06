import pytest


@pytest.mark.parametrize('shelf_id', [None, 'random_id'])
@pytest.mark.parametrize('shelf_type', [None, 'store'])
@pytest.mark.parametrize('direction', [None, 'ASC', 'DESC'])
async def test_list_empty(tap, dataset, api, direction, shelf_type, shelf_id):
    with tap.plan(7, 'Запрос за пустым списком'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        admin = await dataset.user(store=store)
        tap.eq(admin.store_id, store.store_id, 'Админ создан')

        t = await api(user=admin)

        filters = {}

        if direction:
            filters['direction'] = direction
        if shelf_type:
            filters['shelf_type'] = shelf_type
        if shelf_id:
            filters['shelf_id'] = shelf_id

        await t.post_ok('api_admin_stocks_list', json=filters)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')
        t.json_hasnt('stocks.0')


@pytest.mark.parametrize('product_filter', [False, 'product'])
@pytest.mark.parametrize('shelf_id_filter', [False, 'shelf_id'])
@pytest.mark.parametrize('shelf_type_filter', [False, 'shelf_type'])
@pytest.mark.parametrize('direction', [False, 'ASC', 'DESC'])
async def test_list(tap,
                    dataset,
                    api,
                    product_filter,
                    shelf_id_filter,
                    shelf_type_filter,
                    direction,
                    time2iso_utc):
    with tap.plan(20, 'Запрос с выдачей и фильтрами'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        admin = await dataset.user(store=store)
        tap.eq(admin.store_id, store.store_id, 'Админ создан')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'Остаток создан')

        t = await api(user=admin)

        filters = {}
        if product_filter:
            filters['print_id'] = stock.product_id
        if shelf_id_filter:
            filters['shelf_id'] = stock.shelf_id
        if shelf_type_filter:
            filters['shelf_type'] = stock.shelf_type
        if direction:
            filters['direction'] = direction

        await t.post_ok('api_admin_stocks_list', json=filters)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')

        t.json_is('stocks.0.stock_id', stock.stock_id)
        t.json_is('stocks.0.store_id', stock.store_id)
        t.json_is('stocks.0.product_id', stock.product_id)
        t.json_is('stocks.0.shelf_id', stock.shelf_id)
        t.json_is('stocks.0.shelf_type', stock.shelf_type)
        t.json_is('stocks.0.count', stock.count)
        t.json_is('stocks.0.reserve', stock.reserve)
        t.json_is('stocks.0.created', time2iso_utc(stock.created))
        t.json_is('stocks.0.updated', time2iso_utc(stock.updated))
        t.json_is('stocks.0.lot', stock.lot)
        t.json_is('stocks.0.lot_price', stock.lot_price)
        t.json_is('stocks.0.lot_price_unit', stock.lot_price_unit)
        t.json_is('stocks.0.valid', stock.valid)
