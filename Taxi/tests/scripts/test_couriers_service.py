# pylint: disable=unused-argument,protected-access

from aiohttp import web

from stall.client.driver_profiles import client as client_dp
from stall.client.eda_core_couriers import client as client_ec
from scripts.couriers import CouriersDaemon


async def test_simple(
        tap, dataset, mock_client_response, ext_api, uuid,
):
    eda_id = uuid()
    courier = await dataset.courier(
        cluster_id=None,
        vars={
            'external_ids': {
                'eats': eda_id,
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
                'courier_service': {
                    'id': 1234,
                    'name': 'Мегаслужба',
                },
            },
        })

    with tap.plan(7, 'Обновление курьерской службы при обновлении информации'):
        async with await ext_api(client_dp, handler_dp) as client1:
            async with await ext_api(client_ec, handler_ec) as client2:
                req = await client1.driver_profiles_updates(
                    last_known_revision=None,
                )
                tap.ok(await req.json(), 'Получили ответ от driver-profiles')

                req = await client2.courier_info(courier_eda_id='1234567')
                tap.ok(await req.json(), 'Получили ответ от eda-core')

                tap.eq(
                    courier.courier_service_id,
                    None,
                    'ID курьской службы не назначен',
                )
                tap.eq(
                    courier.courier_service_name,
                    None,
                    'Название курьской службы не назначено',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()

                tap.eq(
                    courier.courier_service_id,
                    1234,
                    'ID курьской службы не назначен',
                )
                tap.eq(
                    courier.courier_service_name,
                    'Мегаслужба',
                    'Название курьской службы не назначено',
                )
                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )
