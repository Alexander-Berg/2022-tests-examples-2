import asyncio
import pytest

from stall.model.stock_log import StockLog


# pylint: disable=too-many-locals
@pytest.mark.parametrize('type_filter', [False, True])
@pytest.mark.parametrize('order_filter', [False, True])
@pytest.mark.parametrize('shelf_filter', [False, True])
async def test_product(
    tap, dataset, api, type_filter, order_filter, shelf_filter,
):
    with tap.plan(15, 'Запрос логов продукта'):
        store = await dataset.store()
        admin = await dataset.user(store=store)
        executer = await dataset.user(store=store, role='executer')

        shelf = await dataset.shelf(store_id=store.store_id)
        order = await dataset.order(store=store, acks=[executer.user_id])
        stock = await dataset.stock(shelf=shelf, count=345, order=order)
        await stock.do_reserve(order, 123)

        logs = await StockLog.list(
            conditions=[
                ('store_id', store.store_id),
                ('product_id', stock.product_id)
            ],
            by='look',
        )
        tap.eq(len(logs.list), 2, 'Создано 2 лога')
        log = logs.list[-1]

        t = await api(user=admin)

        filters = {}
        if type_filter:
            filters['type'] = 'put'
        if shelf_filter:
            filters['shelf_id'] = shelf.shelf_id
        if order_filter:
            filters['order_id'] = order.order_id

        await t.post_ok('api_admin_stocks_product_log',
                        json={
                            'product': {'product_id': stock.product_id},
                            **filters})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)

        t.json_is('stocks_log.0.stock_id', stock.stock_id)
        t.json_is('stocks_log.0.log_id', log.log_id)
        t.json_is('stocks_log.0.product_id', log.product_id)
        t.json_is('stocks_log.0.type', log.type)
        t.json_is('stocks_log.0.delta_count', log.delta_count)
        t.json_is('stocks_log.0.count', log.count)
        t.json_has('stocks_log.0.created')
        t.json_is('stocks_log.0.shelf_id', log.shelf_id)
        t.json_is('stocks_log.0.user_id', log.user_id)

        t.json_hasnt('stocks_log.1', 'reserve не вернулся')


# pylint: disable=too-many-locals
@pytest.mark.parametrize('direction, index', [('ASC', -1), ('DESC', 0)])
async def test_limit(tap, dataset, api, direction, index):
    with tap.plan(10, 'Проверяем limit и direction'):
        store = await dataset.store()
        admin = await dataset.user(store=store)
        executer = await dataset.user(store=store, role='executer')

        shelf = await dataset.shelf(store_id=store.store_id)
        product = await dataset.product()
        order = await dataset.order(store=store, acks=[executer.user_id])
        stock = await dataset.stock(count=345, order=order, product=product)
        await asyncio.sleep(1)  # для разного времени создания стоклогов
        await stock.do_put(order, shelf, product, 3)

        logs = await StockLog.list(
            conditions=[
                ('store_id', store.store_id),
                ('product_id', stock.product_id)
            ],
            by='look',
            sort=('serial', 'DESC'),
        )
        tap.eq(len(logs.list), 2, 'Создано 2 лога')
        log = logs.list[index]

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json={'product': {'product_id': stock.product_id},
                              'direction': direction,
                              'limit': 1}
                        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        t.json_is('stocks_log.0.stock_id', log.stock_id)
        t.json_is('stocks_log.0.log_id', log.log_id)
        t.json_is('stocks_log.0.type', log.type)
        t.json_is('stocks_log.0.count', log.count)

        t.json_hasnt('stocks_log.1', 'больше стоков нет')


async def test_item(tap, dataset, api):
    with tap.plan(15, 'Запрос логов посылки'):
        store = await dataset.store()
        admin = await dataset.user(store=store)
        executer = await dataset.user(store=store, role='executer')

        item = await dataset.item()
        shelf = await dataset.shelf(store_id=store.store_id)
        order = await dataset.order(store=store, acks=[executer.user_id])
        stock = await dataset.stock(shelf=shelf,
                                    count=1,
                                    order=order,
                                    item=item)
        await stock.do_reserve(order, 1)

        logs = await StockLog.list(
            conditions=[
                ('store_id', store.store_id),
                ('product_id', item.item_id)],
            by='look',
        )
        tap.eq(len(logs.list), 2, 'Создано 2 лога')
        log = logs.list[-1]

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json={'product': {'item_id': item.item_id}})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)

        t.json_is('stocks_log.0.stock_id', stock.stock_id)
        t.json_is('stocks_log.0.log_id', log.log_id)
        t.json_is('stocks_log.0.product_id', log.product_id)
        t.json_is('stocks_log.0.type', log.type)
        t.json_is('stocks_log.0.delta_count', log.delta_count)
        t.json_is('stocks_log.0.count', log.count)
        t.json_has('stocks_log.0.created')
        t.json_is('stocks_log.0.shelf_id', log.shelf_id)
        t.json_is('stocks_log.0.user_id', log.user_id)

        t.json_hasnt('stocks_log.1')


async def test_empty_list(tap, dataset, api):
    with tap.plan(6, 'Пустой список стоков продукта'):
        store = await dataset.store()
        product = await dataset.product()
        admin = await dataset.user(store=store)

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json={
                            'product': {'product_id': product.product_id},
                            'type': 'lost',
                            'direction': 'ASC'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_has('stocks_log')
        t.json_hasnt('stocks_log.0')


@pytest.mark.parametrize('param', ['product_id', 'item_id'])
async def test_product_not_found(tap, dataset, api, uuid, param):
    with tap.plan(3, 'Товар не найден'):
        store = await dataset.store()
        admin = await dataset.user(store=store)

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json={'product': {param: uuid()}})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('param', ['shelf_id', 'order_id'])
async def test_not_found(tap, dataset, api, uuid, param):
    with tap.plan(3, 'Параметр не найден'):
        store = await dataset.store()
        admin = await dataset.user(store=store)
        product = await dataset.product()

        filters = {'product': {'product_id': product.product_id}}
        filters[param] = uuid()

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json=filters)
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('param', ['shelf_id', 'order_id'])
async def test_not_from_store(tap, dataset, api, param):
    with tap.plan(3, f'{param} не принадлежит лавке'):
        store_1 = await dataset.store()
        admin = await dataset.user(store=store_1)
        product = await dataset.product()

        store_2 = await dataset.store()

        filters = {'product': {'product_id': product.product_id}}
        if param == 'shelf_id':
            shelf = await dataset.shelf(store=store_2)
            filters[param] = shelf.shelf_id
        else:
            order = await dataset.order(store=store_2)
            filters[param] = order.order_id

        t = await api(user=admin)
        await t.post_ok('api_admin_stocks_product_log',
                        json=filters)
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
