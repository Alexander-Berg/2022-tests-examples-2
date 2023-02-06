import pytest

from stall.model.shelf import Shelf, SHELF_TYPES


@pytest.mark.parametrize('shelf_type', SHELF_TYPES)
async def test_shelf_types(tap, api, uuid, shelf_type, dataset):
    with tap.plan(7):
        user = await dataset.user(role='admin')
        tap.ok(user, 'Создали пользователя')

        external_id = uuid()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'external_id': external_id,
                'type': shelf_type,
                'title': uuid(),
            }
        )
        t.status_is(200, diag=True)

        shelf = await Shelf.load([user.store_id, external_id], by='external')

        await t.post_ok(
            'api_admin_shelves_load',
            json={'shelf_id': [shelf.shelf_id]}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('shelf.0.type', shelf_type)


async def test_change_shelf_type(tap, api, dataset):
    with tap.plan(6, 'Смена типа полки'):
        store = await dataset.store()

        shelf = await dataset.shelf(type='markdown', store=store)
        tap.ok(shelf, 'Полка создана')
        tap.eq(shelf.type, 'markdown', 'Правильный исходный тип полки')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': shelf.shelf_id,
                'type': 'store',
            }
        )
        t.status_is(200, diag=True)
        tap.ok(await shelf.reload(), 'Перезагрузить полку')
        tap.eq(shelf.type, 'store', 'У полки новый тип')


async def test_change_shelf_type_stocks(tap, api, dataset):
    with tap.plan(7, 'Смена типа полки с остатками'):
        store = await dataset.store()

        shelf = await dataset.shelf(type='markdown', store=store, title='мед.')
        tap.ok(shelf, 'Полка создана')
        tap.eq(shelf.type, 'markdown', 'Правильный исходный тип полки')
        tap.ok(await dataset.stock(shelf=shelf, count=1), 'Созданы остатки')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': shelf.shelf_id,
                'type': 'store',
            }
        )
        t.status_is(409, diag=True)
        tap.ok(await shelf.reload(), 'Перезагрузить полку')
        tap.eq(shelf.type, 'markdown', 'У полки тип не изменился')
