# pylint: disable=too-many-locals
from stall.script import csv2dicts


async def test_simple(tap, api, dataset):
    with tap.plan(15, 'Экспорт CSV файла со списоком курьеров'):
        user = await dataset.user(role='admin')
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        courier3 = await dataset.courier(cluster=await dataset.cluster())
        courier4 = await dataset.courier(cluster=cluster, tags=['olo', 'ulu'])
        courier5 = await dataset.courier(
            cluster=cluster,
            first_name='Иван',
            status='disabled',
            vars={'external_ids': {'eats': '1234567'}},
        )
        courier6 = await dataset.courier(
            cluster=cluster,
            tags_store=[store.store_id],
        )

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_export_data', json={
            'cluster_id': cluster.cluster_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('csv')

        csv = t.res['json']['csv']
        result = {x['courier_id']: x for x in csv2dicts(csv)}

        with courier1 as courier:
            tap.ok(result[courier.courier_id], 'Курьер кластера выведен')
            tap.eq(
                result[courier.courier_id]['depot_id'],
                '',
                'Не привязан к лавке'
            )

        with courier2 as courier:
            tap.ok(result[courier.courier_id], 'Курьер кластера выведен')
            tap.eq(
                result[courier.courier_id]['depot_id'],
                '',
                'Не привязан к лавке'
            )

        with courier3 as courier:
            tap.ok(
                courier.courier_id not in result,
                'Курьер из другого кластера не выведен'
            )

        with courier4 as courier:
            tap.ok(result[courier.courier_id], 'Курьер кластера выведен')
            tap.eq(
                result[courier.courier_id]['depot_id'],
                '',
                'Не привязан к лавке'
            )
            tap.eq(
                result[courier.courier_id]['tags'],
                ','.join(['olo', 'ulu']),
                'Теги выведены'
            )

        with courier5 as courier:
            tap.ok(result[courier.courier_id], 'Отключенный выведен')

        with courier6 as courier:
            tap.ok(result[courier.courier_id], 'Курьер кластера выведен')
            tap.eq(
                result[courier.courier_id]['depot_id'],
                store.external_id,
                'Привязан к лавке'
            )


async def test_tags(tap, api, dataset, uuid):
    with tap.plan(9, 'Экспорт CSVс фильтром по тегам'):
        user = await dataset.user(role='admin')

        uniq_tag = f"{uuid()}"
        courier1 = await dataset.courier(tags=[uniq_tag])
        courier2 = await dataset.courier(tags=[uniq_tag, 'aloha'])
        courier3 = await dataset.courier(tags=['qwerty', uniq_tag, 'aloha'])
        courier4 = await dataset.courier(tags=['aloha'])
        courier5 = await dataset.courier()

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_export_data', json={
            'tags': [uniq_tag],
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('csv')

        t.json_like('csv', courier1.courier_id, 'Курьер 1 выведен')
        t.json_like('csv', courier2.courier_id, 'Курьер 2 выведен')
        t.json_like('csv', courier3.courier_id, 'Курьер 3 выведен')
        t.json_unlike('csv', courier4.courier_id, 'Курьер 4 не выведен')
        t.json_unlike('csv', courier5.courier_id, 'Курьер 5 не выведен')


async def test_status(tap, api, dataset, uuid):
    with tap.plan(7, 'Экспорт только активных курьеров'):
        user = await dataset.user(role='admin')

        uniq_tag = f"{uuid()}"
        courier1 = await dataset.courier(tags=[uniq_tag], status='active')
        courier2 = await dataset.courier(tags=[uniq_tag], status='disabled')
        courier3 = await dataset.courier(tags=[uniq_tag], status='removed')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_export_data', json={
            'tags': [uniq_tag],
            'status': 'active',
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('csv')

        t.json_like('csv', courier1.courier_id, 'Курьер 1 выведен')
        t.json_unlike('csv', courier2.courier_id, 'Курьер 2 не выведен')
        t.json_unlike('csv', courier3.courier_id, 'Курьер 3 не выведен')
