async def test_get_portions(tap, api, dataset, uuid):
    with tap.plan(6, 'Проверяем разбивку по стокам'):
        store = await dataset.store()

        product = await dataset.product()
        trash = await dataset.shelf(
            store=store,
            type='trash'
        )
        reasons = [
            {
                uuid():
                    {
                        'count': 0, 'reason_code': 'TRASH_MOVE'
                    }
            },
            {
                uuid():
                    {
                        'count': -4, 'reason_code': 'TRASH_MOVE'
                    }
            },
            {
                uuid():
                    {
                        'count': 3, 'reason_code': 'TRASH_TTL'
                    }
            },
            {
                uuid():
                    {
                        'count': 2, 'reason_code': 'TRASH_OPTIMIZE'
                    }
            },
                ]
        await dataset.stock(
            store_id=store.store_id,
            shelf_id=trash.shelf_id,
            count=5,
            shelf_type='trash',
            product_id=product.product_id,
            lot=uuid(),
            vars={
                'reasons': reasons
            }
        )
        user = await dataset.user(
            role='admin',
            store_id=store.store_id,
        )

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_get_portions',
            json={
                'shelf_id': trash.shelf_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('portions', 'portions')
        portions = t.res['json']['portions']

        tap.ok(len(portions), 2, 'Разбил на 2')

        tap.ok(
            sum(
                portion['count'] for portion in portions
            ),
            5,
            'Суммарно верное число'
        )

        tap.eq_ok(
            set(
                portion['reason_code'] for portion in portions
            ),
            set(['TRASH_TTL', 'TRASH_OPTIMIZE']),
            'Причины записаны верное'
        )
