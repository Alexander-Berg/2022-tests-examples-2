import argparse
import pytest

from aiohttp import web

from scripts.dev.update_assortment_contractor import main
from stall.client.onec import client as onec_client
from stall.client.woody import woodyclient_dict
from stall.model.assortment_contractor import AssortmentContractor
from stall.model.assortment_contractor_product import (
    AssortmentContractorProduct
)


# pylint: disable=too-many-locals
@pytest.mark.parametrize('region', ['ru', 'fr'])
async def test_update_assortment_store(
        tap, dataset, uuid, ext_api, cfg, region
):
    with tap.plan(9, 'пробуем запустить скрипт с store_id'):
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 'password')

        company = await dataset.company(instance_erp=region)
        store = await dataset.store(
            company=company,
            options={'exp_schrodinger': False},
        )
        product = await dataset.product()

        orders = []
        for status in ['reserving', 'request', 'processing']:
            order_params = {
                'store': store,
                'type': 'acceptance',
                'status': status,
                'estatus': 'begin',
                'required': [
                    {'product_id': product.product_id, 'count': 3}
                ],
                'attr': {'contractor_id': uuid()},
            }
            orders.append(await dataset.order(**order_params))

        async def handler(req):
            rj = await req.json()

            if not rj.get('cursor'):
                return web.json_response(
                    status=200,
                    data={
                        'products': [
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

        args = argparse.Namespace(
            order='',
            company='',
            store=store.store_id,
            verbose=False,
            apply=True,
        )
        async with await ext_api(
                woodyclient_dict.get(region, onec_client), handler
        ):
            await main(args)

        for order in orders:
            assortment = await AssortmentContractor.load(
                (order.attr['contractor_id'], store.store_id),
                by='contractor_store',
            )
            if order.status == 'reserving':
                tap.ok(not assortment, 'нет ассортимента')
                continue
            tap.ok(assortment, 'ассортимент появился')
            tap.eq(assortment.cursor, '111', 'курсор 111')

            acp = await AssortmentContractorProduct.load(
                (assortment.assortment_id, product.product_id),
                by='assortment_product',
            )
            tap.eq(acp.status, 'active', 'статус active')
            tap.eq(str(acp.price), str(1.11), 'цена 1.11')
