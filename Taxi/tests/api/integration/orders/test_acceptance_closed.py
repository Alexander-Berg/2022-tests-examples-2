from datetime import timedelta
from libstall.util import tzone


async def test_acceptance_not_closed(
        tap, api, dataset, cfg, wait_order_status):
    with tap.plan(8, 'Полноценный флоу на свежий acceptance'):
        cfg.set('business.order.acceptance.stowage_limit', 0)

        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        user = await dataset.user(store=store)

        acceptance_order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
            ],
            status='reserving',
        )

        await wait_order_status(
            acceptance_order, ('complete', 'done'), user_done=user)

        for stowage_order_id in acceptance_order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            await stowage_order.ack(user=user)

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            await stowage_order.signal({'type': 'sale_stowage'})

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': acceptance_order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('is_acceptance_closed', False)


async def test_company_token(
        tap, api, dataset, cfg, wait_order_status):
    with tap.plan(8, 'Проверяем работоспособность токена компании'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        user = await dataset.user(store=store)

        acceptance_order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
            ],
            status='reserving',
        )

        await wait_order_status(
            acceptance_order, ('complete', 'done'), user_done=user)

        for stowage_order_id in acceptance_order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            await stowage_order.ack(user=user)

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            await stowage_order.signal({'type': 'sale_stowage'})

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(token=company.token)
        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': acceptance_order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('is_acceptance_closed', False)


async def test_order_problems(
        tap, api, dataset, uuid, now):
    with tap.plan(11, 'Ошибки, связанные с ордером'):
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': uuid()}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        order = await dataset.order()

        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': order.order_id}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.message', 'Wrong order type')

        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(store=store)

        product = await dataset.product(store_id=user.store_id)

        order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {'product_id': product.product_id},
            ],
            type='acceptance',
            status='complete',
            estatus='done',
            vars={'all_children_done': now()},
        )

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': order.order_id}
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.message', 'Acceptance has not stowages')


async def test_acceptance_closed(
        tap, api, dataset, cfg, now):
    with tap.plan(12, 'Приемка закрыта'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(store=store)

        product = await dataset.product(store_id=user.store_id)

        tz = tzone(store.tz)

        cfg.set(
            'business.order.acceptance.last_stowage_time_limit', '04:00')

        order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {'product_id': product.product_id},
            ],
            type='acceptance',
            status='complete',
            estatus='done',
            vars={'all_children_done': now()},
        )

        t = await api(token=company.token)

        stowage = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='sale_stowage',
            updated=now(tz=tz) - timedelta(hours=48),
            parent=[order.order_id],
        )

        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('is_acceptance_closed', True)

        stowage.updated = now()
        await stowage.save()
        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('is_acceptance_closed', False)

        order.vars['closed'] = now()
        await order.save()
        await t.post_ok(
            'api_integration_orders_acceptance_closed',
            json={'order_id': order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('is_acceptance_closed', True)
