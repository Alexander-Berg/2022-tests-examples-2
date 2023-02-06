# pylint: disable=too-many-locals

import pytest

from stall.model.order import Order
from stall.model.stock import Stock


@pytest.mark.parametrize('variant', [
    {
        'type': 'store',
        'reason': None,
        'desc': 'На обычную полку',
    },
    {
        'type': 'kitchen_components',
        'reason': None,
        'desc': 'На полку для ингредиентов',
    },
    {
        'type': 'trash',
        'reason': {
            'code': 'TRASH_DAMAGE',
        },
        'desc': 'Списание: повреждение',
    },
    {
        'type': 'trash',
        'reason': {
            'code': 'TRASH_TTL',
        },
        'desc': 'списание: срок годности',
    },
    {
        'type': 'trash',
        'reason': {
            'code': 'TRASH_DECAYED',
        },
        'desc': 'списание: нетоварный вид',
    },
    {
        'type': 'trash',
        'reason': {'code': 'TRASH_ORDINANCE'},
        'desc': 'списание: по распоряжению',
    },
    {
        'type': 'trash',
        'reason': {'code': 'TRASH_MOL'},
        'desc': 'списание: на сотрудника',
    },
    {
        'type': 'trash',
        'reason': {'code': 'TRASH_ACCIDENT'},
        'desc': 'списание: поломка оборудования',
    },
    {
        'type': 'trash',
        'reason': {
            'code': 'COMMENT',
            'comment': 'коментарий',
        },
        'desc': 'списание: причину указал кладовщик',
    },
])
async def test_move(tap, api, dataset, uuid, variant, wait_order_status):
    with tap.plan(32, f'создание ордера: {variant["desc"]}'):
        del variant['desc']

        store = await dataset.store()

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id,
                                    type=variant['type'])
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.eq(shelf.type, variant['type'], f'тип полки: {variant["type"]}')

        stock = await dataset.stock(store_id=user.store_id)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        stock2 = await dataset.stock(
            store_id=user.store_id,
            reserve=10,
            count=20,
            shelf_id=stock.shelf_id,
        )
        tap.eq(stock2.store_id, user.store_id, 'ещё остаток там же')
        tap.ne(stock2.product_id, stock.product_id, 'другой товар')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'та же полка')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }
        if variant.get('reason'):
            request['reason'] = variant.get('reason')

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'move')
        t.json_is('order.status', 'reserving')
        t.json_is('order.estatus', 'begin')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')

        order = await Order.load((user.store_id, external_id), by='external')
        tap.ok(order, 'заказ найден')
        t.json_is('order.order_id', order.order_id)

        r = await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(r, 'Перемещение выполнено')

        stocks = await Stock.list(
            by='full',
            conditions=(
                ('shelf_id', {shelf.shelf_id}),
                ('product_id', {stock.product_id}),
            ),
            sort=(),
        )
        tap.ok(stocks, 'Получили остаток')
        tap.eq(list(stocks)[0].shelf_id, shelf.shelf_id, 'Посылка перемещена')

        tap.eq(len(order.required), 1, 'количество в required')

        with order.required[0] as r:
            tap.eq(r.product_id, stock.product_id, 'product_id')
            tap.eq(r.count, stock.count, 'count')
            tap.eq(r.dst_shelf_id, shelf.shelf_id, 'dst_shelf_id')
            tap.eq(r.src_shelf_id, stock.shelf_id, 'src_shelf_id')

            reason = variant.get('reason') or {'code': 'OPTIMIZE'}
            tap.eq(r.reason_code, reason['code'], 'Код ризон')
            tap.eq(r.reason_comment, reason.get('comment'), 'коммент')


async def test_move_item(tap, api, dataset, uuid, wait_order_status):
    with tap.plan(26, 'перемещение посылок между полками'):
        store = await dataset.store()

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id, type='parcel')
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.eq(shelf.type, 'parcel', 'тип полки: parcel')

        item = await dataset.item(store=store)
        stock = await dataset.stock(
            item=item,
            store_id=user.store_id,
            reserve=0,
            count=1,
        )
        tap.eq(stock.store_id, user.store_id, 'ещё остаток там же')
        tap.eq(stock.product_id, item.item_id, 'item_id')
        tap.ne(stock.shelf_id, shelf.shelf_id, 'полка назначения отличается')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'item_id': item.item_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }

        await t.post_ok('api_tsd_order_move', json={
            'order_id': external_id,
            'move': [request],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'move')
        t.json_is('order.status', 'reserving')
        t.json_is('order.estatus', 'begin')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)

        order = await Order.load((user.store_id, external_id), by='external')
        tap.ok(order, 'заказ найден')
        t.json_is('order.order_id', order.order_id)

        r = await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.ok(r, 'Перемещение выполнено')

        stocks = await Stock.list(
            by='full',
            conditions=(
                ('shelf_id', {shelf.shelf_id}),
            ),
            sort=(),
        )
        tap.ok(stocks, 'Получили остаток на полке назначения')
        tap.eq(len(list(stocks)), 1, 'На полке назначения 1 посылка')
        tap.eq(list(stocks)[0].shelf_id, shelf.shelf_id, 'Посылка перемещена')

        stocks = await Stock.list(
            by='full',
            conditions=(
                ('shelf_id', {stock.shelf_id}),
            ),
            sort=(),
        )
        tap.ok(stocks, 'Получили остаток на начальной полке')
        tap.eq(list(stocks)[0].count, 0, 'На начальной полке 0 посылок')


async def test_error_no_item(tap, dataset, wait_order_status):
    with tap.plan(5, 'перемещение посылки, с соседней полки'):
        stock = await dataset.stock(shelf_type='parcel')
        tap.ok(stock, 'остаток создан')

        stock_two = await dataset.stock(
            shelf_type='parcel',
            store_id=stock.store_id,
        )
        tap.ok(stock_two, 'остаток создан на второй полке')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            required=[
                {
                    'item_id': stock.product_id,
                    'count': stock.count,
                    'src_shelf_id': stock_two.shelf_id,
                    'dst_shelf_id': stock.shelf_id,
                }
            ]
        )
        tap.ok(order, 'ордер создан')

        res = await wait_order_status(order, ('failed', 'done'))
        tap.ok(res, 'Не смогли переместить')


async def test_removed_shelf(tap, api, dataset, uuid):
    with tap.plan(6, 'Перемещение на полку removed'):
        store = await dataset.store()

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        stock = await dataset.stock(
            store_id=user.store_id,
            count=20,
        )
        shelf = await dataset.shelf(
            store_id=user.store_id,
            type='store',
            status='removed',
        )
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.ne(stock.shelf_id, shelf.shelf_id, 'не та же полка')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': external_id,
            'move': [request],
        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_move_error(tap, api, dataset, uuid):
    with tap.plan(5, 'Ошибки полок'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user.store_id, 'пользователь создан')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': uuid(),
                            'move': [
                                {
                                    'product_id': uuid(),
                                    'count': 234,
                                    'src_shelf_id': uuid(),
                                    'dst_shelf_id': uuid(),
                                }
                            ]
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Bad request')


async def test_move_reserved(tap, api, dataset, uuid):
    with tap.plan(13, 'товар зарезервирован'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id)
        tap.eq(shelf.store_id, user.store_id, 'полка создана')

        stock = await dataset.stock(store_id=user.store_id,
                                    count=22,
                                    reserve=1)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [
                                {
                                    'product_id': stock.product_id,
                                    'count': stock.count,
                                    'src_shelf_id': stock.shelf_id,
                                    'dst_shelf_id': shelf.shelf_id,
                                }
                            ]
                        })
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Bad request parameters')
        t.json_is('details.errors.0.code', 'ER_COUNT_OR_RESERVE')
        t.json_is('details.errors.0.message',
                  'Too low product or has reserved')
        t.json_is('details.errors.0.product_id', stock.product_id)
        t.json_is('details.errors.0.shelf_id', stock.shelf_id)
        t.json_is('details.errors.0.count', stock.count)
        t.json_is('details.errors.0.reserve', stock.reserve)


@pytest.mark.parametrize('variant', [
    {
        'desc': 'Нет ризона',
        'detail_code': 'ER_WRONG_REASON',
        'http_code': 410,
        'error_code': 'ER_CONFLICT',
        'estatus': 'processing',
    },
    {
        'desc': 'Неправильный ризон',
        'detail_code': 'ER_WRONG_REASON',
        'reason': {'code': 'OPTIMIZE'},
        'http_code': 410,
        'error_code': 'ER_CONFLICT',
        'estatus': 'processing',
    },
    {
        'desc': 'Нет комментария',
        'detail_code': 'ER_NO_COMMENT',
        'reason': {'code': 'COMMENT'},
        'http_code': 410,
        'error_code': 'ER_CONFLICT',
        'estatus': 'processing',
    },
])
async def test_conflicts(tap, api, dataset, uuid, variant):
    with tap.plan(10, f'товар зарезервирован: {variant["desc"]}'):
        store = await dataset.store(estatus=variant['estatus'])
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id, type='trash')
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.eq(shelf.type, 'trash', 'полка списания')

        stock = await dataset.stock(store_id=user.store_id,
                                    count=22,
                                    reserve=1)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }
        if variant.get('reason'):
            request['reason'] = variant['reason']

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.status_is(variant['http_code'], diag=True)
        t.json_is('code', variant['error_code'])
        t.json_is('message', 'Bad request parameters')
        t.json_is('details.errors.0.code', variant['detail_code'])


@pytest.mark.parametrize('estatus',
                         ['inventory_begin', 'inventory_finish', 'inventory'])
async def test_inventarize(tap, api, dataset, estatus, uuid):
    with tap.plan(8, 'Ошибки move при других режимах склада'):
        store = await dataset.store(estatus=estatus)
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id)
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.eq(shelf.type, 'store', 'полка тёплая')

        stock = await dataset.stock(store_id=user.store_id,
                                    count=22,
                                    reserve=1)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
        }

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_STORE_MODE')


@pytest.mark.parametrize('src_shelf_type', ['trash', 'kitchen_trash'])
async def test_er_access(tap, api, dataset, uuid, src_shelf_type):
    with tap.plan(5, 'Перемещение с полки списания без пермита'):
        store = await dataset.store()
        user = await dataset.user(role='barcode_executer', store=store)

        stock = await dataset.stock(
            store_id=user.store_id,
            shelf_type=src_shelf_type,
            count=20,
        )
        shelf = await dataset.shelf(
            store_id=user.store_id,
        )
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.ne(stock.shelf_id, shelf.shelf_id, 'не та же полка')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
            'reason': {
                'code': 'TRASH_DAMAGE',
            },
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': external_id,
            'move': [request],
        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('src_shelf_type', ['trash', 'kitchen_trash'])
async def test_er_wrong_required(tap, api, dataset, uuid, src_shelf_type):
    with tap.plan(7, 'Перемещение с полки списания с неверными полями'):
        store = await dataset.store()
        user = await dataset.user(role='vice_store_admin', store=store)

        stock = await dataset.stock(
            store_id=user.store_id,
            shelf_type=src_shelf_type,
            count=20,
        )
        shelf = await dataset.shelf(
            store_id=user.store_id, shelf_type=src_shelf_type,
        )
        tap.eq(shelf.store_id, user.store_id, 'полка создана')
        tap.ne(stock.shelf_id, shelf.shelf_id, 'не та же полка')

        t = await api(user=user)
        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf.shelf_id,
            'stock_id': stock.stock_id,
            'reason': {
                'code': 'TRASH_DAMAGE',
            },
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': uuid(),
            'move': [request],
        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors[0].code', 'ER_WRONG_REQUIRED')
        t.json_is(
            'details.errors[0].message',
            'Moving from trash required stock_id and stock reason'
        )


@pytest.mark.parametrize(
    'src_shelf_type, dst_shelf_type',
    [
        ('trash', 'store'),
        ('kitchen_trash', 'kitchen_components')
    ]
)
async def test_ok_from_trash(
        tap, api, dataset, uuid, wait_order_status,
        src_shelf_type, dst_shelf_type
):
    with tap.plan(28, 'Успешное перемещение с полки списания'):
        store = await dataset.store()
        user = await dataset.user(role='vice_store_admin', store=store)

        stock_1 = await dataset.stock(
            store_id=user.store_id,
            shelf_type=dst_shelf_type,
            count=20,
        )
        trash_shelf = await dataset.shelf(
            store_id=user.store_id, type=src_shelf_type,
        )
        tap.eq(trash_shelf.store_id, user.store_id, 'полка создана')
        tap.ne(stock_1.shelf_id, trash_shelf.shelf_id, 'вторая полка')

        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock_1.store_id,
            required=[
                {
                    'product_id': stock_1.product_id,
                    'count': 20,
                    'src_shelf_id': stock_1.shelf_id,
                    'dst_shelf_id': trash_shelf.shelf_id,
                }
            ]
        )
        await wait_order_status(order, ('complete', 'done'))

        stock_2 = (await Stock.list_by_product(
            product_id=stock_1.product_id,
            store_id=store.store_id,
            shelf_type=src_shelf_type,
            empty=True,
        ))[0]
        tap.eq_ok(stock_2.count, 20, 'второй остаток создан')

        t = await api(user=user)
        external_id = uuid()
        request = {
            'product_id': stock_1.product_id,
            'count': 4,
            'src_shelf_id': trash_shelf.shelf_id,
            'dst_shelf_id': stock_1.shelf_id,
            'stock_id': stock_2.stock_id,
            'move_order_id': order.order_id,
            'reason': {
                'code': 'TRASH_DAMAGE',
            },
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': external_id,
            'move': [request],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'move')
        t.json_is('order.status', 'reserving')
        t.json_is('order.estatus', 'begin')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')

        res_order = await Order.load(
            (user.store_id, external_id), by='external')
        tap.ok(res_order, 'заказ найден')
        t.json_is('order.order_id', res_order.order_id)

        r = await wait_order_status(
            res_order, ('complete', 'done'), user_done=user)
        tap.ok(r, 'Перемещение выполнено')

        stocks = sorted(await Stock.list(
            by='full',
            conditions=(
                ('product_id', {stock_1.product_id}),
            ),
            sort=(),
        ), key=lambda x: x.count)
        tap.eq_ok({s.count for s in stocks}, {16, 4}, 'остатки перемещены')
        tap.eq(len(res_order.required), 1, 'количество в required')

        with res_order.required[0] as r:
            tap.eq(r.product_id, stock_1.product_id, 'product_id')
            tap.eq(r.count, 4, 'count')
            tap.eq(r.dst_shelf_id, request['dst_shelf_id'], 'dst_shelf_id')
            tap.eq(r.src_shelf_id, request['src_shelf_id'], 'src_shelf_id')

            tap.eq(r.reason_code, request['reason']['code'], 'Код ризон')
            tap.eq(r.reason_comment, None, 'коммент')


async def test_wrong_to_office(tap, api, dataset, uuid):
    with tap.plan(5, 'Перемещение на полку office товаров'):
        store = await dataset.store(options={'exp_illidan': True})
        user = await dataset.user(role='vice_store_admin', store=store)

        src_shelf = await dataset.shelf(
            store_id=user.store_id,
            type='store',
        )

        stock = await dataset.stock(
            store_id=user.store_id,
            shelf_id=src_shelf.shelf_id,
            count=20,
        )

        dst_shelf = await dataset.shelf(
            store_id=user.store_id,
            type='office',
        )

        t = await api(user=user)
        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': src_shelf.shelf_id,
            'dst_shelf_id': dst_shelf.shelf_id,
            'stock_id': stock.stock_id,
            'reason': {
                'code': 'TRASH_DAMAGE',
            },
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': uuid(),
            'move': [request],
        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors[0].code', 'ER_WRONG_DST_SHELF')
        t.json_is(
            'details.errors[0].message',
            f'Can\'t move to {dst_shelf.title}'
        )


async def test_wrong_from_office(tap, api, dataset, uuid):
    with tap.plan(5, 'перемещение расходников с полки office'):
        store = await dataset.store(options={'exp_illidan': True})
        user = await dataset.user(role='vice_store_admin', store=store)

        consumable = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )

        src_shelf = await dataset.shelf(
            store_id=user.store_id,
            type='office',
        )

        stock = await dataset.stock(
            product_id=consumable.product_id,
            store_id=user.store_id,
            shelf_id=src_shelf.shelf_id,
            count=20,
        )

        dst_shelf = await dataset.shelf(
            store_id=user.store_id,
            type='store',
        )

        t = await api(user=user)
        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': src_shelf.shelf_id,
            'dst_shelf_id': dst_shelf.shelf_id,
            'stock_id': stock.stock_id,
            'reason': {
                'code': 'TRASH_DAMAGE',
            },
        }
        await t.post_ok('api_tsd_order_move', json={
            'order_id': uuid(),
            'move': [request],
        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.errors[0].code', 'ER_WRONG_DST_SHELF')
        t.json_is(
            'details.errors[0].message',
            f'Can\'t move to {dst_shelf.title}'
        )


async def test_move_to_repacking(tap, api, dataset, uuid, wait_order_status):
    with tap.plan(30, 'создание ордера на полку перефасовка'):

        store = await dataset.store()

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store_id=user.store_id,
                                    type='store')
        tap.eq(shelf.store_id, user.store_id, 'полка создана')

        shelf2 = await dataset.shelf(store_id=user.store_id,
                                     type='repacking')
        tap.eq(shelf2.store_id, user.store_id, 'полка 2 создана')

        stock = await dataset.stock(store_id=user.store_id, shelf=shelf)
        tap.eq(stock.store_id, user.store_id, 'остаток создан')

        t = await api(user=user)
        external_id = uuid()

        request = {
            'product_id': stock.product_id,
            'count': stock.count,
            'src_shelf_id': stock.shelf_id,
            'dst_shelf_id': shelf2.shelf_id,
        }

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user = await dataset.user(role='executer', store=store)
        tap.ok(user.store_id, 'пользователь вошел по пинкоду')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_move',
                        json={
                            'order_id': external_id,
                            'move': [request]
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Order created')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'move')
        t.json_is('order.status', 'reserving')
        t.json_is('order.estatus', 'begin')
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')

        order = await Order.load((user.store_id, external_id), by='external')
        tap.ok(order, 'заказ найден')
        t.json_is('order.order_id', order.order_id)

        r = await wait_order_status(
            order, ('complete', 'done'), user_done=user)
        tap.ok(r, 'Перемещение выполнено')

        tap.eq(len(order.required), 1, 'количество в required')

        with order.required[0] as r:
            tap.eq(r.product_id, stock.product_id, 'product_id')
            tap.eq(r.count, stock.count, 'count')
            tap.eq(r.src_shelf_id, stock.shelf_id, 'src_shelf_id')
            tap.eq(r.dst_shelf_id, shelf2.shelf_id, 'dst_shelf_id')

        stocks = await Stock.list(
            by='full',
            conditions=(
                ('product_id', {stock.product_id}),
            ),
            sort=(),
        )
        tap.eq(
            {
                (stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (shelf.shelf_id, 0),
                (shelf2.shelf_id, stock.count),
            },
            'Первая полка пуста, на второй весь товар'
        )
