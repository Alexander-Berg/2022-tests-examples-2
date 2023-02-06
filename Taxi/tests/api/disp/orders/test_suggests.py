import pytest


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_suggests(tap, dataset, api, role):
    with tap.plan(13, 'Саджесты по заказу в диспетчерской'):
        admin = await dataset.user(role=role)
        tap.ok(admin, f'Админ склада создан: {role}')
        tap.eq(admin.role, role, 'Его роль')
        tap.ok(admin.store_id, 'привязан к складу')

        order = await dataset.order(store_id=admin.store_id)
        tap.ok(order, 'заказ создан')

        suggests = [await dataset.suggest(order, suggest_order=10 - x)
                    for x in range(5)]
        tap.ok(suggests, 'Саджесты созданы')

        t = await api(user=admin)
        await t.post_ok('api_disp_orders_suggests',
                        json={'order_id': order.order_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        suggests.sort(key=lambda x: x.order)

        for i, s in enumerate(suggests):
            t.json_is(f'suggests.{i}.suggest_id', s.suggest_id)
