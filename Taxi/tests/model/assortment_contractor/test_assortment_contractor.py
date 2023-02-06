import argparse
import pytest

from aiohttp import web

from scripts.dev.update_assortment_contractor import main
from stall.client.onec import client as onec_client
from stall.client.woody import woodyclient_dict
from stall.model.assortment_contractor import (
    AssortmentContractor, job_update_assortment_contractor,
)
from stall.model.assortment_contractor_product import (
    AssortmentContractorProduct
)
from stall.job import ErrorJobRetryDelay


async def test_assortment_contractor(tap, dataset, uuid):
    with tap.plan(4):

        store = await dataset.store()

        assortment = AssortmentContractor({
            'contractor_id': uuid(),
            'store_id': store.store_id,
        })

        tap.ok(assortment, 'Инстанцирован')
        tap.ok(not assortment.assortment_id, 'идентификатора пока нет')
        tap.ok(await assortment.save(), 'Сохранён в БД')
        tap.ok(assortment.assortment_id, 'идентификатор')


async def test_dataset(tap, dataset):
    with tap.plan(5):
        assortment = await dataset.assortment_contractor()
        tap.ok(assortment, 'ассортимент создан')
        tap.ok(assortment.assortment_id, 'есть айди')
        tap.ok(assortment.store_id, 'есть склад')
        tap.ok(not assortment.instance_erp, 'источник пуст')
        tap.eq_ok(assortment.vars, {}, 'vars == {}')


async def test_first_not_empty(tap, dataset, uuid, ext_api):
    with tap.plan(4, 'присылаем сразу не пустой ассортимент'):
        contractor_id = uuid()
        company = await dataset.company(instance_erp='fr')
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': True},
        )
        product = await dataset.product()

        order_params = {
            'store': store,
            'type': 'acceptance',
            'status': 'reserving',
            'estatus': 'begin',
            'required': [
                {'product_id': product.product_id, 'count': 3}
            ],
            'attr': {'contractor_id': contractor_id},
        }
        order = await dataset.order(**order_params)

        async def woody_handler(req):
            rj = await req.json()

            if not rj.get('cursor'):
                return web.json_response(
                    status=200,
                    data={
                        'products': [
                            {
                                'product_id': product.product_id,
                                'active': True,
                                'price': 0.5,
                            },
                            {
                                'product_id': product.product_id,
                                'active': True,
                                'price': 1.11,
                            }
                        ],
                        'cursor': '111',
                    }
                )
            return web.json_response(status=200, data={})

        async with await ext_api(woodyclient_dict['fr'], woody_handler):
            await job_update_assortment_contractor(order.order_id)

            assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.ok(assortment, 'ассортимент появился')
            tap.eq(assortment.cursor, '111', 'курсор 111')

            acp = await AssortmentContractorProduct.load(
                (assortment.assortment_id, product.product_id),
                by='assortment_product',
            )
            tap.eq(acp.status, 'active', 'статус active')
            tap.eq(str(acp.price), str(1.11), 'цена 1.11')


# pylint: disable=too-many-statements
async def test_update_assortment(tap, dataset, uuid, ext_api):
    with tap.plan(31, 'проверяем обновление ассортимента'):
        contractor_id = uuid()
        company = await dataset.company(instance_erp='fr')
        store = await dataset.store(
            company=company, options={'exp_schrodinger': False}
        )
        products = [
            await dataset.product(external_id=uuid()) for _ in range(3)
        ]

        order_params = {
            'store': store,
            'source': 'woody',
            'type': 'acceptance',
            'status': 'reserving',
            'estatus': 'begin',
            'required': [
                {'product_id': p.product_id, 'count': 3} for p in products
            ],
        }
        order = await dataset.order(**order_params)

        async def woody_handler(req):
            rj = await req.json()
            tap.eq(
                rj.get('contractor_id'),
                contractor_id,
                'Правильный поставщик'
            )
            tap.eq(
                rj.get('store_id'),
                store.store_id,
                'Правильный склад'
            )

            cursor = rj['cursor'] if rj.get('cursor') else ''

            result = {
                '': {
                    'products': [],
                    'cursor': '111',
                },
                '111': {
                    'products': [
                        {'product_id': products[i].product_id, 'active': True}
                        for i in range(3)
                    ],
                    'cursor': '222',
                },
                '222': {
                    'products': [],
                    'cursor': '333',
                },
                '333': {
                    'products': [
                        {'product_id': products[i].product_id, 'active': False}
                        for i in range(2)
                    ],
                    'cursor': '444',
                },
                '444': {
                    'products': [],
                    'cursor': '555',
                },
                '555': {
                    'products': [
                        {'product_id': products[i].product_id, 'active': True}
                        for i in range(3)
                    ],
                    'cursor': '666',
                },
                '666': {
                    'products': [],
                    'cursor': '777',
                },
                '777': {
                    'products': [
                        {'product_id': 'fake_product_id', 'active': True}
                    ],
                    'cursor': '888',
                }
            }

            ans = web.json_response(status=500, data={})
            if result.get(cursor):
                ans = web.json_response(status=200, data=result[cursor])
            return ans

        async with await ext_api(woodyclient_dict['fr'], woody_handler):
            await job_update_assortment_contractor(order.order_id)

            assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.ok(not assortment, 'ассортимент не появился')

            order_params['attr'] = {'ignore_assortment': True}
            order = await dataset.order(**order_params)

            await job_update_assortment_contractor(order.order_id)

            assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.ok(not assortment, 'ассортимент не появился')

            order_params['attr'] = {'contractor_id': contractor_id}
            order = await dataset.order(**order_params)

            await job_update_assortment_contractor(order.order_id)

            assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )

            tap.ok(assortment, 'ассортимент появился')
            tap.eq(assortment.cursor, '111', 'курсор 111')

            await job_update_assortment_contractor(order.order_id)

            await assortment.reload()
            tap.eq(assortment.cursor, '333', 'курсор 333')

            acps = [
                await AssortmentContractorProduct.load(
                    (assortment.assortment_id, products[i].product_id),
                    by='assortment_product',
                )
                for i in range(3)
            ]

            tap.ok(all(acps), 'все ассортименты появились')
            tap.ok(
                all(acp.status == 'active' for acp in acps),
                'все статусы active',
            )

            await job_update_assortment_contractor(order.order_id)

            await assortment.reload()
            tap.eq(assortment.cursor, '555', 'курсор 555')

            for acp in acps:
                await acp.reload()
            tap.eq(acps[0].status, 'removed', 'статус стал removed')
            tap.eq(acps[1].status, 'removed', 'статус стал removed')
            tap.eq(acps[2].status, 'active', 'статус остался active')

            await job_update_assortment_contractor(order.order_id)

            for acp in acps:
                await acp.reload()
            tap.ok(
                all(acp.status == 'active' for acp in acps),
                'все статусы active',
            )
            tap.ok(
                all(acp.price is None for acp in acps),
                'все цены пусты'
            )
            await assortment.reload()
            tap.eq(assortment.cursor, '777', 'курсор 777')

            await job_update_assortment_contractor(order.order_id)

            await assortment.reload()
            tap.eq(assortment.cursor, '777', 'курсор 777')


# pylint: disable=too-many-locals
@pytest.mark.parametrize('region', ['ru', 'fr'])
async def test_error_get_assortment(
        tap, cfg, dataset, job, wait_order_status,
        ext_api, push_events_cache, region):
    with tap.plan(3, 'Ошибка при получении ассортимента'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')
        company = await dataset.company(instance_erp=region)

        store = await dataset.full_store(
            company=company,
            options={'exp_schrodinger': True}
        )

        user = await dataset.user(store=store)

        products = [await dataset.product() for _ in range(3)]

        assortment = await dataset.assortment_contractor(store=store)
        orders = []

        for _ in range(2):
            acceptance = await dataset.order(
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
                attr={'contractor_id': assortment.contractor_id},
                status='reserving'
            )
            await wait_order_status(
                acceptance, ('complete', 'done'), user_done=user)
            orders.append(acceptance)

        async def handler(req):
            rj = await req.json()

            if not rj.get('cursor'):
                return web.json_response(
                    status=429,
                    data={'code': 'OH_NO_MR_DUDOS'}
                )
            return web.json_response(
                status=429, data={'code': 'OH_NO_MR_DUDOS'}
            )

        args = argparse.Namespace(
            order='',
            company='',
            store=store.store_id,
            verbose=False,
            apply=True,
            force=True,
        )
        async with await ext_api(
                woodyclient_dict.get(region, onec_client), handler
        ):
            await main(args)

        for number in range(2):
            await push_events_cache(
                orders[number],
                job_method='job_update_assortment_contractor'
            )

        try:
            await job.call(await job.take())
        except Exception as e:
            tap.ok(isinstance(e, ErrorJobRetryDelay), 'Верный тип ошибки')


async def test_no_uuid_contractor_id(
        tap, cfg, dataset, job, wait_order_status, ext_api):
    with tap.plan(2, 'Contractor_id не uuid'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')
        company = await dataset.company(instance_erp='ru')

        store = await dataset.full_store(
            company=company,
            options={'exp_schrodinger': True}
        )

        user = await dataset.user(store=store)

        product = await dataset.product()

        assortment = await dataset.assortment_contractor(
            store=store,
            contractor_id='88005553535'
        )

        acceptance = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 2
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving'
        )
        await wait_order_status(
            acceptance, ('complete', 'done'), user_done=user)

        async def handler(req):
            rj = await req.json()

            if not rj.get('cursor'):
                return web.json_response(
                    status=200,
                    data={'code': 'OK'}
                )
            return web.json_response(
                status=200, data={'code': 'OK'}
            )

        args = argparse.Namespace(
            order='',
            company='',
            store=store.store_id,
            verbose=False,
            apply=True,
            force=True,
        )
        async with await ext_api(
                woodyclient_dict.get('ru', onec_client), handler
        ):
            await main(args)

        tap.ok(await job.call(await job.take()), 'Задание выполнено')


async def test_no_order(tap, dataset, uuid, ext_api):
    with tap.plan(11, 'Обновление ассортимента без ордера'):
        contractor_id = uuid()
        company = await dataset.company(instance_erp='fr')
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': True},
        )
        product = await dataset.product()

        async def woody_handler(req):
            rj = await req.json()
            tap.eq(
                rj.get('contractor_id'),
                contractor_id,
                'Правильный поставщик'
            )
            tap.eq(
                rj.get('store_id'),
                store.store_id,
                'Правильный склад'
            )

            if not rj.get('cursor'):
                return web.json_response(
                    status=200,
                    data={
                        'products': [
                            {
                                'product_id': product.product_id,
                                'active': True,
                                'price': 0.5,
                            },
                            {
                                'product_id': product.product_id,
                                'active': True,
                                'price': 1.11,
                            }
                        ],
                        'cursor': '111',
                    }
                )
            return web.json_response(status=200, data={})

        async with await ext_api(woodyclient_dict['fr'], woody_handler):
            await job_update_assortment_contractor(
                store_id=store.store_id,
                contractor_id=contractor_id
            )

            assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.ok(assortment, 'ассортимент появился')
            tap.eq(assortment.cursor, '111', 'курсор 111')

            acp = await AssortmentContractorProduct.load(
                (assortment.assortment_id, product.product_id),
                by='assortment_product',
            )
            tap.eq(acp.status, 'active', 'статус active')
            tap.eq(str(acp.price), str(1.11), 'цена 1.11')

            await job_update_assortment_contractor(
                store_id=store.store_id,
                contractor_id=contractor_id
            )
            new_assortment = await AssortmentContractor.load(
                (contractor_id, store.store_id),
                by='contractor_store',
            )
            tap.eq(
                new_assortment.cursor,
                assortment.cursor,
                'Не поменялся курсор ассортимента'
            )
