from datetime import timedelta


async def test_wrong_type(tap, dataset, api):
    with tap.plan(4, 'не приемка на входе'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='employee_audit')
        order = await dataset.order(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_reopen_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(400)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Order type is not acceptance')


async def test_not_closed(tap, dataset, api):
    with tap.plan(4, 'приемка не закрыта'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='employee_audit')
        order = await dataset.order(store=store, type='acceptance')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_reopen_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Acceptance is not closed')


async def test_time_expired(
    tap, dataset, api, now, cfg, wait_order_status,
):
    with tap.plan(15, 'время истекло, переоткрыть нельзя'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store, role='admin')
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
        tap.ok(
            await order.reload(),
            'Перезабрали приемку'
        )
        tap.ok(
            order.vars.get('all_children_done'),
            'Есть флаг завершения дочерних'
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(200)
        t.json_is('code', 'OK')
        await order.reload()
        tap.ok(order.vars['all_children_done'], 'дочерние раскладки сделаны')
        tap.ok(order.vars.get('closed'), 'приемка аппрувнута')

        order.vars['all_children_done'] = str(now() - timedelta(days=3))
        tap.ok(await order.save(store_job_event=False), 'Сохранили новую дату')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_reopen_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is(
            'message',
            'Time limit expired, acceptance cant be reopened',
        )


async def test_happy_flow(
    tap, dataset, api, now, cfg, wait_order_status,
):
    # pylint: disable=too-many-locals
    with tap.plan(38, 'хеппи флоу'):
        cfg.set('business.order.acceptance.approval_time_limit', '16:20')
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store, role='admin')
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

        async def cl():
            await t.post_ok(
                'api_disp_orders_approve_acceptance',
                json={'order_id': order.order_id},
            )
            t.status_is(200)
            t.json_is('code', 'OK')
            await order.reload()
            tap.eq(
                order.vars('closed_by', None),
                user.user_id,
                'Тот пользователь'
            )
            tap.ok(
                order.vars.get('closed'),
                'Закрытие проставлено'
            )

        async def op():
            await t.post_ok(
                'api_disp_orders_reopen_acceptance',
                json={'order_id': order.order_id},
            )
            t.status_is(200)
            t.json_is('code', 'OK')
            await order.reload()

            tap.ok(
                'closed' not in order.vars,
                'Флаг закрытия удален'
            )
            tap.ok(
                'all_children_done',
                'Флаг закрытия остался'
            )

        await cl()
        await op()
        await cl()
        await op()
        await cl()

        await order.reload()
        order.vars['all_children_done'] = str(now() - timedelta(days=4))
        tap.ok(
            await order.save(store_job_event=False),
            'Сохранили дату'
        )

        await t.post_ok(
            'api_disp_orders_reopen_acceptance',
            json={'order_id': order.order_id},
        )
        t.status_is(409)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is(
            'message',
            'Time limit expired, acceptance cant be reopened',
        )

        await order.reload()
        tap.eq(
            len(order.vars('previous_approves', [])),
            2,
            'В истории две записи'
        )
        for record in order.vars('previous_approves', []):
            tap.eq(
                record.get('closed_by'),
                user.user_id,
                'Закрыт тем пользователем'
            )
            tap.eq(
                record.get('reopened_by'),
                user.user_id,
                'Открыт правильным пользователем'
            )
