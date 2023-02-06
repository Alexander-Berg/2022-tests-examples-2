async def test_my_store(tap, api, dataset):
    with tap.plan(15, 'Проверка может ли смотреть свой склад админ склада'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на складе')
        tap.eq(user.role, 'store_admin', 'роль')

        other = await dataset.user(role='store_admin')
        tap.ok(other, 'другой пользователь сгенерирован')
        tap.eq(other.role, 'store_admin', 'роль')
        tap.ok(other.store_id, 'склад у него есть')
        tap.ne(other.store_id, user.store_id, 'на другом складе')


        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_stores_load',
                        json={'store_id': user.store_id})
        t.status_is(200, diag=True, desc='Может смотреть свой склад')
        t.json_is('store.store_id', store.store_id)


        await t.post_ok('api_admin_stores_load',
                        json={'store_id': other.store_id})
        t.status_is(403, diag=True, desc='Не может смотреть чужой склад')
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


async def test_stores(tap, api, dataset):
    with tap.plan(16, 'Проверка может ли смотреть свой склад админ склада'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на складе')
        tap.eq(user.role, 'store_admin', 'роль')

        other = await dataset.user(role='admin')
        tap.ok(other, 'другой пользователь сгенерирован')
        tap.eq(other.role, 'admin', 'роль')
        tap.ok(other.store_id, 'склад у него есть')
        tap.ne(other.store_id, user.store_id, 'на другом складе')


        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_stores_seek',
                        json={})
        t.status_is(403, diag=True, desc='Не может смотреть чужой склад')
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')

        t.set_user(other)
        await t.post_ok('api_admin_stores_seek',
                        json={})
        t.status_is(200, diag=True, desc='Не может смотреть чужой склад')
        t.json_is('code', 'OK')
        t.json_has('stores', 'Склады в ответе')

