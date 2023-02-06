from unittest.mock import patch
import pytest
from stall.model.lock import ProlongLock


async def test_instance(tap, dataset):
    with tap.plan(4, 'инстанцирование и заглушка на save'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        stock = dataset.StoreStock({
            'store_id':  store.store_id,
            'product_id': product.product_id,
            'shelf_type': 'store',
            'company_id': store.company_id,
        })
        tap.ok(stock, 'инстанцирован')

        with tap.raises(RuntimeError, 'Вызывать save нельзя'):
            await stock.save()


@pytest.mark.non_parallel
async def test_daemon_methods(tap, dataset):
    with tap.plan(12, 'Запрос за посл записями'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='kitchen_components')
        tap.eq(shelf.type, 'kitchen_components', 'полка создана')
        stock = await dataset.stock(shelf=shelf)
        tap.eq(stock.shelf_type, 'kitchen_components', 'остаток сгенерирован')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        last = await dataset.StoreStock.last()
        tap.isa_ok(last, dict, 'список последних получен')

        lastc = await dataset.StoreStock.daemon_cycle()
        tap.ok(lastc, 'цикл демона выполнен')
        tap.ne(lastc, last, 'цикл возвращает новый курсор')

        tap.ok(await dataset.StoreStock.daemon(exit_at_endlog=True),
               'Демон дочитал до конца и вышел')

        record = await dataset.StoreStock.load(
            (stock.store_id, stock.product_id, stock.shelf_type),
            by='store_product'
        )
        count = stock.count
        tap.eq(record.count, count, 'количество')
        lsn = record.lsn

        tap.ok(await stock.do_put_exists(order, 10),  'put сделан')

        tap.ok(await dataset.StoreStock.daemon(exit_at_endlog=True),
               'Демон дочитал до конца и вышел')

        record = await dataset.StoreStock.load(
            (stock.store_id, stock.product_id, stock.shelf_type),
            by='store_product'
        )
        tap.eq(record.count, count + 10, 'количество')
        tap.ok(record.lsn > lsn, 'lsn увеличился')


@pytest.mark.non_parallel
async def test_lock_active(tap, dataset, uuid):
    with tap.plan(8, 'Работа демона с разными блокировками'), \
            patch.object(
        dataset.StoreStock,
        'load',
        wraps=dataset.StoreStock.load
    ) as ss_load:
        shelf = await dataset.shelf(type='kitchen_components')
        tap.eq(shelf.type, 'kitchen_components', 'полка создана')
        saved_last = await dataset.StoreStock.last()
        stock = await dataset.stock(shelf=shelf)
        tap.eq(stock.shelf_type, 'kitchen_components', 'остаток сгенерирован')
        lock_name = f'daemon_cycle-{uuid()}'
        lock = ProlongLock(lock_name)
        tap.ok(saved_last, 'Получили последний курсор')
        async with lock as pl:
            last = await dataset.StoreStock.daemon_cycle(pl)
            tap.ne(last, saved_last, 'Вернули новый курсор')
            call_count = ss_load.call_count
            tap.ne(call_count, 0, 'Вызывали меняющую операцию')
        stock = await dataset.stock(shelf=shelf)
        tap.eq(stock.shelf_type, 'kitchen_components', 'добавил еще остаток')
        new_last = await dataset.StoreStock.daemon_cycle(pl)
        tap.eq(new_last, None, 'С мертвой блокировкой не вернули')
        tap.eq(ss_load.call_count, call_count, 'Новых вызовов не было')


@pytest.mark.parametrize(
    'reserve, count, expected', [
        (1, 2, 1),
        (3, 3, 0),
        (0, 0, 0),
        (-1, 0, 0),
        (0, -1, 0),
        (3, 2, 0),
    ]
)
async def test_property_left(tap, dataset, reserve, count, expected):
    with tap.plan(1, 'проверяем корректность работы self.left'):
        # всё что меньше 0 или дробное должно ассёртить...
        store = await dataset.store()
        company = await dataset.company()
        product = await dataset.product()
        store_stock = dataset.StoreStock(
            reserve=reserve,
            count=count,
            store_id=store.store_id,
            company_id=company.company_id,
            product_id=product.product_id,
            shelf_type='kitchen_components',
        )
        tap.eq_ok(store_stock.left, expected, 'нормально работает')
