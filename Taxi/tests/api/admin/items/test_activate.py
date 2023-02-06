import pytest


@pytest.mark.parametrize('status', ['active', 'inactive'])
async def test_activate_item(dataset, api, tap, status, uuid):
    with tap.plan(5, 'Активация посылки c непустым стоком'):
        store = await dataset.store()
        item = await dataset.item(store=store, status=status)

        shelf = await dataset.shelf(store=store, type='parcel')
        stock = await dataset.stock(
            store=store,
            product=item,
            shelf=shelf,
            shelf_type='parcel',
            lot=uuid(),
            count=1
        )
        tap.eq(stock.count, 1, 'непустой остаток создан')

        t = await api(role='support_it')

        await t.post_ok(
            'api_admin_items_activate',
            json={'item_id': item.item_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await item.reload()

        tap.eq(item.status, 'active', 'Посылка активна')


async def test_empty_stock(dataset, api, tap, uuid):
    with tap.plan(4, 'Активация посылки с пустым стоком'):
        store = await dataset.store()
        item = await dataset.item(store=store)

        shelf = await dataset.shelf(store=store, type='parcel')
        stock = await dataset.stock(
            store=store,
            product=item,
            shelf=shelf,
            shelf_type='parcel',
            lot=uuid(),
            count=1,
            reserve=1,
        )

        order = await dataset.order(store_id=stock.store_id)
        stock = await stock.do_sale(order=order, count=1)
        tap.eq(stock.count, 0, 'пустой остаток создан')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_items_activate',
            json={'item_id': item.item_id}
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_stock_not_found(dataset, api, tap):
    with tap.plan(3, 'Активация посылки без стока'):
        store = await dataset.store()
        item = await dataset.item(store=store)

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_items_activate',
            json={'item_id': item.item_id}
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_activate_item_not_found(tap, api):
    with tap.plan(3, 'Экземпляра нет'):
        t = await api(role='admin')

        fake_item_id = '0' * 12

        await t.post_ok(
            'api_admin_items_activate',
            json={'item_id': fake_item_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role, expected_code', [
    ('admin', 200),
    ('support', 200),
    ('supervisor', 403),
    ('store_admin', 403)
])
async def test_permit(tap, dataset, api, role, expected_code, uuid):
    with tap.plan(3, 'Проверка права с ролью'):
        store = await dataset.store()
        item = await dataset.item(store=store)

        shelf = await dataset.shelf(store=store, type='parcel')
        stock = await dataset.stock(
            store=store,
            product=item,
            shelf=shelf,
            shelf_type='parcel',
            lot=uuid(),
            count=1,
        )

        tap.eq(stock.count, 1, 'непустой остаток создан')

        t = await api(role=role)
        await t.post_ok(
            'api_admin_items_activate',
            json={'item_id': item.item_id}
        )
        t.status_is(expected_code, diag=True)
