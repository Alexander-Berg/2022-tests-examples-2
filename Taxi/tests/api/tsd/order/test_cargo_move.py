import pytest


async def test_success(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(12, 'Создание ордера перемещения груза'):
        store = await dataset.store(type='dc', estatus='processing')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_cargo_move',
            json={
                'external_id': external_id,
                'shelf_id': cargo.shelf_id
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        order_id = t.res['json']['order']['order_id']
        order = await dataset.Order.load(order_id)
        tap.ok(order, 'Ордер создали')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'начальный статус')
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Успешно переведен в обработку'
        )
        tap.eq(order.type, 'cargo_move', 'Тип ордера')
        tap.eq(order.shelves, [cargo.shelf_id], 'Полки в ордере те')
        tap.eq(order.acks, [user.user_id], 'Пользователь проставился')
        tap.eq(order.source, 'tsd', 'Источник тот')


@pytest.mark.parametrize('store_params, http_code, code', [
    ({'type': 'dc', 'estatus': 'inventory'}, 423, 'ER_STORE_MODE'),
    ({'estatus': 'processing'}, 400, 'ER_BAD_REQUEST'),
])
async def test_wrong_store(
    tap, dataset, api, uuid, store_params, http_code, code):
    with tap.plan(3, 'Кривой склад'):
        store = await dataset.store(**store_params)
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo'
        )

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_cargo_move',
            json={
                'external_id': external_id,
                'shelf_id': cargo.shelf_id
            }
        )
        t.status_is(http_code, diag=True)
        t.json_is('code', code)


@pytest.mark.parametrize('shelf_params, http_code, code', [
    ({'type': 'store', 'rack_id': None}, 400, 'ER_BAD_REQUEST'),
    ({'rack_id': None}, 400, 'ER_BAD_REQUEST'),
    ({'status': 'removed'}, 400, 'ER_BAD_REQUEST'),
    ({'vars': {'order_external_id': '1'}}, 409, 'ER_CONFLICT'),
])
async def test_wrong_shelf(
    tap, dataset, api, uuid, shelf_params, http_code, code):
    with tap.plan(3, 'Кривая полка'):
        store = await dataset.store(type='dc', estatus='processing')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        params = {
            'store_id': store.store_id,
            'rack_id': rack.rack_id,
            'type': 'cargo',
        }
        params.update(shelf_params)
        cargo = await dataset.shelf(**params)

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_cargo_move',
            json={
                'external_id': external_id,
                'shelf_id': cargo.shelf_id
            }
        )
        t.status_is(http_code, diag=True)
        t.json_is('code', code)
