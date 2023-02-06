from aiohttp import web

from stall.client.pigeon import client as pigeon_client
from stall.client.pigeon_chef import client as chef_client
from stall.client.pigeon_nana import client as nana_client
from stall.client.tanker import client as tanker_client
from scripts.cron.sync_products import main


async def test_cursors(tap, dataset, ext_api, cfg, load_json, uuid):
    # pylint: disable=too-many-return-statements, unused-argument, too-many-locals, too-many-statements
    with tap.plan(12, 'Сохранение курсоров'):

        async def handler_pigeon(req):
            rj = await req.json()

            if 'actual-categories' in req.path:
                if rj.get('lastCursor') == 2:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 2,
                            'items': [categories[2]]
                        }
                    )
                if rj.get('lastCursor') >= 3:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 4,
                            'items': [categories[3]]
                        }
                    )
                return web.json_response(
                    status=200,
                    data={
                        'lastCursor': 2,
                        'items': [
                            categories[0],
                            categories[1]
                        ]
                    }
                )

            if 'deleted-categories' in req.path:
                if rj.get('lastCursor') == 1:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 1,
                            'items': [categories[3]['code']]
                        }
                    )
                if rj.get('lastCursor') >= 2:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 3,
                            'items': [categories[3]['code']]
                        }
                    )
                return web.json_response(
                    status=200,
                    data={
                        'lastCursor': 1,
                        'items': [categories[2]['code']]
                    }
                )

            if 'actual-products' in req.path:
                if rj.get('lastCursor') == 2:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 2,
                            'items': [products[2]]
                        }
                    )
                if rj.get('lastCursor') >= 3:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 4,
                            'items': [products[3]]
                        }
                    )
                return web.json_response(
                    status=200,
                    data={
                        'lastCursor': 2,
                        'items': [
                            products[0],
                            products[1]
                        ]
                    }
                )

            if 'deleted-products' in req.path:
                if rj.get('lastCursor') == 1:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 1,
                            'items': [products[3]['skuId']]
                        }
                    )
                if rj.get('lastCursor') >= 2:
                    return web.json_response(
                        status=200,
                        data={
                            'lastCursor': 3,
                            'items': [products[3]['skuId']]
                        }
                    )
                return web.json_response(
                    status=200,
                    data={
                        'lastCursor': 1,
                        'items': [products[2]['skuId']]
                    }
                )

            return web.json_response(
                status=500,
                data={
                    'code': 'BAD_REQUEST',
                    'message': 'Incorrect request'
                }
            )

        async def handler_tanker(req):
            return web.json_response(
                status=500,
                data={
                    'code': 'Ne ok'
                }
            )

        products = []
        categories = []
        for product in load_json('data/products.pigeon.json'):
            product['skuId'] = uuid()
            products.append(product)

        for group in load_json('data/categories.pigeon.json'):
            group['code'] += ':' + uuid()
            categories.append(group)

        cfg.set('pigeon_chef.login', 'login')
        cfg.set('pigeon_chef.password', 'password')

        product_stash_name = 'sync_product_cursors' + uuid()
        product_group_stash_name = 'sync_product_group_cursors' + uuid()

        tap.eq(
            await dataset.Stash.load(
                product_stash_name, by='name'
            ),
            None,
            'Нет стеша с курсорами'
        )

        tap.eq(
            await dataset.Stash.load(
                product_group_stash_name, by='name'
            ),
            None,
            'Нет стеша с курсорами'
        )

        async with await ext_api(
            pigeon_client, handler_pigeon
        ), await ext_api(
            chef_client, handler_pigeon
        ), await ext_api(
            nana_client, handler_pigeon
        ), await ext_api(
            tanker_client, handler_tanker
        ):
            await main(
                product_stash_name=product_stash_name,
                product_group_stash_name=product_group_stash_name
            )

        product_cursors = await dataset.Stash.load(
            product_stash_name, by='name'
        )

        tap.ok(product_cursors, 'Курсоры на месте')

        product_group_cursors = await dataset.Stash.load(
            product_group_stash_name, by='name'
        )

        tap.ok(product_group_cursors, 'Курсоры на месте')

        tap.eq(
            product_cursors.value['actual_cursor'], 2,
            'Верный курсор актуальных групп'
        )
        tap.eq(
            product_cursors.value['deleted_cursor'], 1,
            'Верный курсор удаленных групп'
        )
        tap.eq(
            product_group_cursors.value['actual_cursor'], 2,
            'Верный курсор актуальных продуктов'
        )
        tap.eq(
            product_group_cursors.value['deleted_cursor'], 1,
            'Верный курсор удаленных продуктов'
        )

        product_cursors.value['actual_cursor'] = 3
        product_cursors.value['deleted_cursor'] = 2
        product_group_cursors.value['actual_cursor'] = 3
        product_group_cursors.value['deleted_cursor'] = 2

        product_cursors.rehashed(value=True)
        await product_cursors.save()

        product_group_cursors.rehashed(value=True)
        await product_group_cursors.save()

        async with await ext_api(
            pigeon_client, handler_pigeon
        ), await ext_api(
            chef_client, handler_pigeon
        ), await ext_api(
            nana_client, handler_pigeon
        ), await ext_api(
            tanker_client, handler_tanker
        ):
            await main(
                product_stash_name=product_stash_name,
                product_group_stash_name=product_group_stash_name
            )

        await product_cursors.reload()
        await product_group_cursors.reload()

        tap.eq(
            product_cursors.value['actual_cursor'], 4,
            'Верный курсор актуальных групп'
        )
        tap.eq(
            product_cursors.value['deleted_cursor'], 3,
            'Верный курсор удаленных групп'
        )
        tap.eq(
            product_group_cursors.value['actual_cursor'], 4,
            'Верный курсор актуальных продуктов'
        )
        tap.eq(
            product_group_cursors.value['deleted_cursor'], 3,
            'Верный курсор удаленных продуктов'
        )
