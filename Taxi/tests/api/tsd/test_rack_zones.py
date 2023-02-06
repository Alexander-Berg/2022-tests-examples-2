async def test_rack_zones(tap, api, dataset):
    with tap.plan(6, 'Запрос зон РЦ'):

        store = await dataset.store()

        user = await dataset.user(
            role='executer',
            store_id=store.store_id,
        )
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)

        rack_zone = await dataset.rack_zone(store_id=store.store_id)

        await t.post_ok(
            'api_tsd_rack_zones',
            json={
                'rack_zone_ids': [rack_zone.rack_zone_id],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('rack_zones.0.rack_zone_id', rack_zone.rack_zone_id)
        t.json_is('rack_zones.0.external_id', rack_zone.external_id)


async def test_empty_request(tap, api, dataset):
    with tap.plan(4, 'Запрос зон РЦ с пустым списком idшников'):

        store = await dataset.store()

        user = await dataset.user(
            role='executer',
            store_id=store.store_id,
        )
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_rack_zones',
            json={
                'rack_zone_ids': [],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
