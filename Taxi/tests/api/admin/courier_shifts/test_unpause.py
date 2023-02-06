# pylint: disable=too-many-locals


async def test_unpause(tap, api, dataset):
    with tap.plan(12, 'Остановка смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
            status='processing',
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_unpause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )

        with await shift.reload():
            pause = shift.shift_events[-2]
            tap.ok(pause, 'Пауза была')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'unpaused', 'unpaused')
                tap.eq(
                    event.detail['shift_event_id'],
                    pause.shift_event_id,
                    'shift_event_id'
                )
                tap.eq(event.user_id, user.user_id, 'user_id')
                tap.eq(event.courier_id, None, 'courier_id none')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Повторное снятие успешно')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )


async def test_gone(tap, api, dataset):
    with tap.plan(3, 'Остановка смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
            status='complete',
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                    'location': {'lon': 33, 'lat': 55},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_unpause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')
