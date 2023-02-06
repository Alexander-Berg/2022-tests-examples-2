# pylint: disable=protected-access,unused-argument

import pytest
from aiohttp import web

from libstall.util import time2time, datetime, tzone
from stall.client.driver_profiles import client as client_dp
from scripts.couriers import TAG_BEGINNER, CouriersDaemon


async def test_no_external_ids(
        tap, dataset, uuid, mock_client_response, ext_api,
):
    eda_id_old = uuid()
    park_id = uuid()

    cluster = await dataset.cluster()
    courier = await dataset.courier(
        cluster=cluster,
        vars={
            'external_ids': {
                'eats': eda_id_old,
            },
        },
    )

    async def handler(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'is_deleted': False,
                'data': {
                    'park_id': park_id,
                },
            }],
        })

    with tap.plan(3, 'Не убирать Едовый id, если он есть, но не пришёл'):
        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_old,
                'Едовый id есть',
            )

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            process = CouriersDaemon()._process
            await process(None)

            await courier.reload()

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_old,
                'Едовый id остался старым'
            )


@pytest.mark.parametrize('external_ids', (
    None,
    {},
    {'eats': None},
))
async def test_null_external_ids(
        tap, dataset, uuid, mock_client_response, external_ids, ext_api,
):
    eda_id_old = uuid()
    park_id = uuid()

    cluster = await dataset.cluster()
    courier = await dataset.courier(
        cluster=cluster,
        vars={
            'external_ids': {
                'eats': eda_id_old,
            },
        },
    )

    async def handler(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'is_deleted': False,
                'data': {
                    'park_id': park_id,
                    'external_ids': external_ids,
                },
            }],
        })

    with tap.plan(3, 'Не убирать Едовый id, если он пришёл пустым'):
        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_old,
                'Едовый id есть',
            )

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            process = CouriersDaemon()._process
            await process(None)

            await courier.reload()

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_old,
                'Едовый id остался старым'
            )


async def test_update_external_ids(
        tap, dataset, uuid, mock_client_response, ext_api,
):
    eda_id_old = uuid()
    eda_id_new = uuid()

    cluster = await dataset.cluster()
    courier = await dataset.courier(
        cluster=cluster,
        vars={
            'external_ids': {
                'eats': eda_id_old,
            },
        },
    )

    async def handler(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'is_deleted': False,
                'data': {
                    'external_ids': {
                        'eats': eda_id_new,
                    },
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        })

    with tap.plan(4, 'Обновление Едового id'):
        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_old,
                'Едовый id есть',
            )

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            process = CouriersDaemon()._process
            await process(None)

            await courier.reload()

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id_new,
                'Едовый id обновился'
            )
            tap.ok(
                set(courier.tags).isdisjoint([TAG_BEGINNER]),
                'тег новичка не выдан, т.к. текущий профиль уже без тега'
            )


async def test_set_external_ids(
        tap, dataset, uuid, mock_client_response, ext_api,
):
    cluster = await dataset.cluster()
    courier = await dataset.courier(cluster=cluster)
    await dataset.courier_shift_tag(title=TAG_BEGINNER)

    eda_id = uuid()

    async def handler(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'is_deleted': False,
                'data': {
                    'external_ids': {
                        'eats': eda_id,
                    },
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        })

    with tap.plan(4, 'Установка Едвого id когда его не было'):
        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                None,
                'Едовый id пуст',
            )

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            process = CouriersDaemon()._process
            await process(None)

            await courier.reload()

            tap.eq(
                (courier.vars.get('external_ids') or {}).get('eats', None),
                eda_id,
                'Едовый id обновился'
            )
            tap.ok(
                set(courier.tags).intersection([TAG_BEGINNER]),
                'тег новичка назначен'
            )


@pytest.mark.parametrize('expire_old,expire_new', (
    (None, '2030-01-01T00:00:00.000'),
    (datetime(2018, 6, 12, 20, tzinfo=tzone('UTC')), '2030-01-01T00:00:00.000'),
))
async def test_set_license_expire(
        tap, dataset, mock_client_response, ext_api, expire_old, expire_new,
):
    cluster = await dataset.cluster()
    courier = await dataset.courier(cluster=cluster, license_expire=expire_old)

    async def handler(request):
        return web.json_response({
            'profiles': [{
                'park_driver_profile_id': courier.external_id,
                'is_deleted': False,
                'data': {
                    'license_expire_date': expire_new,
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        })

    with tap.plan(3, 'Установка срока действия прав'):
        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            tap.eq(
                courier.license_expire,
                expire_old,
                'Срок действия прав не установлен',
            )

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            process = CouriersDaemon()._process
            await process(None)

            await courier.reload()

            tap.eq(
                courier.license_expire,
                time2time(expire_new),
                'Срок действия прав установлен',
            )


async def test_create_beginner_ok(
        tap, dataset, uuid, mock_client_response, ext_api,
):
    with tap.plan(7, 'Создание курьера-новичка два раза подряд'):
        park_driver_profile_id = [f'{uuid()}_{uuid()}']
        eda_id = uuid()

        async def handler(request):
            return web.json_response({
                'profiles': [{
                    'park_driver_profile_id': park_driver_profile_id[0],
                    'is_deleted': False,
                    'data': {
                        'orders_provider': {
                            'eda': True,
                        },
                        'park_id': uuid(),
                        'work_status': 'working',
                        'full_name': {
                            'first_name': uuid(),
                            'middle_name': uuid(),
                            'last_name': uuid(),
                        },
                        'license': {
                            'pd_id': uuid(),
                        },
                        'external_ids': {
                            'eats': eda_id,  # у обоих профилей один eda_id
                        },
                    },
                }],
            })

        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            # создаем профиль №1
            process = CouriersDaemon()._process
            await process(None)

            courier = await dataset.Courier.find_by_id(
                courier_id=park_driver_profile_id[0],
            )

            tap.eq(courier.external_id,
                   park_driver_profile_id[0],
                   'external_id')
            tap.eq(courier.vars['external_ids']['eats'], eda_id, 'eda_id')
            tap.ok(TAG_BEGINNER in courier.tags, 'тег-новичок')

            # меняем идентификатор
            park_driver_profile_id[0] = f'{uuid()}_{uuid()}'

            # создаем профиль №2
            process = CouriersDaemon()._process
            await process(None)

            courier = await dataset.Courier.find_by_id(
                courier_id=park_driver_profile_id[0],
            )

            tap.eq(courier.external_id,
                   park_driver_profile_id[0],
                   'external_id')
            tap.eq(courier.vars['external_ids']['eats'], eda_id, 'eda_id')
            tap.ok(TAG_BEGINNER in courier.tags, 'тег-новичок опять на месте')


async def test_create_beginner_fail(
        tap, dataset, uuid, mock_client_response, ext_api,
):
    with tap.plan(4, 'Новичок не создается, если уже был профиль не новичок'):
        park_driver_profile_id = f'{uuid()}_{uuid()}'
        eda_id = uuid()

        await dataset.courier(
            vars={
                'external_ids': {
                    'eats': eda_id,  # у обоих профилей один eda_id
                },
            }
        )

        async def handler(request):
            return web.json_response({
                'profiles': [{
                    'park_driver_profile_id': park_driver_profile_id,
                    'is_deleted': False,
                    'data': {
                        'orders_provider': {
                            'eda': True,
                        },
                        'park_id': uuid(),
                        'work_status': 'working',
                        'full_name': {
                            'first_name': uuid(),
                            'middle_name': uuid(),
                            'last_name': uuid(),
                        },
                        'license': {
                            'pd_id': uuid(),
                        },
                        'external_ids': {
                            'eats': eda_id,  # у обоих профилей один eda_id
                        },
                    },
                }],
            })

        async with await ext_api(client_dp, handler) as client:
            req = await client.driver_profiles_updates(last_known_revision=None)
            tap.ok(await req.json(), 'Получили ответ от внешнего API')

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            # создаем профиль №1
            process = CouriersDaemon()._process
            await process(None)

            courier = await dataset.Courier.find_by_id(
                courier_id=park_driver_profile_id,
            )

            tap.eq(courier.external_id, park_driver_profile_id, 'external_id')
            tap.eq(courier.vars['external_ids']['eats'], eda_id, 'eda_id')
            tap.ok(TAG_BEGINNER not in courier.tags, 'тег-новичок не выдан')
