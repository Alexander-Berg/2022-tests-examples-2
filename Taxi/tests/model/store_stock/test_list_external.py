import asyncio
import pytest


@pytest.mark.non_parallel
@pytest.mark.parametrize('subscribe', [True, False, None])
async def test_list(tap, dataset, subscribe):
    with tap.plan(13, 'Запрос списка'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store,
                                    type='kitchen_components')
        tap.ok(shelf.type, 'kitchen_components', 'полка создана')

        stock = await dataset.stock(shelf=shelf)
        tap.eq(stock.shelf_type, 'kitchen_components', 'остаток сгенерирован')

        tap.ok(await dataset.StoreStock.daemon_cycle(), 'Цикл выполнен')

        cursor, lst = await dataset.StoreStock.list_external(
            subscribe=subscribe
        )

        tap.ok(cursor, 'курсор сформирован')
        tap.eq(cursor['subscribe'], subscribe, 'значение subscribe в курсоре')
        tap.isa_ok(lst, list, 'список записей')
        tap.ok(lst, 'не пустой')
        tap.isa_ok(lst[0], dataset.StoreStock, 'тип записи')

        cursor2, lst2 = await dataset.StoreStock.list_external(cursor=cursor)
        tap.ok(cursor2, 'курсор сформирован')
        tap.eq(cursor2['subscribe'], subscribe, 'значение subscribe в курсоре')
        tap.isa_ok(lst2, list, 'список записей')
        if lst2:
            tap.ok(
                sum(cursor2['shard'].values()) > sum(cursor['shard'].values()),
                'lsn/serial растёт в курсоре'
            )
        else:
            tap.eq(cursor2, cursor, 'курсор не меняется')


@pytest.mark.non_parallel
@pytest.mark.parametrize('subscribe', [True, False, None])
async def test_list_store_id(tap, dataset, subscribe):
    with tap.plan(10, 'Запрос списка с фильтром store_id'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        tap.ok(await dataset.StoreStock.daemon_cycle(), 'Цикл выполнен')

        cursor, lst = await dataset.StoreStock.list_external(
            subscribe=subscribe,
            store_id=store.store_id,
        )

        tap.ok(cursor, 'курсор сформирован')
        tap.eq(cursor['subscribe'], subscribe, 'значение subscribe в курсоре')
        tap.isa_ok(lst, list, 'список записей')
        tap.ok(not lst, 'пустой')

        cursor2, lst2 = await dataset.StoreStock.list_external(cursor=cursor)
        tap.ok(cursor2, 'курсор сформирован')
        tap.eq(cursor2['subscribe'], subscribe, 'значение subscribe в курсоре')
        tap.isa_ok(lst2, list, 'список записей')
        tap.eq(cursor2, cursor, 'курсор не меняется')


@pytest.mark.non_parallel
async def test_list_company_id(tap, dataset):
    with tap:
        company = await dataset.company()
        store = await dataset.store(company=company)
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(
            store=store,
            type='kitchen_components'
        )
        tap.ok(shelf, 'полка создана')

        tap.ok(await dataset.StoreStock.daemon_cycle(), 'Цикл выполнен')
        cursor, lst = await dataset.StoreStock.list_external(
            company_id=company.company_id
        )
        tap.eq(len(lst), 0, 'нет стоков')

        stock = await dataset.stock(shelf=shelf, count=335, quants=335)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.company_id, company.company_id, 'правильный company_id')

        second_shelf = await dataset.shelf(type='kitchen_components')
        tap.ok(second_shelf, 'вторая полка')
        stock_second = await dataset.stock(
            shelf=second_shelf,
            count=100,
            quants=100
        )
        tap.ok(stock_second, 'второй остаток')
        for i in range(5):
            # флапы, демон не всегда справляется за один цикл
            tap.ok(
                await dataset.StoreStock.daemon_cycle(),
                f'Цикл выполнен, попытка {i+1}'
            )
            store_stocks = await dataset.StoreStock.list(
                by='full',
                conditions=('store_id', store.store_id)
            )

            if store_stocks and store_stocks.list:
                break
            await asyncio.sleep(0.5)

        cursor, lst = await dataset.StoreStock.list_external(
            company_id=company.company_id
        )
        tap.ok(cursor, 'курсор сформирован')
        tap.eq(
            cursor.get('company_id'),
            company.company_id,
            'правильный company'
        )
        tap.eq(len(lst), 1, 'сток один')
        tap.eq(lst[0].count, stock.count, 'количество в стоке правильное')
        tap.eq(lst[0].company_id, stock.company_id, 'правильная компания')
