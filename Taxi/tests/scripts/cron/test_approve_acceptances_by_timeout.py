from argparse import Namespace
from datetime import timedelta

from scripts.cron.approve_acceptances_by_timeout import (
    main, OLD_ORDER_DAYS_CNT,
)


async def test_not_approved_by_timeout(tap, dataset, cfg, now):
    # pylint: disable=too-many-locals
    with tap.plan(7, 'проверяем всевозможные отсекающие ифы'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={'exp_agutin': True})

        not_acceptance = await dataset.order(store=store)
        not_complete = await dataset.order(store=store, type='acceptance')
        done = {
            'store': store,
            'type': 'acceptance',
            'status': 'complete',
            'estatus': 'done',
        }
        children_not_done = await dataset.order(**done)
        broken = await dataset.order(**done, vars={'all_children_done': now()})
        closed = await dataset.order(
            **done,
            vars={
                'all_children_done': now(),
                'closed': now(),
            },
        )
        with_opened_child = await dataset.order(
            **done,
            vars={
                'all_children_done': now(),
            },
        )
        await dataset.order(  # собсно сам opened_child
            type='sale_stowage',
            parent=[with_opened_child.order_id],
        )
        not_expired = await dataset.order(
            **done,
            vars={
                'all_children_done': now(),
            },
        )

        args = Namespace(
            store_ids=[store.store_id],
            apply=True,
        )
        await main(args)

        for order in [
            not_acceptance,
            not_complete,
            children_not_done,
            broken,
            closed,
            with_opened_child,
            not_expired,
        ]:
            old_lsn = order.lsn
            await order.reload()
            tap.eq(order.lsn, old_lsn, 'ордер не изменился')


async def test_approved_by_timeout(tap, dataset, cfg, wait_order_status, now):
    with tap.plan(8, 'тестим аппрув по таймауту'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(
            options={'exp_freegan_party': True, 'exp_agutin': True},
        )
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
        await order.reload()

        args = Namespace(
            store_ids=[store.store_id],
            apply=True,
        )

        await main(args)
        old_lsn = order.lsn
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')
        order.vars['all_children_done'] = str(now() - timedelta(days=3))
        tap.ok(
            await order.save(),
            'Подвинули время'
        )
        old_lsn = order.lsn

        args.apply = False
        await main(args)
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')

        args.apply = True
        await main(args)
        await order.reload()
        tap.ok(order.vars['closed'], 'приемка закрыта')
        tap.eq(order.vars['closed_by'], None, 'закрыта автоматически')


async def test_too_old_acceptance(tap, dataset, cfg, wait_order_status, now):
    with tap.plan(4, 'игнорим оч старый ордер'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(
            options={'exp_freegan_party': True, 'exp_agutin': True},
        )
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
        await order.reload()
        order.vars['all_children_done'] = str(
            now() - timedelta(days=OLD_ORDER_DAYS_CNT * 2 + 1)
        )

        args = Namespace(
            store_ids=[store.store_id],
            apply=True,
        )

        await main(args)
        old_lsn = order.lsn
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')


async def test_has_children(tap, dataset, cfg, wait_order_status, now):
    with tap.plan(7, 'Не апрувим с дочерними'):
        cfg.set('business.order.acceptance.approval_time_limit', '04:20')
        store = await dataset.full_store(options={
            'exp_freegan_party': True,
            'exp_agutin': True,
        })
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
        await order.reload()
        await dataset.order(
            type='check_product_on_shelf',
            parent=[order.order_id],
        )

        args = Namespace(
            store_ids=[store.store_id],
            apply=True,
        )

        await main(args)
        old_lsn = order.lsn
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')
        order.vars['all_children_done'] = str(now() - timedelta(days=3))
        tap.ok(await order.save(), 'Подвинули время')
        old_lsn = order.lsn

        args.apply = False
        await main(args)
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')

        args.apply = True
        await main(args)
        await order.reload()
        tap.eq(order.lsn, old_lsn, 'ордер не тронут')
