import argparse

from aiohttp import web

from scripts.dev.remove_external_couriers import main
from stall.client.grocery_tags import (
    GroceryTagsUploadItem, GroceryTagsUploadTag, client as client_gt,
)
from stall.model.courier import Courier


async def test_simple(tap, dataset, ext_api):
    async def handler_gt(_):
        return web.json_response({
            'status': 'ok',
        })

    with tap.plan(2, 'Удаление внешних курьеров'):
        async with await ext_api(client_gt, handler_gt) as client:
            await client.upload(
                provider_id='wms-couriers',
                remove=[
                    GroceryTagsUploadItem({
                        'entity_type': 'item_id',
                        'tags': [GroceryTagsUploadTag({
                            'entity': '12345',
                            'name': 'grocery_male_under18_rus',
                        })],
                    })
                ],
            )

            courier_ok = await dataset.courier(
                order_provider='lavka',
            )
            courier_bad = await dataset.courier(
                order_provider='eda',
            )

            await main(
                args=argparse.Namespace(
                    apply=True,
                    count=None,
                ),
                counter={
                    'processed': 0,
                    'no_provider': 0,
                    'skipped': 0,
                    'errors_tags': 0,
                    'errors_save': 0,
                    'success': 0,
                },
            )

            courier_ok = await Courier.load(courier_ok.courier_id)
            tap.ok(courier_ok, 'Курьер остался')

            courier_bad = await Courier.load(courier_bad.courier_id)
            tap.eq(courier_bad, None, 'Курьер удалён')


async def test_with_shifts(tap, dataset, ext_api):
    async def handler_gt(_):
        return web.json_response({
            'status': 'ok',
        })

    with tap.plan(1, 'Курьеры, у которых были заказы'):
        async with await ext_api(client_gt, handler_gt) as client:
            await client.upload(
                provider_id='wms-couriers',
                remove=[
                    GroceryTagsUploadItem({
                        'entity_type': 'item_id',
                        'tags': [GroceryTagsUploadTag({
                            'entity': '12345',
                            'name': 'grocery_male_under18_rus',
                        })],
                    })
                ],
            )

            courier_bad = await dataset.courier(
                order_provider='eda',
            )
            await dataset.courier_shift(
                courier=courier_bad,
            )

            await main(
                args=argparse.Namespace(
                    apply=True,
                    count=None,
                ),
                counter={
                    'processed': 0,
                    'no_provider': 0,
                    'skipped': 0,
                    'errors_tags': 0,
                    'errors_save': 0,
                    'success': 0,
                },
            )

            courier_bad = await Courier.load(courier_bad.courier_id)
            tap.ok(courier_bad, 'Курьер остался')


async def test_with_orders(tap, dataset, ext_api):
    async def handler_gt(_):
        return web.json_response({
            'status': 'ok',
        })

    with tap.plan(1, 'Курьеры, у которых были заказы'):
        async with await ext_api(client_gt, handler_gt) as client:
            await client.upload(
                provider_id='wms-couriers',
                remove=[
                    GroceryTagsUploadItem({
                        'entity_type': 'item_id',
                        'tags': [GroceryTagsUploadTag({
                            'entity': '12345',
                            'name': 'grocery_male_under18_rus',
                        })],
                    })
                ],
            )

            courier_bad = await dataset.courier(
                order_provider='eda',
            )
            await dataset.order(
                courier_id=courier_bad.courier_id,
                status='processing',
                estatus='waiting',
            )

            await main(
                args=argparse.Namespace(
                    apply=True,
                    count=None,
                ),
                counter={
                    'processed': 0,
                    'no_provider': 0,
                    'skipped': 0,
                    'errors_tags': 0,
                    'errors_save': 0,
                    'success': 0,
                },
            )

            courier_bad = await Courier.load(courier_bad.courier_id)
            tap.ok(courier_bad, 'Курьер остался')
