import pytest


@pytest.mark.parametrize('role', ['expansioner', 'admin'])
async def test_create_rack_limited(tap, dataset, api, role, cfg):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)
        t = await api()
        t.set_user(user)
        cfg.set('business.shelves.qty_limit', 20)
        shelves_number = 21
        order = 11
        await t.post_ok(
            'api_admin_shelves_create_rack',
            json={'store_id': store.store_id,
                  'rack': 'стеллаж1',
                  'order': order,
                  'shelves_number': shelves_number,
                  'prefix': 'ББ',
                  'tags': ['refrigerator', 'freezer'],
                  'type': 'store'})
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'Too many shelves to create')


@pytest.mark.parametrize('role', ['expansioner', 'admin'])
async def test_create_rack_unlimited(tap, dataset, api, role, cfg):
    with tap.plan(24):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)
        t = await api()
        t.set_user(user)
        cfg.set('business.shelves.qty_limit', 20)
        shelves_number = 21
        no_limit_qty = True
        order = 11
        await t.post_ok(
            'api_admin_shelves_create_rack',
            json={'store_id': store.store_id,
                  'rack': 'стеллаж1',
                  'order': order,
                  'shelves_number': shelves_number,
                  'no_limit_qty': no_limit_qty,
                  'prefix': 'ББ',
                  'tags': ['refrigerator', 'freezer'],
                  'type': 'store'})
        t.status_is(200, diag=True)
        t.json_has('shelves')
        shelves = [
            {k: s[k] for k in ('rack', 'order', 'title', 'user_id',
                               'tags', 'type', 'store_id', 'status')}
            for s in t.res['json']['shelves']
        ]
        for i in range(1, shelves_number + 1):
            tap.eq_ok(
                shelves[i - 1],
                {'title': f'ББ-{i}',
                 'rack': 'стеллаж1',
                 'order': order + i - 1,
                 'store_id': store.store_id,
                 'tags': ['refrigerator', 'freezer'],
                 'type': 'store',
                 'user_id': user.user_id,
                 'status': 'active'},
                f'Полка {i} создана правильно'
            )


async def test_titles_duplicate(tap, dataset, api, cfg):
    with tap.plan(6, 'Дубли названий при создании стеллада'):
        cfg.set('business.shelves.qty_limit', 20)
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store, title='ББ-3')
        tap.ok(shelf, 'Создали полку')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_shelves_create_rack',
            json={
                'store_id': store.store_id,
                'rack': 'стеллаж1',
                'order': 9,
                'shelves_number': 9,
                'prefix': 'ББ',
                'tags': ['refrigerator', 'freezer'],
                'type': 'store'
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Duplicate titles')

        store_shelves = await shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(store_shelves), 1, 'Одна полка так и осталась')
