# pylint: disable=unused-variable

import pytest


@pytest.mark.parametrize('status', ('active', 'disabled'))
async def test_delivery_zones(tap, api, dataset, status):
    with tap.plan(10, 'Получение списка зон'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster, status=status)
        await dataset.store(cluster=cluster, status='closed')
        courier = await dataset.courier(cluster=cluster)

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_delivery_zones',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.0')
        t.json_is('data.0.id', store.store_id)
        t.json_is('data.0.type', 'startPoint')
        t.json_is('data.0.attributes.name', store.title)
        t.json_hasnt('data.1')
        t.json_has('meta')
        t.json_is('meta.count', 1)


async def test_tags_store(tap, api, dataset):
    with tap.plan(15, 'Привязка к лавке'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        store1, store2 = sorted([store1, store2], key=lambda x: x.store_id)

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_delivery_zones',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.0')
        t.json_has('data.1')
        t.json_hasnt('data.2')
        t.json_has('meta')
        t.json_is('meta.count', 2)

        data = sorted(t.res['json']['data'], key=lambda x: x['id'])
        tap.eq(len(data), 2, 'data contains all stores')

        for store_data, store in zip(data, [store1, store2]):
            tap.note(f'store_id={store.store_id}')
            tap.eq(store_data['id'], store.store_id, 'store_id')
            tap.eq(store_data['type'], 'startPoint', 'startPoint')
            tap.eq(store_data['attributes']['name'], store.title, 'title')


async def test_tags_store_flag_disabled(tap, api, dataset, cfg):
    with tap.plan(10, 'Привязка к лавке'):
        cfg.set('flags.courier_shift_public_attr', False)

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_delivery_zones',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_has('data.0')
        t.json_is('data.0.id', store1.store_id, 'store_id')
        t.json_is('data.0.type', 'startPoint', 'startPoint')
        t.json_is('data.0.attributes.name', store1.title, 'title')
        t.json_hasnt('data.1')
        t.json_has('meta')
        t.json_is('meta.count', 1)
