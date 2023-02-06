from datetime import datetime, timedelta

import pytest

from libstall.util import tzone
from stall.model.order_business.job_stowage_on_diff import (
    job_stowage_on_diff
)


async def test_stowage_on_diff(
        tap, dataset, api, wait_order_status, cfg, job, push_events_cache):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(23, 'Генерация раскладок разницы'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )

        products = [await dataset.product() for _ in range(3)]

        user = await dataset.user(store=store)

        order = await dataset.order(
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

        right_answer = {}

        for number, product in enumerate(products[1::], start=1):
            right_answer[product.product_id] = number*2

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user
        )

        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            tap.ok(await s.done(count=2), 'закрываем саджесты')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
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

        stock = await dataset.Stock.list_by_product(
            product_id=products[0].product_id,
            shelf_type='store',
            store_id=store.store_id,
        )

        check_order = await dataset.order(
            type='check_product_on_shelf',
            products=[products[0].product_id],
            shelves=[stock[0].shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            parent=[order.order_id],
        )

        await wait_order_status(check_order, ('request', 'waiting'))
        await check_order.ack(user)

        await wait_order_status(check_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(check_order)

        with suggests[0] as s:
            tap.ok(
                await s.done(count=13, valid='02-03-2022'),
                'Закрыли suggest пересчета по распоряжению'
            )

        await check_order.done('complete', user=user)

        await wait_order_status(check_order, ('complete', 'done'))

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновление ассортимента
        await job.call(await job.take())

        name_job_stash = f'orders_stowage_on_diff-{order.order_id}'
        stash = await dataset.Stash.load(name_job_stash, by='name')
        await push_events_cache(stash, job_method='job_stowage_on_diff')

        # Создаем размещение на разницу
        await job.call(await job.take())

        await order.reload()

        tap.eq(
            len(order.vars['stowage_id']), 2, 'Правильное количество stowage')

        for stowage_id in order.vars['stowage_id']:
            stowage = await dataset.Order.load(stowage_id)
            if stowage.fstatus == ('complete', 'done'):
                continue
            tap.eq(
                stowage.attr['doc_number'],
                order.attr['doc_number'] + '-D1',
                'Корректный номер'
            )
            tap.ok(
                stowage.attr['diff_stowage'],
                'Атрибут размещения на разницу'
            )
            for row in stowage.required:
                tap.eq(
                    row.count,
                    right_answer[row.product_id],
                    'Правильное количество'
                )

            await wait_order_status(stowage, ('request', 'waiting'))

            await stowage.ack(user=user)

            await wait_order_status(stowage, ('processing', 'waiting'))

            await stowage.signal({'type': 'sale_stowage'})

            await wait_order_status(
                stowage,
                ('complete', 'done'),
                user_done=user
            )


async def test_no_exp(
        tap, dataset, api, wait_order_status, cfg):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(4, 'У склада отсутствует эксперимент'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
        )

        product = await dataset.product()

        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': product.product_id,
                  'count': 2
                },
            ],
            status='reserving',
        )

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_STORE_EXP_OFF')


async def test_no_more_stowages(
        tap, dataset, api, wait_order_status, cfg, job, push_events_cache):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(8, 'Раскладок больше не требуется'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )

        products = [await dataset.product() for _ in range(3)]

        user = await dataset.user(store=store)

        order = await dataset.order(
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

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
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

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновление ассортимента
        await job.call(await job.take())

        name_job_stash = f'orders_stowage_on_diff-{order.order_id}'
        stash = await dataset.Stash.load(name_job_stash, by='name')
        await push_events_cache(stash, job_method='job_stowage_on_diff')

        # Создаем размещение на разницу
        await job.call(await job.take())

        children = await order.get_descendants(order_types=['sale_stowage'])
        diff_stowage = [
            child for child in children if child.attr.get('diff_stowage')]

        tap.eq(
            len(diff_stowage), 0,
            'Количество stowages не поменялось'
        )


async def test_incorrect_order(tap, dataset, api, uuid, wait_order_status):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(7, 'Некорректный ордер'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )

        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': uuid()
            }
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        product = await dataset.product(store_id=user.store_id)

        order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {'product_id': product.product_id},
            ],
            type='acceptance',
            status='complete',
            estatus='check_children',
        )

        await wait_order_status(order, ('complete', 'done'))

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )
        t.status_is(400, diag=True)
        t.json_is('details.message', 'Acceptance has not stowages')


async def test_incorrect_data(
        tap, dataset, api, wait_order_status, cfg):
    with tap.plan(16, 'Неверные данные при запросе'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )

        product = await dataset.product()

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        await dataset.assortment_contractor_product(
            assortment=assortment,
            product=product,
            status='active',
            price=69
        )

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 2
                },
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_DESCENDANTS_IS_NOT_DONE')

        stowage_order = await dataset.Order.load(order.vars['stowage_id'][0])

        await wait_order_status(stowage_order, ('request', 'waiting'))

        await stowage_order.ack(user=user)

        await wait_order_status(stowage_order, ('processing', 'waiting'))

        await stowage_order.signal({'type': 'sale_stowage'})

        await wait_order_status(
            stowage_order,
            ('complete', 'done'),
            user_done=user
        )

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


@pytest.mark.skip
async def test_acceptance_closed(
        tap, api, dataset, cfg, now):
    with tap.plan(3, 'Приемка закрыта'):
        company = await dataset.company()
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )
        user = await dataset.user(store=store)

        product = await dataset.product(store_id=user.store_id)

        tz = tzone(store.tz)

        time_limit = f'{now(tz=tz).hour}:00'

        cfg.set(
            'business.order.acceptance.last_stowage_time_limit', time_limit)

        order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {'product_id': product.product_id},
            ],
            type='acceptance',
            status='complete',
            estatus='done'
        )

        await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='sale_stowage',
            updated=str(now(tz=tz) - timedelta(hours=49)),
            parent=[order.order_id],
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(400, diag=True)
        t.json_is('message', 'Stowage is completed too long ago')


async def test_stowage_exist(
        tap, dataset, api, wait_order_status, cfg, job, push_events_cache):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(12, 'Ордер на раскладку сущетсвует'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_michael_burry': True}
        )

        products = [await dataset.product() for _ in range(3)]

        user = await dataset.user(store=store)

        order = await dataset.order(
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
            order,
            ('processing', 'waiting'),
            user_done=user
        )

        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            tap.ok(await s.done(count=2), 'закрываем саджесты')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
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

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        name_job_stash = f'orders_stowage_on_diff-{order.order_id}'

        stowage_stash = await dataset.Stash.load(name_job_stash, by='name')

        # Обновление ассортимента
        await job.call(await job.take())

        name_job_stash = f'orders_stowage_on_diff-{order.order_id}'
        stash = await dataset.Stash.load(name_job_stash, by='name')
        await push_events_cache(stash, job_method='job_stowage_on_diff')

        # Создаем размещение на разницу
        await job.call(await job.take())

        await order.reload()

        children = await order.get_descendants(order_types=['sale_stowage'])
        sale_stowage = [
            child for child in children if not child.attr.get('diff_stowage')
        ][0]

        order.vars['stowage_id'] = [sale_stowage.order_id]

        await order.save(store_job_event=False)

        await stowage_stash.save()

        await job.put(
            job_stowage_on_diff,
            stash_id=stowage_stash.stash_id
        )

        await job.call(await job.take())

        await order.reload()

        tap.eq(
            len(order.vars['stowage_id']), 2, 'Правильное количество stowage')


async def test_child_products(
        tap, dataset, api, wait_order_status, cfg, job, push_events_cache):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(30, 'Проверка дочерних продуктов'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={
                'exp_schrodinger': False,
                'exp_michael_burry': True,
            }
        )

        products = [await dataset.product() for _ in range(3)]

        children = [
            await dataset.product(parent_id=products[2].product_id)
            for _ in range(3)
        ]

        user = await dataset.user(store=store)

        order = await dataset.order(
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

        right_answer = {
            products[1].product_id: 2,
            products[2].product_id: 1
        }

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user
        )

        suggests = await dataset.Suggest.list_by_order(order)
        for s in suggests:
            if s.count != 6:
                tap.ok(await s.done(count=2), 'закрываем саджесты')
                continue
            tap.ok(await s.done(count=6), 'закрываем саджесты')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stowage_order = await dataset.Order.load(
            order.vars['stowage_id'])

        await wait_order_status(stowage_order, ('request', 'waiting'))

        await stowage_order.ack(user=user)

        for product in children[:-1]:
            await wait_order_status(stowage_order, ('processing', 'waiting'))
            await stowage_order.signal(
                {
                    'type': 'more_product',
                    'data': {
                        'product_id': product.product_id,
                        'count': 2,
                    }
                }
            )

        await wait_order_status(stowage_order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(stowage_order)
        for s in suggests:
            kw = {'count': s.count % 6}
            if s.conditions['need_valid']:
                kw['valid'] = '2012-01-02'
            tap.ok(
                await s.done(**kw),
                f'закрываем саджест {s.count}'
            )

        await stowage_order.signal({'type': 'sale_stowage'})

        await wait_order_status(
            stowage_order,
            ('complete', 'done'),
            user_done=user
        )

        shelf = await dataset.shelf(store=store)

        check_order = await dataset.order(
            type='check_product_on_shelf',
            products=[children[2].product_id],
            shelves=[shelf.shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            parent=[order.order_id],
        )

        await wait_order_status(check_order, ('request', 'waiting'))
        await check_order.ack(user)

        await wait_order_status(check_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(check_order)

        with suggests[0] as s:
            tap.ok(
                await s.done(count=1, valid='02-03-2022'),
                'Закрыли suggest пересчета по распоряжению'
            )

        await check_order.done('complete', user=user)

        await wait_order_status(check_order, ('complete', 'done'))

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновление ассортимента
        await job.call(await job.take())

        name_job_stash = f'orders_stowage_on_diff-{order.order_id}'
        stash = await dataset.Stash.load(name_job_stash, by='name')
        await push_events_cache(stash, job_method='job_stowage_on_diff')

        # Создаем размещение на разницу
        await job.call(await job.take())

        await order.reload()

        tap.eq(
            len(order.vars['stowage_id']), 2, 'Правильное количество stowage')

        for stowage_id in order.vars['stowage_id']:
            stowage = await dataset.Order.load(stowage_id)
            if stowage.fstatus == ('complete', 'done'):
                continue
            tap.eq(
                stowage.attr['doc_number'],
                order.attr['doc_number'] + '-D1',
                'Корректный номер'
            )
            tap.ok(
                stowage.attr['diff_stowage'],
                'Атрибут размещения на разницу'
            )
            for row in stowage.required:
                tap.eq(
                    row.count,
                    right_answer[row.product_id],
                    'Правильное количество'
                )

            await wait_order_status(stowage, ('request', 'waiting'))

            await stowage.ack(user=user)

            await wait_order_status(stowage, ('processing', 'waiting'))

            await stowage.signal({'type': 'sale_stowage'})

            await wait_order_status(
                stowage,
                ('complete', 'done'),
                user_done=user
            )


async def test_acceptance_closed_vars(
    tap, dataset, time_mock, api, now, cfg, wait_order_status,
):
    with tap.plan(11, 'приемка закрыта через ручку'):
        cfg.set('business.order.acceptance.approval_time_limit', '16:20')
        store = await dataset.full_store(
            options={'exp_freegan_party': True, 'exp_michael_burry': True},
        )
        user = await dataset.user(store=store)
        product = await dataset.product()

        time_mock.set(datetime(2420, 4, 20, 1, 20, 0))

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

        time_mock.sleep(days=1, hours=11, minutes=59, seconds=59)

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_approve_acceptance',
            json={'order_id': order.order_id},
        )

        t.status_is(200)
        t.json_is('code', 'OK')
        await order.reload()
        tap.ok(order.vars['closed'], 'приемка закрыта')

        await t.post_ok(
            'api_disp_orders_stowage_on_diff',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(410)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Acceptance is closed')
