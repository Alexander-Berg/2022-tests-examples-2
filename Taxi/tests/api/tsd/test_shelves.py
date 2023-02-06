import pytest

@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
@pytest.mark.parametrize('by', ['ids', 'shelf_ids'])
async def test_shelves(tap, api, dataset, role, by, uuid):
    with tap.plan(23):
        unexists = uuid()

        user = await dataset.user(role=role)
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.role, 'executer', 'роль')
        if role == 'barcode_executer':
            tap.eq(user.force_role, role, 'force_role')
        else:
            tap.eq(user.force_role, None, 'force_role')

        shelf = await dataset.shelf(store_id=user.store_id, rack='прив')
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, user.store_id, 'на складе')

        shelf2 = await dataset.shelf()
        tap.ok(shelf2, 'полка создана')
        tap.ne(shelf2.store_id, user.store_id, 'на складе')


        t = await api(user=user)
        await t.post_ok('api_tsd_shelves',
                        json={by: [shelf.shelf_id, shelf2.shelf_id, unexists]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        t.json_is('shelves.0.shelf_id', shelf.shelf_id)
        t.json_is('shelves.0.title', shelf.title)
        t.json_is('shelves.0.barcode', shelf.barcode)
        t.json_is('shelves.0.tags', shelf.tags)
        t.json_is('shelves.0.type', shelf.type)
        t.json_is('shelves.0.rack', shelf.rack)

        t.json_is('errors.0.shelf_id', shelf2.shelf_id)
        t.json_is('errors.0.code', 'ER_NOT_EXISTS')
        t.json_is('errors.0.message', 'Shelf is not exists')

        t.json_is('errors.1.shelf_id', unexists)
        t.json_is('errors.1.code', 'ER_NOT_EXISTS')
        t.json_is('errors.1.message', 'Shelf is not exists')



@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
@pytest.mark.parametrize('by', ['ids', 'shelf_ids'])
async def test_shelves_empty_ids(tap, api, dataset, role, by):
    with tap.plan(8):
        user = await dataset.user(role=role)
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.role, 'executer', 'роль')
        if role == 'barcode_executer':
            tap.eq(user.force_role, role, 'force_role')
        else:
            tap.eq(user.force_role, None, 'force_role')

        t = await api(user=user)
        await t.post_ok('api_tsd_shelves', json={by: []})
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'code')
        t.json_is('message', 'shelf ids is not defined or empty')

