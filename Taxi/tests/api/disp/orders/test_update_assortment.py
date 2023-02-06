from aiohttp import web

from stall.client.onec import client as onec_client
from stall.client.woody import woodyclient_dict


async def test_success(tap, dataset, api, job, uuid, cfg, ext_api):
    # pylint: disable=too-many-locals
    with tap.plan(4, 'Успешный запуск обновления ассортимента'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_schrodinger': False}
        )
        contractor_id = uuid()
        user = await dataset.user(store=store)
        t = await api(user=user)
        product = await dataset.product()
        order = await dataset.order(
            store_id=user.store_id,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1
                }
            ],
            attr={'contractor_id': contractor_id},
            status='complete',
            estatus='done'
        )

        async def woody_handler(req):
            if not (await req.json()).get('cursor'):
                return web.json_response(
                    status=200,
                    data={
                        'products': [
                            {
                                'product_id': product.product_id,
                                'active': True,
                                'price': 0.5,
                            }
                        ],
                        'cursor': '111',
                    }
                )
            return web.json_response(status=200, data={})

        async with await ext_api(
            woodyclient_dict.get('ru', onec_client),
            woody_handler
        ):
            await t.post_ok(
                'api_disp_orders_update_assortment',
                json={
                    'order_id': order.order_id,
                    'job_tube': job.name,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            await job.call(await job.take())

            assortment = await dataset.AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.ok(assortment, 'ассортимент появился')


async def test_check_order(tap, dataset, api, job, uuid):
    with tap.plan(5, 'Обновление ассортимента от дочернего'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': False}
        )
        contractor_id = uuid()
        user = await dataset.user(store=store)
        t = await api(user=user)
        product = await dataset.product()
        acc_order = await dataset.order(
            store_id=user.store_id,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1
                }
            ],
            attr={'contractor_id': contractor_id},
            status='complete',
            estatus='done'
        )
        check_order = await dataset.order(
            store_id=user.store_id,
            acks=[user.user_id],
            type='check_product_on_shelf',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1
                }
            ],
            parent=[acc_order.order_id],
            status='reserving',
        )

        await t.post_ok(
            'api_disp_orders_update_assortment',
            json={
                'order_id': check_order.order_id,
                'job_tube': job.name,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        task = await job.take()
        tap.eq(
            task.callback,
            'stall.model.assortment_contractor.'
            'job_update_assortment_contractor',
            'Правильный колбэк '
        )
        tap.eq(
            task.data.get('order_id'),
            acc_order.order_id,
            'Правильный ордер'
        )


async def test_another_store(tap, dataset, api, job, uuid):
    with tap.plan(3, 'Другой склад'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': False}
        )
        another_store = await dataset.store()
        contractor_id = uuid()
        user = await dataset.user(store=store)
        t = await api(user=user)
        product = await dataset.product()
        acc_order = await dataset.order(
            store_id=another_store.store_id,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1
                }
            ],
            attr={'contractor_id': contractor_id},
            status='complete',
            estatus='done'
        )

        await t.post_ok(
            'api_disp_orders_update_assortment',
            json={
                'order_id': acc_order.order_id,
                'job_tube': job.name,
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_wrong_order(tap, dataset, api, job):
    with tap.plan(3, 'Неправильный тип документа'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': False}
        )
        user = await dataset.user(store=store)
        t = await api(user=user)
        product = await dataset.product()
        acc_order = await dataset.order(
            store_id=store.store_id,
            acks=[user.user_id],
            type='check_product_on_shelf',
            required=[{'product_id': product.product_id}],
            status='complete',
            estatus='done'
        )

        await t.post_ok(
            'api_disp_orders_update_assortment',
            json={
                'order_id': acc_order.order_id,
                'job_tube': job.name,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
