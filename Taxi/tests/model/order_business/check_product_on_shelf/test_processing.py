import pytest

from stall.model.suggest import Suggest

# pylint: disable=too-many-statements
@pytest.mark.parametrize(
    'shelf_type', ['store', 'kitchen_components', 'repacking'],
)
async def test_reserving_shelf(tap, dataset, uuid,
                               wait_order_status, shelf_type):
    with tap.plan(27):
        product = await dataset.product(quants=2)
        tap.ok(product, 'товар сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'Склад сгенерирован')

        shelf = await dataset.shelf(store=store, type=shelf_type)
        tap.ok(shelf, 'полки сгенерированы')

        stocks = [await dataset.stock(shelf=shelf,
                                      count=123,
                                      lot=uuid(),
                                      product=product)
                  for _ in range(2)]
        tap.ok(stocks, 'остатки сгенерированы')
        tap.eq([x.store_id for x in stocks],
               [store.store_id]*len(stocks),
               'Все на складе')
        tap.eq([x.shelf_id for x in stocks],
               [shelf.shelf_id]*len(stocks),
               'Все на полке')
        tap.eq([x.product_id for x in stocks],
               [product.product_id]*len(stocks),
               'Все на один продукт')
        tap.eq(len(stocks), 2, 'два стока')

        order = await dataset.order(
            type='check_product_on_shelf',
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            store=store,
            status='processing',
            estatus='suggests_generate',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                    'update_valids': True
                }
            ],
        )

        tap.ok(order, 'ордер сгенерирован')
        tap.eq(order.type, 'check_product_on_shelf', 'инвентаризация')
        tap.eq(order.status, 'processing', 'статус')
        tap.eq(order.estatus, 'suggests_generate', 'сабстатус')
        tap.ok(order.shelves, 'полки есть')
        tap.eq(order.users, [], 'пользователь не назначен')
        version = order.version

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.reload(), 'перезагружен')
        tap.ok(version < order.version, 'версия ордера инкрементнулась')
        version = order.version

        suggests = await Suggest.list_by_order(order)
        tap.isa_ok(suggests, list, 'саджесты получены')
        tap.eq(len(suggests), 1, 'количество саджестов')


        with suggests[0] as s:
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.shelf_id, shelf.shelf_id, 'полка')
            tap.eq(s.count, sum(s.count for s in stocks), 'количество')
            tap.eq(s.status, 'request', 'предлагается')

            smap = sorted(s.vars('stocks.*'), key=lambda x: x[0])
            smap_s = [[s.stock_id, s.lsn, s.count]
                      for s in sorted(stocks, key=lambda x: x.stock_id)]
            tap.eq(smap_s, smap, 'сгенерированы данные для идемпотентности')
            tap.ok(s.conditions.all, 'можно указывать любое количество')
            tap.ok(not s.conditions.editable, 'не редактруем')
            tap.ok(s.conditions.need_valid, 'требуется указывать срок годности')
