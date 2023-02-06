async def test_simple(tap, api, dataset):
    with tap.plan(6, 'Возобновление смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            status='processing',
            courier=courier,
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }, {
                'courier_id': courier.courier_id,
                'type': 'paused',
                'location': {'lon': 33, 'lat': 55},
            }],
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_unpause', json={
            'id': courier.external_id,
        })

        t.status_is(200, diag=True)
        t.json_is('current_slot_shift_id', shift.courier_shift_id, 'ID')

        await shift.reload()
        pause = shift.shift_events[-2]
        tap.ok(pause, 'Пауза была')

        event = shift.shift_events[-1]
        tap.eq(event.type, 'unpaused', 'unpaused')
        tap.eq(
            event.detail['shift_event_id'],
            pause.shift_event_id,
            'shift_event_id'
        )
