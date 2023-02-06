from aiohttp import web
import pytest

from libstall.util import uuid
from stall.client.personal import client as pd_client


async def test_simple(tap, dataset, api, ext_api):
    with tap.plan(4, 'Получаем 2 номера курьера'):
        user = await dataset.user(role='admin')
        pd_id_1, pd_id_2 = uuid(), uuid()
        courier = await dataset.courier(
            vars={
                "phone_pd_ids": [
                    {"pd_id": pd_id_1},
                    {"pd_id": pd_id_2},
                ]
            }
        )

        async def handler(request):  # pylint: disable=unused-argument
            tap.note('Ручка вызвана')
            return 200, {
                'code': 'OK',
                'items': [
                    {'id': pd_id_1, 'value': 'phone_1'},
                    {'id': pd_id_2, 'value': 'phone_2'},
                ],
            }

        async with await ext_api(pd_client, handler):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load_phone',
                json={'courier_id': courier.courier_id},
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код')
            t.json_is('phones', ['phone_1', 'phone_2'], 'номера телефонов')


@pytest.mark.parametrize(
    'body', [
        # номера не найдены
        {'code': 'OK', 'items': []},

        # ошибки формата данных
        {'code': 'OK', 'items': None},
        {'code': 'OK', 'items': uuid()},
        {},
        None,
        '',
        'dfasdfsfdasdg',
    ]
)
async def test_error_response(tap, dataset, api, ext_api, body):
    with tap.plan(4, f'Проверка обработки ошибок в ответах сервиса: {body}'):
        user = await dataset.user(role='admin')
        courier = await dataset.courier(
            vars={
                "phone_pd_ids": [
                    {"pd_id": uuid()},
                ]
            }
        )

        async def handler(request):  # pylint: disable=unused-argument
            tap.passed('Ручка вызвана')
            return 200, body

        async with await ext_api(pd_client, handler):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load_phone',
                json={'courier_id': courier.courier_id},
            )
            t.status_is(424, diag=True)
            t.json_is('code', 'ER_EXTERNAL_SERVICE', 'код')


async def test_error_json_decoder(tap, dataset, api, ext_api):
    with tap.plan(4, 'Проверка обработки ошибки в JSON'):
        user = await dataset.user(role='admin')
        courier = await dataset.courier(
            vars={
                "phone_pd_ids": [
                    {"pd_id": uuid()},
                ]
            }
        )

        async def handler(request):  # pylint: disable=unused-argument
            tap.passed('Ручка вызвана')
            return web.Response(
                status=200,
                body='dfasdfsfdasdg',
                content_type='application/json'
            )

        async with await ext_api(pd_client, handler):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load_phone',
                json={'courier_id': courier.courier_id},
            )
            t.status_is(424, diag=True)
            t.json_is('code', 'ER_EXTERNAL_SERVICE', 'код')
