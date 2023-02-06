import pytest


async def test_suggests(api, tap, dataset):
    with tap.plan(16):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на складе')
        tap.eq(user.role, 'executer', 'роль')
        tap.eq(user.force_role, 'barcode_executer', 'роль итого')

        order = await dataset.order(status='processing',
                                    store=store,
                                    users=[user.user_id])
        tap.ok(order, 'Заказ создан')

        suggests = [ await dataset.suggest(order, suggest_order=10 - x)
                     for x in range(3)]
        tap.ok(suggests, 'саджесты сгенерированы')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_tsd_order_suggests',
                        json={'order_id': order.order_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        suggests.reverse()

        for i, suggest in enumerate(suggests):
            t.json_is(f'suggests.{i}.suggest_id',
                      suggest.suggest_id,
                      f'suggests[{i}].suggest_id')
            t.json_is(f'suggests.{i}.shelf_id',
                      suggest.shelf_id,
                      f'suggests[{i}].shelf_id')


@pytest.mark.parametrize('suggest_attrs', [
    {'count': 8},
    {'weight': 9}
])
async def test_suggests_fields(tap, dataset, api, suggest_attrs):
    with tap.plan(11, 'Поля саджестов'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на складе')

        order = await dataset.order(status='processing',
                                    store=store,
                                    users=[user.user_id])
        tap.ok(order, 'Заказ создан')

        suggests = [
            await dataset.suggest(order, suggest_order=1, **suggest_attrs)
        ]
        tap.ok(suggests[0], 'Саджест создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_suggests',
                        json={'order_id': order.order_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        s = suggests[0]
        t.json_is('suggests.0.suggest_id', s.suggest_id)
        for attr in ('count', 'weight'):
            t.json_is(f'suggests.0.{attr}', getattr(s, attr))


async def test_suggests_other_order(api, tap, dataset):
    with tap.plan(10):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(role='barcode_executer', store=store)
        tap.ok(user, 'пользователь сгенерирован')
        tap.eq(user.store_id, store.store_id, 'на складе')
        tap.eq(user.role, 'executer', 'роль')
        tap.eq(user.force_role, 'barcode_executer', 'роль итого')

        order = await dataset.order(status='processing',
                                    users=[user.user_id])
        tap.ok(order, 'Заказ сгенерирован')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_tsd_order_suggests',
                        json={'order_id': order.order_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


