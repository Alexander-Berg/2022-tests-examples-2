from aiohttp import web

from scripts.cron.compare_and_delete_translations import prepare_data_to_remove
from stall.client.tanker import client as tanker_client


async def test_compare_and_delete(tap, dataset, ext_api):
    with tap.plan(3, 'проверяем работу чистки ключей в танкере'):
        ps = [
            await dataset.product(
                vars={'locales': {'title': {
                    'en_US': 'big banana',
                    'ru_RU': 'большой банан',
                }}}
            )
            for _ in range(2)
        ]

        ps[1].vars['locales'] = {}
        await ps[1].save()

        async def tanker_handler(req):
            keyset = req.query['keyset-id']

            if keyset != 'testing_products_title':
                return web.json_response(
                    status=200,
                    data={'keysets': {keyset: {'keys': {}}}}
                )

            data = {'keysets': {keyset: {'keys': {
                ps[0].product_id + '_title': {
                    'translations': {
                        'ru': {'form': 'большой банан'},
                        'en': {'form': 'big banana'},
                        'fr': {'form': 'le banana petit pas =D'},
                        'he': {'form': ''},
                    }
                },
                ps[1].product_id + '_title': {
                    'translations': {'en': {'form': 'small banana'}}
                },
                'fake_key': {
                    'translations': {'en': {'form': 'fake translation'}}
                }
            }}}}
            return web.json_response(status=200, data=data)

        async with await ext_api(tanker_client, tanker_handler):
            keys_to_remove, trans_to_remove = await prepare_data_to_remove(
                project_id='lavka-ma',
                languages=['en', 'fr', 'ru', 'he'],
                mode='testing',
            )

        keys_to_remove = keys_to_remove['testing_products_title']
        trans_to_remove = trans_to_remove['testing_products_title']

        tap.eq(
            set(keys_to_remove),
            {ps[1].product_id + '_title', 'fake_key'},
            'удаляем нужные ключи',
        )
        tap.eq(
            set(trans_to_remove),
            {ps[0].product_id + '_title'},
            'чистим нужные ключи',
        )
        tap.eq(
            set(trans_to_remove[ps[0].product_id + '_title']),
            {'fr'},
            'чистим нужные языки',
        )


async def test_compare_and_delete_updated(tap, dataset, ext_api):
    with tap.plan(3, 'проверяем работу чистки ключей в танкере'):
        ps = [
            await dataset.product(
                vars={'locales': {'title': {
                    'en_US': 'big banana',
                    'ru_RU': 'большой банан',
                }}}
            )
            for _ in range(2)
        ]

        ps[1].vars['locales'] = {}
        await ps[1].save()

        async def tanker_handler(req):
            keyset = req.query['keyset-id']

            if keyset != 'testing_products_title':
                return web.json_response(
                    status=200,
                    data={'keysets': {keyset: {'keys': {}}}}
                )

            data = {'keysets': {keyset: {'keys': {
                ps[0].product_id + '_title': {
                    'translations': {
                        'ru': {'form': 'большой банан'},
                        'en': {'form': 'Big banana'},
                        'fr': {'form': 'le banana petit pas =D'},
                        'he': {'form': ''},
                    }
                },
                ps[1].product_id + '_title': {
                    'translations': {'en': {'form': 'small banana'}}
                },
                'fake_key': {
                    'translations': {'en': {'form': 'fake translation'}}
                }
            }}}}
            return web.json_response(status=200, data=data)

        async with await ext_api(tanker_client, tanker_handler):
            keys_to_remove, trans_to_remove = await prepare_data_to_remove(
                project_id='lavka-ma',
                languages=['en', 'fr', 'ru', 'he'],
                mode='testing',
            )

        keys_to_remove = keys_to_remove['testing_products_title']
        trans_to_remove = trans_to_remove['testing_products_title']

        tap.eq(
            set(keys_to_remove),
            {ps[1].product_id + '_title', 'fake_key'},
            'удаляем нужные ключи',
        )
        tap.eq(
            set(trans_to_remove),
            {ps[0].product_id + '_title'},
            'чистим нужные ключи',
        )
        tap.eq(
            set(trans_to_remove[ps[0].product_id + '_title']),
            {'fr'},
            'чистим нужные языки',
        )
