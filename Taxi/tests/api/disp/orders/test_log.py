async def test_log(tap, dataset, api):
    with tap.plan(22, 'лог событий по заказу'):
        admin = await dataset.user(role='admin')
        tap.ok(admin.store_id, 'админ сгенерирован')
        t = await api(user=admin)

        order = await dataset.order(store_id=admin.store_id)
        tap.ok(order, 'заказ сгенерирован')

        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 1,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('log.0.serial')
        t.json_has('log.0.lsn')
        t.json_has('log.0.order_id')
        t.json_has('log.0.source')
        t.json_has('log.0.created')
        t.json_has('log.0.status')
        t.json_has('log.0.estatus')
        t.json_has('log.0.eda_status')
        t.json_has('log.0.user_id')
        t.json_has('log.0.suggest_id')
        t.json_has('log.0.vars')

        t.json_like('cursor', r'\S')

        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': t.res['json']['cursor'],
                            'limit': 1,
                        },
                        desc='Вторая страница')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_hasnt('log.0')


# В LAVKADEV-1180 разбираемся с параметром лимита
# @pytest.mark.xfail(reason='лог-лимит параметр не работает')
# async def test_log_limit(tap, dataset, api):
#     logs_count = 200
#     admin = await dataset.user(role='admin')
#     tap.ok(admin.store_id, 'админ сгенерирован')
#     order = await dataset.order(store_id=admin.store_id)
#     tap.ok(order, 'заказ сгенерирован')
#     for _ in range(logs_count):
#         a = await dataset.user(role='admin', store_id=admin.store_id)
#         await order.ack(a)
#     t = await api(user=admin)
#     await t.post_ok(
#         'api_disp_orders_log',
#         json={
#             'order_id': order.order_id,
#             'cursor': None,
#             'limit': logs_count,
#         }
#     )
#     t.status_is(200, diag=True)
#     t.json_is('code', 'OK')
#     tap.ok(len(t.res['json']['log']) > 100, 'логов больше сотни')


async def test_log_list(tap, dataset, api):
    async def fetch_log(cursor):
        return await t.post_ok(
            'api_disp_orders_log',
            json={
                'order_id': order.order_id,
                'cursor': cursor,
            }
        )

    logs_count = 1000  # много больше лимита
    admin = await dataset.user(role='admin')
    tap.ok(admin.store_id, 'админ сгенерирован')
    order = await dataset.order(store_id=admin.store_id)
    tap.ok(order, 'заказ сгенерирован')
    for _ in range(logs_count):
        a = await dataset.user(role='admin', store_id=admin.store_id)
        await order.ack(a)

    t = await api(user=admin)
    await fetch_log(cursor=None)
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    first_page_lsns = [l['lsn'] for l in t.res['json']['log']]

    await fetch_log(cursor=t.res['json']['cursor'])
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    second_page_lsns = [l['lsn'] for l in t.res['json']['log']]

    tap.ok(first_page_lsns != second_page_lsns, 'разные страницы')
    tap.eq(
        first_page_lsns, sorted(first_page_lsns), 'сорчено на первой странице'
    )
    tap.eq(
        second_page_lsns, sorted(second_page_lsns), 'сорчено на второй странице'
    )
    tap.ok(
        not set(first_page_lsns).intersection(set(second_page_lsns)),
        'разные логи на разных страницах'
    )

async def test_log_with_none_vars(tap, dataset, api):
    with tap.plan(6, 'лог событий по заказу'):
        admin = await dataset.user(role='admin')
        tap.ok(admin.store_id, 'админ сгенерирован')
        t = await api(user=admin)

        order = await dataset.order(store_id=admin.store_id)
        tap.ok(order, 'заказ сгенерирован')
        await order.save(order_logs=[dict(vars=None)])
        tap.ok(order, 'Добавим лог с пустым vars')

        await t.post_ok('api_disp_orders_log',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
