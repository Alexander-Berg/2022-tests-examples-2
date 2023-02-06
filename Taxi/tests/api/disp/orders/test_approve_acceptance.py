from datetime import timedelta


async def test_wrong_type(tap, dataset, api):
    with tap.plan(4, 'не приемка на входе'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='store_admin')
        order = await dataset.order(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(400)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Order type is not acceptance')


async def test_all_children_done(tap, dataset, api):
    with tap.plan(4, 'не все основные раскладки готовы'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='store_admin')
        order = await dataset.order(store=store, type='acceptance')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Main stowages are not completed')


async def test_already_closed(tap, dataset, api, now, cfg, wait_order_status):
    with tap.plan(12, 'уже все закрыто'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='acceptance',
            acks=[user.user_id],
            approved=now(),
            required=[{'product_id': product.product_id, 'count': 69}]
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stowages = await order.get_descendants()
        tap.eq(len(stowages), 1, 'одна раскладка')
        stowages[0].acks = [user.user_id]
        await stowages[0].save()
        await wait_order_status(
            stowages[0], ('complete', 'done'), user_done=user,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )
        t.status_is(200)
        t.json_is('code', 'OK')
        await order.reload()
        tap.ok(order.vars['closed'], 'зааппрувлен')
        tap.eq(order.vars['closed_by'], user.user_id, 'нужным юзером')

        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Order is approved already')


async def test_time_expired(
    tap, dataset, api, now, cfg, wait_order_status,
):
    with tap.plan(12, 'время на аппрув истекло'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        product = await dataset.product()

        order = await dataset.order(
            store=store,
            type='acceptance',
            acks=[user.user_id],
            approved=now(),
            required=[{'product_id': product.product_id, 'count': 69}]
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stowages = await order.get_descendants()
        tap.eq(len(stowages), 1, 'одна раскладка')
        stowage = stowages[0]
        stowage.acks = [user.user_id]
        await stowage.save()
        await wait_order_status(stowage, ('complete', 'done'), user_done=user)
        tap.ok(
            await order.reload(),
            'Перезабрали приемку'
        )
        tap.ok(
            order.vars.get('all_children_done'),
            'Есть флаг завершения дочерних'
        )
        order.vars['all_children_done'] = str(now() - timedelta(days=3))
        tap.ok(await order.save(store_job_event=False), 'Сохранили новую дату')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is(
            'message',
            'Time limit expired, acceptance will be approved automatically',
        )
        await order.reload()
        tap.ok(order.vars['all_children_done'], 'дочерние раскладки сделаны')
        tap.ok(not order.vars.get('closed'), 'приемка не аппрувнута')


async def test_not_all_children_done(
    tap, dataset, api, now, cfg, wait_order_status,
):
    with tap.plan(7, 'не все дочерние готовы'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        product = await dataset.product()

        order = await dataset.order(
            store=store,
            type='acceptance',
            acks=[user.user_id],
            approved=now(),
            required=[{'product_id': product.product_id, 'count': 69}]
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stowages = await order.get_descendants()
        tap.eq(len(stowages), 1, 'одна раскладка')
        stowage = stowages[0]
        stowage.acks = [user.user_id]
        await stowage.save()
        await wait_order_status(
            stowage, ('complete', 'done'), user_done=user,
        )
        await dataset.order(store=store, parent=[order.order_id])

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Child orders are not completed')


async def test_happy_flow(
    tap, dataset, api, now, cfg, wait_order_status,
):
    with tap.plan(9, 'хеппи флоу'):
        cfg.set('business.order.acceptance.approval_time_limit', '16:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        product = await dataset.product()

        order = await dataset.order(
            store=store,
            type='acceptance',
            acks=[user.user_id],
            approved=now(),
            required=[{'product_id': product.product_id, 'count': 69}]
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stowages = await order.get_descendants()
        tap.eq(len(stowages), 1, 'одна раскладка')
        stowage = stowages[0]
        stowage.acks = [user.user_id]
        await stowage.save()
        await wait_order_status(
            stowage, ('complete', 'done'), user_done=user,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(200)
        t.json_is('code', 'OK')
        await order.reload()
        tap.ok(order.vars['all_children_done'], 'проставлено время')
        tap.eq(order.vars['closed_by'], user.user_id, 'аппрувнута мною')
        tap.ok(order.vars['closed'], 'закрылось')
