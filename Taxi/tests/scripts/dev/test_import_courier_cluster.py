# pylint: disable=unused-argument

from aiohttp import web

from stall.client.eda_core_couriers import client as client_ec
from scripts.dev.import_courier_cluster import update_cluster


async def test_simple(tap, dataset, uuid, mock_client_response, ext_api):
    eda_region_id = uuid()

    cluster = await dataset.cluster(
        eda_region_id=eda_region_id,
    )

    async def handler_ec(request):
        return web.json_response({
            'courier': {
                'work_region': {
                    'id': eda_region_id,
                },
            },
        })

    with tap.plan(3, 'Выставление кластеров курьерам'):
        async with await ext_api(client_ec, handler_ec) as client:
            req = await client.courier_info(courier_eda_id='1234567')
            tap.ok(await req.json(), 'Получили ответ от eda-core')

            # Отрицательный результат не влияет на обработку запроса
            mock_client_response(status=500)

            courier = await dataset.courier(
                cluster_id=None,
                vars={
                    'external_ids': {
                        'eats': '1234567',
                    },
                },
            )

            tap.eq(courier.cluster_id, None, 'Кластер не назначен')

            await update_cluster(courier)

            await courier.reload()
            tap.eq(courier.cluster_id, cluster.cluster_id, 'Кластер назначен')


async def test_not_found(tap, dataset, mock_client_response):
    with tap.plan(2, 'Кластер не найден'):
        # Отрицательный результат не влияет на обработку запроса
        mock_client_response(status=500)

        courier = await dataset.courier(
            cluster_id=None,
            vars={
                'external_ids': {
                    'eats': '1234567',
                },
            },
        )

        tap.eq(courier.cluster_id, None, 'Кластер не назначен')

        await update_cluster(courier)

        await courier.reload()
        tap.eq(courier.cluster_id, None, 'Кластер назначен')


async def test_save_old(tap, dataset, uuid, mock_client_response):
    with tap.plan(2, 'Кластер не найден'):
        cluster = await dataset.cluster(
            eda_region_id=uuid(),
        )

        # Отрицательный результат не влияет на обработку запроса
        mock_client_response(status=500)

        courier = await dataset.courier(
            cluster_id=cluster.cluster_id,
            vars={
                'external_ids': {
                    'eats': '1234567',
                },
            },
        )

        tap.eq(courier.cluster_id, cluster.cluster_id, 'Кластер не назначен')

        await update_cluster(courier)

        await courier.reload()
        tap.eq(courier.cluster_id, cluster.cluster_id, 'Кластер назначен')
