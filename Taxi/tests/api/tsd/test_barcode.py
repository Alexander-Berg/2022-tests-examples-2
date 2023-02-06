import random

import pytest

from stall.model.product import ean13_check_digit


async def test_barcode_empty_found(tap, api):
    with tap.plan(5, 'Метод ничего не нашел'):
        t = await api()
        await t.set_role('admin')

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': 1234})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found', [])


async def test_product_scope(tap, api, dataset, uuid):
    with tap.plan(10, 'не показываем продукты из другоо товарного объема'):
        company = await dataset.company(products_scope=['france'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )

        t = await api(user=user)

        with await dataset.product(
                barcode=[uuid()],
                products_scope=[],
        ) as product:
            await t.post_ok('api_tsd_barcode',
                            json={'barcode': product.barcode[0]})
            t.status_is(200, diag=True)
            t.content_type_like(r'^application/json')
            t.json_is('code', 'OK')
            t.json_is('found', [])

        with await dataset.product(
                barcode=[uuid()],
                products_scope=['israel'],
        ) as product:
            await t.post_ok('api_tsd_barcode',
                            json={'barcode': product.barcode[0]})
            t.status_is(200, diag=True)
            t.content_type_like(r'^application/json')
            t.json_is('code', 'OK')
            t.json_is('found', [])


async def test_barcode_found_user(tap, api, dataset):
    with tap.plan(9, 'нашёлся пользователь'):
        user = await dataset.user(role='executer',
                                  force_role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад назначен')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': user.qrcode})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'user')
        t.json_is('found.0.user_id', user.user_id)
        t.json_is('found.0.title', user.nick)


async def test_barcode_found_product(tap, api, dataset, uuid):
    with tap.plan(13, 'нашёлся продукт но нет остатков'):
        product = await dataset.product(
            barcode=[uuid()],
            products_scope=['russia'],
        )

        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)
        t.json_is('found.0.external_id', product.external_id)
        t.json_is('found.0.title', product.title)
        t.json_is('found.0.long_title', product.long_title)
        t.json_is('found.0.valid', product.valid)
        t.json_is('found.0.write_off_before', product.write_off_before)
        t.json_is('found.0.available', [], 'available пуст')
        t.json_is('found.0.true_mark', False, 'нету ЧЗ')


async def test_found_product_stock(tap, api, dataset, uuid):
    with tap.plan(22, 'нашёлся продукт и есть остатки'):
        product = await dataset.product(
            barcode=[uuid()],
            products_scope=['russia'],
        )

        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(store=store, role='executer')

        stock = await dataset.stock(
            store=store,
            product=product,
            count=223,
            reserve=11
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.store_id, user.store_id, 'склад')
        tap.eq(stock.product_id, product.product_id, 'продукт')
        tap.eq(stock.count, 223, 'количество')
        tap.eq(stock.reserve, 11, 'зарезервировано')

        stock2 = await dataset.stock(shelf_id=stock.shelf_id,
                                     product_id=stock.product_id,
                                     count=222,
                                     reserve=1,
                                     lot=uuid())
        tap.ok(stock2, 'Остаток зарезервирован')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'полка')
        tap.eq(stock2.count, 222, 'количество')
        tap.eq(stock2.reserve, 1, 'резерв')
        tap.ne(stock.stock_id, stock2.stock_id, 'это разные остатки')

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)
        t.json_is('found.0.title', product.title)
        t.json_is('found.0.available.0.shelf_id', stock.shelf_id, 'полка')
        t.json_is('found.0.available.0.count',
                  stock.count + stock2.count,
                  'количество')
        t.json_is('found.0.available.0.reserved',
                  stock.reserve + stock2.reserve,
                  'резерв')
        t.json_is('found.0.available.0.is_components', False)
        t.json_is('found.0.available.0.shelf_type', stock.shelf_type)


async def test_barcode_found_empty_shelf(tap, api, dataset):
    with tap.plan(18, 'нашлась полка и она пуста'):

        user = await dataset.user(role='executer')
        tap.ok(user, 'пользователь создан')

        shelf1 = await dataset.shelf(store_id=user.store_id)
        tap.ok(shelf1, 'полка создана')
        tap.eq(shelf1.store_id, user.store_id, 'на том же складе')

        shelf2 = await dataset.shelf()
        tap.ok(shelf2, 'полка создана')
        tap.ne(shelf2.store_id, user.store_id, 'на другом складе')

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': shelf1.barcode})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'shelf')
        t.json_is('found.0.shelf_id', shelf1.shelf_id)
        t.json_is('found.0.title', shelf1.title)
        t.json_is('found.0.available', [], 'полка пуста')

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': shelf2.barcode})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found', [], 'ничего не найдено по чужой полке')


async def test_barcode_found_shelf(tap, api, dataset, uuid):
    with tap.plan(22, 'нашлась полка и на ней есть товар'):
        user = await dataset.user(role='executer')
        tap.ok(user, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, user.store_id, 'на том же складе')

        stock = await dataset.stock(shelf=shelf,
                                    count=23,
                                    reserve=11,
                                    lot=uuid())
        tap.ok(stock, 'Остаток зарезервирован')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'полка')
        tap.eq(stock.count, 23, 'количество')
        tap.eq(stock.reserve, 11, 'резерв')

        stock2 = await dataset.stock(shelf=shelf,
                                     product_id=stock.product_id,
                                     count=222,
                                     reserve=1,
                                     lot=uuid())
        tap.ok(stock2, 'Остаток зарезервирован')
        tap.eq(stock2.shelf_id, shelf.shelf_id, 'полка')
        tap.eq(stock2.count, 222, 'количество')
        tap.eq(stock2.reserve, 1, 'резерв')
        tap.ne(stock.stock_id, stock2.stock_id, 'это разные остатки')

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': shelf.barcode})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'shelf')
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.title', shelf.title)
        t.json_is('found.0.available.0.product_id', stock.product_id, 'товар')
        t.json_is('found.0.available.0.count',
                  stock.count + stock2.count, 'количество')
        t.json_is('found.0.available.0.reserved',
                  stock.reserve + stock2.reserve,
                  'зарезервировано')


@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
async def test_barcode_by_disabled_user(tap, api, dataset, role, uuid):
    with tap.plan(4, 'Попытка запросить выключенным пользователем'):
        user = await dataset.user(status='disabled', role=role)
        tap.ok(user, 'пользователь создан')

        product = await dataset.product(barcode=[uuid()])
        tap.ok(product, 'товар создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]})
        t.status_is(401, diag=True, desc='Требуется авторизация')


async def test_zero_stock(tap, api, dataset, uuid):
    with tap.plan(8, 'Нуль на стоке не показывается в баркод'):
        product = await dataset.product(
            barcode=[uuid()],
            products_scope=['russia'],
        )

        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(store=store, role='barcode_executer')

        stock = await dataset.stock(count=0,
                                    store=store,
                                    product=product)
        tap.eq(stock.store_id, user.store_id, 'сток сгенерирован')
        tap.eq(stock.count, 0, 'в нём нет товаров')
        tap.eq(stock.product_id, product.product_id, 'товар в стоке')

        t = await api(user=user)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('found.0.product_id', product.product_id)
        t.json_is('found.0.available', [])


async def test_product_stock_kitchen(tap, api, dataset, uuid):
    with tap.plan(19, 'нашёлся продукт и есть остатки'):
        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        shelf = await dataset.shelf(store=store, type='kitchen_components')

        product = await dataset.product(
            barcode=[uuid()],
            products_scope=['russia'],
        )

        user = await dataset.user(role='executer', store=store)

        stock = await dataset.stock(
            store=store,
            product=product,
            count=223,
            reserve=11,
            shelf=shelf,
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.store_id, user.store_id, 'склад')
        tap.eq(stock.product_id, product.product_id, 'продукт')
        tap.eq(stock.count, 223, 'количество')
        tap.eq(stock.reserve, 11, 'зарезервировано')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'на полке компонент')

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': product.barcode[0]})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)
        t.json_is('found.0.title', product.title)
        t.json_is('found.0.available.0.shelf_id', stock.shelf_id, 'полка')
        t.json_is('found.0.available.0.count', stock.count, 'количество')
        t.json_is('found.0.available.0.reserved', stock.reserve, 'резерв')
        t.json_is('found.0.available.0.is_components', True)
        t.json_is('found.0.available.0.shelf_type', stock.shelf_type)
        t.json_is('found.0.available.0.quants', product.quants)


async def test_items(tap, api, dataset):
    with tap.plan(17, 'Штрих коды по экземплярам хранения'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        user = await dataset.user(role='executer', store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store,
                                    product_id=item.item_id,
                                    count=1,
                                    shelf_type='parcel')
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': item.barcode[0]})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'item')
        t.json_is('found.0.item_id', item.item_id)
        t.json_is('found.0.title', item.title)
        t.json_is('found.0.status', item.status)
        t.json_is('found.0.description', item.description)

        t.json_is('found.0.available.0.shelf_id', stock.shelf_id, 'полка')
        t.json_is('found.0.available.0.count', stock.count, 'количество')
        t.json_is('found.0.available.0.reserved', stock.reserve, 'резерв')
        t.json_is('found.0.available.0.shelf_type', stock.shelf_type)


def weight_barcode(article: int, weight: int):
    no_check = f'2{article:06d}{weight:05d}'
    return no_check + ean13_check_digit(no_check)


async def test_barcode_weight_product(tap, api, dataset):
    with tap.plan(16, 'Поиск весового товара'):
        article = random.randint(0, 999999)
        parent_barcode = weight_barcode(article, 0)
        parent = await dataset.product(
            barcode=[parent_barcode],
            products_scope=['russia'],
        )
        barcode1 = weight_barcode(article, 2013)
        child = await dataset.product(
            parent_id=parent.product_id,
            barcode=[barcode1],
            products_scope=['russia'],
            lower_weight_limit=2000,
            upper_weight_limit=2500,
        )
        barcode2 = weight_barcode(article, 2333)
        barcode_not_in_weight_limit = weight_barcode(article, 1128)

        company = await dataset.company(products_scope=['russia'])
        store   = await dataset.store(company=company)
        user    = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )
        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': barcode1})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found.0', 'found')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', child.product_id)
        t.json_is('found.0.external_id', child.external_id)
        t.json_hasnt('found.1', 'Only one product found')

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': barcode2})
        t.json_has('found.0', 'found')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', child.product_id)
        t.json_is('found.0.external_id', child.external_id)
        t.json_hasnt('found.1', 'Only one product found')

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': barcode_not_in_weight_limit})
        t.json_hasnt('found.0', 'No products found')


async def test_non_digit_barcode(tap, api, dataset, uuid):
    with tap.plan(4, 'Штрих-код с буквами'):
        company = await dataset.company(products_scope=['russia'])
        store = await dataset.store(company=company)
        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )
        t = await api(user=user)

        non_digit_barcode = '2Z' + uuid()[:11]
        await t.post_ok('api_tsd_barcode',
                        json={'barcode': non_digit_barcode})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('found.0', 'No products found')


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_barcode_title(tap, api, dataset, lang):
    with tap.plan(9, 'отдаем long_title в title, когда есть в locales'):
        article = random.randint(0, 999999)
        barcode1 = weight_barcode(article, 12)
        barcode2 = weight_barcode(article, 323)

        user = await dataset.user(lang=lang)

        products = [
            await dataset.product(
                title='нет перевода',
                barcode=[barcode1],
            ),
            await dataset.product(
                title='есть перевод',
                vars={
                    'locales': {
                        'long_title': {lang: f'есть перевод {lang}'}
                    }
                },
                barcode=[barcode2]
            ),
        ]

        tap.ok(products, 'создали товары')

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': barcode1})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('found.0.title', 'нет перевода')

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': barcode2})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('found.0.title', f'есть перевод {lang}')


async def test_barcode_true_mark(tap, dataset, api):
    with tap.plan(6, 'вытаскиваем баркод из честного знака'):
        user = await dataset.user(role='admin')

        product = await dataset.product(true_mark=True)
        true_mark = await dataset.true_mark_value(product=product)

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode', json={'barcode': true_mark})
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'product')
        t.json_is('found.0.product_id', product.product_id)
        t.json_is('found.0.true_mark', True, 'есть ЧЗ')


async def test_barcode_found_rack_zone(tap, api, dataset):
    with tap.plan(7, 'ищем зону РЦ'):
        store = await dataset.full_store()
        user = await dataset.user(role='admin', store=store)

        rack_zone = await dataset.rack_zone(store_id=store.store_id)

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': rack_zone.barcode})
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'rack_zone')
        t.json_is('found.0.rack_zone_id', rack_zone.rack_zone_id)
        t.json_is('found.0.title', rack_zone.title)
        t.json_is('found.0.status', rack_zone.status)


async def test_barcode_found_rack(tap, api, dataset):
    with tap.plan(7, 'ищем стеллаж'):
        store = await dataset.full_store()
        user = await dataset.user(role='admin', store=store)

        rack = await dataset.rack(store_id=store.store_id)

        t = await api(user=user)

        await t.post_ok('api_tsd_barcode',
                        json={'barcode': rack.barcode})
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('found.0.type', 'rack')
        t.json_is('found.0.rack_id', rack.rack_id)
        t.json_is('found.0.title', rack.title)
        t.json_is('found.0.status', rack.status)
