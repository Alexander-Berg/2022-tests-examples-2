# pylint: disable=unused-variable,too-many-statements,unused-variable
import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_subscribe(tap, api, dataset, subscribe):
    with tap.plan(26, 'Список'):

        company = await dataset.company()
        store = await dataset.store(company=company)
        # создается по умолчанию
        # zone1 = await dataset.zone(store=store, status='active')

        zone2 = await dataset.zone(store=store, status='disabled')
        zone3 = await dataset.zone(store=store, status='template')

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_zones_list',
            json={'cursor': None, 'subscribe': subscribe},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('zones', 'Список присутствует')

        t.json_has('zones.0', 'элементы есть')
        t.json_has('zones.0.zone_id')
        t.json_has('zones.0.store_id')
        t.json_has('zones.0.status')
        t.json_has('zones.0.delivery_type')
        t.json_has('zones.0.delivery_type')
        t.json_has('zones.0.effective_from')
        t.json_has('zones.0.effective_till')
        t.json_has('zones.0.updated')
        t.json_has('zones.0.created')

        t.json_has('zones.1', 'элементы есть')
        t.json_has('zones.1.zone_id')
        t.json_has('zones.1.store_id')
        t.json_has('zones.1.status')
        t.json_has('zones.1.delivery_type')
        t.json_has('zones.1.delivery_type')
        t.json_has('zones.1.effective_from')
        t.json_has('zones.1.effective_till')
        t.json_has('zones.1.updated')
        t.json_has('zones.1.created')

        t.json_hasnt('zones.2')


@pytest.mark.parametrize(['delivery_type', 'mapped_delivery_type'], [
    ('foot_external', 'foot'),
    ('foot_night', 'foot'),
    ('foot', 'foot'),
])
async def test_list_map_delivery_type(
        tap, api, dataset, delivery_type, mapped_delivery_type
):
    with tap:
        company = await dataset.company()
        store = await dataset.store(company=company)

        zone = await dataset.zone(store=store, delivery_type=delivery_type)

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_zones_list',
            json={'cursor': None},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('zones', 'Список присутствует')

        t.json_has('zones.0', 'элементы есть')
        t.json_is('zones.0.delivery_type', mapped_delivery_type)
