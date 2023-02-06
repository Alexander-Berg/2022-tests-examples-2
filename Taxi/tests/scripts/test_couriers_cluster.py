# pylint: disable=protected-access,unused-argument

from aiohttp import web
import pytest

from libstall.util import uuid
from scripts.couriers import CouriersDaemon
from stall.client.driver_profiles import client as client_dp
from stall.client.eda_core_couriers import client as client_ec


async def test_update_to_none(
        tap, dataset, mock_client_response, ext_api,
):
    eda_id = uuid()

    cluster = await dataset.cluster()
    courier = await dataset.courier(
        cluster=cluster,
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
                'work_region': {
                    'id': None,
                },
            },
        })

    with tap.plan(5, 'Обновление курьера с назначенным кластером'):
        async with await ext_api(client_dp, handler_dp) as client1:
            async with await ext_api(client_ec, handler_ec) as client2:
                req = await client1.driver_profiles_updates(
                    last_known_revision=None
                )
                tap.ok(await req.json(), 'Получили ответ от driver-profiles')

                req = await client2.courier_info(courier_eda_id='1234567')
                tap.ok(req is None or await req.json(), 'Получили ответ от ec')

                tap.eq(
                    courier.cluster_id,
                    cluster.cluster_id,
                    'Старый кластер',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()
                tap.eq(
                    courier.cluster_id,
                    cluster.cluster_id,
                    'Кластер остался тем же'
                )

                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )


async def test_replace(
        tap, dataset, mock_client_response, ext_api,
):
    eda_id = uuid()

    cluster = await dataset.cluster()
    courier = await dataset.courier(
        cluster=cluster,
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

    cluster_new = await dataset.cluster(
        eda_region_id=uuid(),
    )

    async def handler_ec(request):
        return web.json_response({
            'courier': {
                'work_region': {
                    'id': cluster_new.eda_region_id,
                },
            },
        })

    with tap.plan(5, 'Обновление курьера с назначенным кластером'):
        async with await ext_api(client_dp, handler_dp) as client1:
            async with await ext_api(client_ec, handler_ec) as client2:
                req = await client1.driver_profiles_updates(
                    last_known_revision=None
                )
                tap.ok(await req.json(), 'Получили ответ от driver-profiles')

                req = await client2.courier_info(courier_eda_id='1234567')
                tap.ok(req is None or await req.json(), 'Получили ответ от ec')

                tap.eq(
                    courier.cluster_id,
                    cluster.cluster_id,
                    'Старый кластер',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()
                tap.eq(
                    courier.cluster_id,
                    cluster_new.cluster_id,
                    'Кластер обновился'
                )

                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )


async def test_update(
        tap, dataset, mock_client_response, ext_api,
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

    cluster_new = await dataset.cluster(
        eda_region_id=uuid(),
    )

    async def handler_ec(request):
        return web.json_response({
            'courier': {
                'work_region': {
                    'id': cluster_new.eda_region_id,
                },
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
                    courier.cluster_id,
                    None,
                    'Кластер не назначен',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()

                tap.eq(
                    courier.cluster_id,
                    cluster_new.cluster_id,
                    'Кластер назначен'
                )

                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )


@pytest.mark.parametrize('eats_region_id', (
    None,  # Без обновления кластера
    123,  # Неверный формат кластера
    '',  # Неверный формат кластера
    '2072fdcd3ee54478950d7cc0d1935965',  # Неизвестный кластер
))
async def test_no_updates(
        tap, dataset, mock_client_response, ext_api, eats_region_id,
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
                'work_region': {
                    'id': eats_region_id,
                },
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
                    courier.cluster_id,
                    None,
                    'Кластер не назначен',
                )

                # Отрицательный результат не влияет на обработку запроса
                mock_client_response(status=500)

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()

                tap.eq(
                    courier.cluster_id,
                    None,
                    'Кластер не назначен'
                )

                tap.eq(
                    courier.first_name,
                    'Иван',
                    'Данные обновлены'
                )


async def test_lsn(
        tap, dataset, mock_client_response, ext_api, unique_int,
):
    with tap.plan(1, 'не обновляем данные если ничего не изменилось'):

        cluster = await dataset.cluster(eda_region_id=str(unique_int()))
        eda_id = unique_int()

        courier = await dataset.courier(
            cluster=cluster,
            first_name='Иван',
            last_name='Иванович',
            vars={
                'car_id': None,
                'email_pd_ids': None,
                'external_ids': {'eats': eda_id},
                'is_deaf': None,
                'park_id': None,
                'phone_pd_ids': None,
                'uuid': uuid(),
            },
            order_provider='lavka',
        )

        async def handler_dp(request):
            return web.json_response({
                'profiles': [{
                    'park_driver_profile_id': courier.external_id,
                    'data': {
                        'full_name': {
                            'first_name': courier.first_name,
                            'last_name': courier.last_name,
                        },
                        'orders_provider': {
                            'lavka': True,
                        },
                        'uuid': courier.vars('uuid'),
                        'external_ids': {
                            'eats': courier.vars('external_ids.eats'),
                        },
                    },
                }],
            })

        async def handler_ec(request):
            return web.json_response({
                'courier': {
                    'work_region': {
                        'id': cluster.eda_region_id,
                    },
                },
            })

        async with await ext_api(client_dp, handler_dp):
            async with await ext_api(client_ec, handler_ec):
                old_lsn = courier.lsn

                process = CouriersDaemon()._process
                await process(None)

                await courier.reload()

                tap.eq(courier.lsn, old_lsn, 'Курьер не сохранялся')
