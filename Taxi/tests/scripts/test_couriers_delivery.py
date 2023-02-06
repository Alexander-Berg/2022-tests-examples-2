# pylint: disable=protected-access,unused-argument

from aiohttp import web

from scripts.couriers import CouriersDaemon
from stall.client.driver_profiles import client as client_dp
from stall.client.eda_core_couriers import client as client_ec


async def test_simple(tap, dataset, mock_client_response, ext_api, uuid):
    courier = await dataset.courier(
        cluster_id=None,
        vars={
            'external_ids': {
                'eats': uuid(),
            },
        },
    )

    async def handler_dp(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'data': {
                    'full_name': {
                        'first_name': 'Иван',
                        'last_name': 'Иванович',
                    },
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        })

    async def handler_ec(request):
        return web.json_response({
            'courier': {
                'courier_type': 'vehicle',
            },
        })

    with tap.plan(5, 'Обновление кластера курьера при обновлении информации'):
        async with await ext_api(client_dp, handler_dp) as client1:
            async with await ext_api(client_ec, handler_ec) as client2:
                req = await client1.driver_profiles_updates(
                    last_known_revision=None
                )
                tap.ok(await req.json(), 'Получили ответ от driver-profiles')

                req = await client2.courier_info(courier_eda_id='1234567')
                tap.ok(await req.json(), 'Получили ответ от eda-core')

                tap.eq(
                    courier.delivery_type,
                    'foot',
                    'Тип доставки пешком',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()

                tap.eq(
                    courier.delivery_type,
                    'car',
                    'Тип доставки обновился'
                )

                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )


async def test_load_data(tap, dataset, ext_api, unique_int, uuid):
    with tap.plan(5, 'Проверка работы load_data'):
        cluster_old = await dataset.cluster()
        cluster_new = await dataset.cluster(eda_region_id=uuid())
        courier = await dataset.courier(
            cluster=cluster_old,
            delivery_type='car',
            gender='female',
            birthday='12.12.1992',
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
        )

        async def handler_dp(request):
            return web.json_response({
                'profiles': [{
                    'park_driver_profile_id': courier.external_id,
                    'is_deleted': False,
                    'data': {
                        'license_expire_date': '2030-01-01T00:00:00.000',
                        'orders_provider': {
                            'lavka': True,
                        },
                    },
                }],
            })

        async def handler_ec(request):
            return web.json_response({
                'courier': {
                    'work_region': {
                        'id': cluster_new.eda_region_id,
                    },
                    'courier_type': 'pedestrian',
                    'gender': 'male',
                    'birthday': '01.01.1970',
                    'is_storekeeper': True,
                    'is_rover': True,
                },
            })

        async with await ext_api(client_dp, handler_dp), \
                await ext_api(client_ec, handler_ec):

            await CouriersDaemon()._process(None)

            with await courier.reload():
                tap.eq(courier.cluster_id, cluster_new.cluster_id, 'cluster_id')
                tap.eq(courier.delivery_type, 'foot', 'delivery_type')
                tap.eq(courier.gender, 'male', 'gender')
                tap.ok(courier.is_storekeeper, 'is_storekeeper')
                tap.ok(courier.is_rover, 'is_rover')
