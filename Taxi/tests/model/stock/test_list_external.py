import random
import pytest
from stall.model.stock import Stock
from libstall.util import token


@pytest.mark.parametrize('subscribe', [True, False])
async def test_external_subscribe(tap, dataset, uuid, subscribe):
    with tap.plan(22, f'Стоки по складу: '
                      f'{"подписка" if subscribe else "просмотр"}'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток сгенерирован')

        stock2 = await dataset.stock(shelf_id=stock.shelf_id,
                                     product_id=stock.product_id,
                                     lot=uuid())
        tap.ok(stock2, 'остаток сгенерирован')
        tap.eq(stock2.product_id, stock.product_id, 'продукт')
        tap.eq(stock2.store_id, stock.store_id, 'склад')

        cursor, res = await Stock.list_external(store_id=stock.store_id,
                                                subscribe=subscribe)
        tap.ok(cursor, 'курсор есть')
        tap.eq(len(res), 1, 'одна запись на выходе')

        for r in res:
            tap.eq(r['product_id'], stock.product_id, 'продукт')
            tap.eq(r['store_id'], stock.store_id, 'склад')
            tap.eq(r['left'], stock.left + stock2.left, 'остаток')
            tap.eq(r['count'], stock.count + stock2.count, 'количество')
            tap.eq(r['reserve'], stock.reserve + stock2.reserve, 'резерв')


        cursor2, res = await Stock.list_external(cursor_str=cursor,
                                                 # специально ниже мусор
                                                 # в параметрах
                                                 subscribe=not subscribe,
                                                 store_id=uuid())
        if subscribe:
            tap.ok(cursor2, 'курсор есть при повторном запросе')
        else:
            tap.ok(not cursor2, 'курсора нет при повторном запросе')

        tap.eq(res, [], 'данных нет')


        stock3 = await dataset.stock(shelf_id=stock.shelf_id)
        tap.ok(stock3, 'третий сток сгенерирован')
        tap.eq(stock3.store_id, stock.store_id, 'на том же складе')


        cursor3, res = await Stock.list_external(cursor_str=cursor)
        tap.ok(cursor3, 'курсор есть у обоих ответов')

        tap.eq(len(res), 1, 'одна запись на выходе')

        for r in res:
            tap.eq(r['product_id'], stock3.product_id, 'продукт')
            tap.eq(r['store_id'], stock3.store_id, 'склад')
            tap.eq(r['left'], stock3.left, 'остаток')
            tap.eq(r['count'], stock3.count, 'количество')
            tap.eq(r['reserve'], stock3.reserve, 'резерв')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_cursor(tap, dataset, uuid, subscribe):
    with tap.plan(8, 'Читаем до конца'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        products = [await dataset.product() for _ in range(3)]
        tap.ok(products, 'товары сгенерированы')
        stocks = [await dataset.stock(product=random.choice(products),
                                      store=store,
                                      lot=uuid())
                  for _ in range(50)]
        tap.eq(set(s.store_id for s in stocks),
               {store.store_id},
               'Остатки на складе сгенерированы')

        tap.eq(set(s.product_id for s in stocks),
               {p.product_id for p in products},
               'По всем продуктам')


        result = {}

        cursor, rows = await Stock.list_external(
            cursor_str=None,
            store_id=store.store_id,
            subscribe=subscribe,
            limit=2
        )

        tap.ok(rows, 'Есть данные в ответе')
        with tap.subtest(None, 'Тестируем выборку') as taps:
            for r in rows:
                key = (r['product_id'], r['store_id'])

                if key not in result:
                    result[key] = r['count']
                    taps.ok(r['count'], 'Добавляем пару в список')
                else:
                    taps.eq(result[key],
                            r['count'],
                            'По одному ключу у всех одинаково')

        with tap.subtest(None, 'Дочитываем') as taps:
            while rows:
                cursor, rows = await Stock.list_external(
                    cursor_str=cursor,
                    store_id=store.store_id,
                    subscribe=subscribe,
                    limit=50
                )

                if rows:
                    with tap.subtest(None, 'Тестируем выборку') as tapl:
                        tapl.ok(rows, 'Есть данные в ответе второй выборки')
                        for r in rows:
                            key = (r['product_id'], r['store_id'])

                            if key not in result:
                                result[key] = r['count']
                                tapl.ok(r['count'], 'Добавляем пару в список')
                            else:
                                tapl.eq(result[key],
                                        r['count'],
                                        'По одному ключу у всех одинаково')
                else:
                    if subscribe:
                        taps.ok(cursor, 'Курсор при подписке есть')
                    else:
                        taps.ok(not cursor, 'Курсора при просмотре в конце нет')


async def test_agg_count(tap, dataset):
    with tap.plan(4):
        store = await dataset.store()
        p1 = await dataset.product()
        p2 = await dataset.product()
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='markdown')

        await dataset.stock(shelf=shelf1, product=p1, count=1)
        await dataset.stock(shelf=shelf2, product=p1, count=2)
        await dataset.stock(shelf=shelf2, product=p1, count=3)

        await dataset.stock(shelf=shelf1, product=p2, count=4)
        await dataset.stock(shelf=shelf1, product=p2, count=5)

        _, stocks = await Stock.list_external(store_id=store.store_id)
        stocks_by_key = {
            (i['store_id'], i['product_id'], i['shelf_type']): i
            for i in stocks
        }

        tap.eq_ok(len(stocks_by_key), 3, 'Correct number of groups')
        tap.eq_ok(
            stocks_by_key[store.store_id, p1.product_id, 'store']['count'],
            1,
            'store shelf with p1',
        )
        tap.eq_ok(
            stocks_by_key[store.store_id, p1.product_id, 'markdown']['count'],
            5,
            'markdown shelf with p1',
        )
        tap.eq_ok(
            stocks_by_key[store.store_id, p2.product_id, 'store']['count'],
            9,
            'store shelf with p2',
        )

async def test_kitchen(tap, dataset, cfg):
    with tap.plan(9, 'Ручка показывает и кухню'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')
        cursor_str, stocks = await Stock.list_external(
            store_id=store.store_id,
            kitchen=True,
            subscribe=True,
        )
        tap.ok(cursor_str, 'курсор возвращён')
        tap.isa_ok(stocks, list, 'остатки')
        tap.ok(not stocks, 'список пуст')

        cursor = token.unpack(cfg('web.auth.secret'), cursor_str)
        tap.isa_ok(cursor, dict, 'курсор распакован')
        tap.in_ok('kitchen', cursor, 'кухня есть в нём')


        cursor_str, stocks = await Stock.list_external(cursor_str=cursor_str)
        tap.ok(cursor_str, 'повтор выполнен')
        tap.isa_ok(stocks, list, 'остатки')
        tap.ok(not stocks, 'список пуст')
