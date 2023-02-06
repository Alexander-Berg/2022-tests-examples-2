async def test_racks(tap, api, dataset):
    with tap.plan(6, 'Запрос стеллажей'):

        store = await dataset.store()

        user = await dataset.user(
            role='executer',
            store_id=store.store_id,
        )
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)

        rack = await dataset.rack(store_id=store.store_id)

        await t.post_ok(
            'api_tsd_racks',
            json={
                'rack_ids': [rack.rack_id],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('racks.0.rack_id', rack.rack_id)
        t.json_is('racks.0.external_id', rack.external_id)


async def test_racks_nf(tap, api, uuid):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok(
            'api_tsd_racks',
            json={
                'rack_ids': [uuid()],
            }
        )

        t.status_is(403, diag=True)
