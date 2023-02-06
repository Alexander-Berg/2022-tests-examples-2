async def test_racks_log(tap, dataset, api):
    with tap.plan(9, 'лог событий по заказу'):
        admin = await dataset.user(role='admin')
        tap.ok(admin.store_id, 'админ сгенерирован')
        t = await api(user=admin)

        rack = await dataset.rack(store_id=admin.store_id)

        order = await dataset.order(store_id=admin.store_id)
        tap.ok(order, 'заказ сгенерирован')

        tap.ok(
            await rack.do_reserve(order=order, user_id=admin.user_id),
            'Сделали резерв места на стеллаже'
        )

        await t.post_ok('api_disp_orders_racks_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 1,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('racks_log.0')
        t.json_is('racks_log.0.rack_id', rack.rack_id)
        t.json_hasnt('racks_log.1')
