from datetime import timedelta


async def test_simple(tap, api, dataset, uuid):
    with tap.plan(16, 'Пауза смены'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        pro_event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': pro_event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')

            pause = shift.shift_events[-2]

            with shift.shift_events[-1] as event:
                tap.eq(
                    event.shift_event_id,
                    f'{pause.shift_event_id}:unpaused',
                    'shift_event_id'
                )
                tap.eq(event.type, 'unpaused', 'unpaused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    event.detail['shift_event_id'],
                    pause.shift_event_id,
                    'shift_event_id'
                )
                tap.eq(
                    event.detail['pro_event_id'],
                    pro_event_id,
                    'pro_event_id'
                )

        pro_event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': pro_event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)


async def test_unpause_user(tap, api, dataset, uuid):
    with tap.plan(2, 'Куьер не может снимать паузу пользователя'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_max_count': 1},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        user = await dataset.user(store=store)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[
                {
                    'user_id': user.user_id,
                    'type': 'paused',
                },
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)


async def test_unpause_race_condition(tap, api, dataset, uuid):
    with tap.plan(11, 'Проверка отсутствия гонок условий'):
        store = await dataset.store()
        courier = await dataset.courier()

        pause_event_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[
                # симуляция ситуации, когда пауза открыта,
                # но кто-то успел ее закрыть
                dataset.CourierShiftEvent({
                    'shift_event_id': f'{pause_event_id}:unpaused',
                    'type': 'unpaused',
                    'location': {
                        'lat': 100.0,
                        'lon': 500.0,
                    },
                    'detail': {
                        'shift_event_id': pause_event_id,
                    },
                }),
                dataset.CourierShiftEvent({
                    'shift_event_id': pause_event_id,
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                }),
            ]
        )

        pro_event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': pro_event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 2, '0 новых событий')

            pause = shift.shift_events[1]

            with shift.shift_events[0] as event:
                tap.eq(
                    event.shift_event_id,
                    f'{pause.shift_event_id}:unpaused',
                    'shift_event_id'
                )
                tap.eq(event.type, 'unpaused', 'unpaused')
                # location первого события, т.е. не перетерто и не дублируется
                tap.eq(event.location.lat, 100.0, 'lat')
                tap.eq(event.location.lon, 500.0, 'lon')
                tap.eq(event.courier_id, None, 'courier_id не задан')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    event.detail['shift_event_id'],
                    pause.shift_event_id,
                    'shift_event_id'
                )


async def test_unpause_scheduled_pause(
        tap, api, dataset, now, push_events_cache, job, uuid,
):
    with tap.plan(6, 'Запуск отложенной паузы по чекину курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[{'type': 'schedule_pause'}],
            started_at=now() - timedelta(hours=1),
            closes_at=now() + timedelta(hours=1),
        )

        courier.checkin_time = now()
        tap.ok(await courier.save(), 'Курьер зачекинился')

        await push_events_cache(courier, job_method='job_start_schedule_pause')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)
