import pytest
from libstall.util import token


@pytest.mark.parametrize('subscribe', [True, False])
async def test_external(tap, dataset, subscribe, cfg):
    with tap.plan(13, f'Стоки по складу (посылки): '
                      f'{"подписка" if subscribe else "просмотр"}'):

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        stock = await dataset.stock(store=store)
        tap.eq(stock.store_id, store.store_id, 'остаток сгенерирован')


        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр сгенерирован')

        item_stock = await dataset.stock(
            store=store,
            product_id=item.item_id,
            count=1,
            shelf_type='parcel',
        )
        tap.eq(item_stock.store_id, store.store_id, 'экземпляр создан')
        tap.eq(item_stock.shelf_type, 'parcel', 'тип полки')
        tap.eq(item_stock.product_id, item.item_id, 'product_id остатка')


        cursor, res = await dataset.Stock.list_external(
            # специально ниже мусор в параметрах
            subscribe=subscribe,
            store_id=store.store_id,
            mode='parcel'
        )
        tap.ok(cursor, 'курсор есть')
        tap.eq(len(res), 1, 'одна запись на выходе')

        cursor_dict = token.unpack(cfg('web.auth.secret'), cursor)
        tap.isa_ok(cursor_dict, dict, 'курсор распаковался')
        tap.eq(cursor_dict['mode'], 'parcel', 'режим курсора')


        tap.eq({x['shelf_type'] for x in res}, {'parcel'}, 'только посылки')

        cursor, res = await dataset.Stock.list_external(
            # специально ниже мусор в параметрах
            subscribe=subscribe,
            store_id=store.store_id,
            mode='parcel',
            cursor_str=cursor,
        )
        if subscribe:
            tap.ok(cursor, 'курсор есть')
        else:
            tap.ok(not cursor, 'курсора дальше нет')
        tap.eq(len(res), 0, 'нет записей во второй выборке')
