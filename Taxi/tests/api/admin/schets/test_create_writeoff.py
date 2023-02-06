# pylint: disable=protected-access,too-many-statements, too-many-locals

import pytest

from scripts.cron import schets_processing


@pytest.mark.parametrize(
    'store_status, should_create_order',
    [
        ('active', True),
        ('closed', False),
        ('disabled', True)
    ]
)
async def test_common(tap, dataset, api, uuid, job, push_events_cache,
                      store_status, should_create_order):
    if should_create_order:
        plan_cnt = 31
    else:
        plan_cnt = 26

    with tap.plan(plan_cnt, 'полный цикл с создания до выполнения'):
        store = await dataset.store(status=store_status)
        user = await dataset.user(store=store)
        user2 = await dataset.user(store=store)

        t1 = await api(user=user)
        t2 = await api(user=user2)

        await t1.post_ok(
            'api_admin_schets_save',
            json={
                'external_id': uuid(),
                'store_id': store.store_id,
                'handler': 'create_writeoff',
                'schedule': {
                    'interval': {'days': 1}
                },
                'kwargs': {
                    'order_type': 'writeoff',
                }
            }
        )
        t1.status_is(200, diag=True)
        t1.json_is('code', 'OK')
        t1.json_has('schet')
        t1.json_has('schet.schet_task_id')

        schet_task_id = t1.res['json']['schet']['schet_task_id']

        await t2.post_ok(
            'api_admin_schets_approve',
            json={
                'schet_task_id': schet_task_id,
            }
        )
        t2.status_is(200, diag=True)
        t2.json_is('code', 'OK')
        t2.json_has('schet')
        t2.json_is('schet.schet_task_id', schet_task_id)
        t2.json_is('schet.approved_by', user2.user_id)

        await t1.post_ok(
            'api_admin_schets_start',
            json={
                'schet_task_id': schet_task_id,
            }
        )
        t1.status_is(200, diag=True)
        t1.json_is('code', 'OK')
        t1.json_has('schet')
        t1.json_is('schet.schet_task_id', schet_task_id)
        t1.json_is('schet.status', 'pending')

        order = (await dataset.Order.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )).list
        tap.isa_ok(order, list, 'order is list')
        tap.ok(not order, 'order is empty')

        schet = await dataset.SchetTask.load(schet_task_id)
        tap.ok(schet, 'schet loaded')
        tap.eq(schet.status, 'pending', 'schet pending')

        await schets_processing._process_tasks([schet])

        await schet.reload()
        tap.eq(schet.status, 'delayed', 'schet delayed')

        await push_events_cache(schet, 'run')
        task = await job.take()
        tap.ok(task, 'task taken')
        await job.call(task)
        await job.ack(task)

        task = await job.take()
        tap.ok(not task, 'queue empty')

        await schet.reload()
        tap.eq(schet.status, 'pending', 'schet proceeded')

        order = (await dataset.Order.list(
            by='full',
            conditions=('store_id', store.store_id),
            sort=(),
        )).list
        if should_create_order:
            tap.isa_ok(order, list, 'order is list')
            tap.ok(order, 'order is not empty')

            with order[0] as o:
                tap.ok(o.order_id, 'order created')
                tap.eq(o.store_id, store.store_id, 'store_id saved')
                tap.eq(o.company_id, store.company_id, 'company_id saved')
                tap.eq(o.type, 'writeoff', 'type saved')
        else:
            tap.eq_ok(order, [], 'order is empty')
