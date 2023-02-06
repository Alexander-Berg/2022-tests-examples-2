from datetime import timedelta


async def test_pause_none_duration(tap, dataset):
    with tap.plan(2, 'пользователь: пауза без ограничений'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                {
                    'user_id': user.user_id,
                    'type': 'paused',
                },
            ],
        )

        pause = shift.event_paused()
        tap.ok(pause, 'пауза начата')

        tap.eq(
            shift.pause_ends_at(pause),
            shift.closes_at,
            'без продолжительности до конца смены'
        )


async def test_pause_duration(tap, dataset, now):
    with tap.plan(2, 'пользователь: задана продолжительность паузы'):
        store = await dataset.store()
        user = await dataset.user(store=store)

        _now = now().replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            started_at=_now,
            closes_at=_now + timedelta(hours=4),
            shift_events=[
                {
                    'created': _now,
                    'user_id': user.user_id,
                    'type': 'paused',
                    'detail': {'duration': 100},
                },
            ],
        )

        pause = shift.event_paused()
        tap.ok(pause, 'пауза начата')

        tap.eq(
            shift.pause_ends_at(pause),
            pause.created + timedelta(seconds=100),
            'на продолжительность'
        )


async def test_pause_duration_too_big(tap, dataset):
    with tap.plan(2, 'пользователь: пауза больше смены'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                {
                    'user_id': user.user_id,
                    'type': 'paused',
                    'detail': {'duration': 99999999},
                },
            ],
        )

        pause = shift.event_paused()
        tap.ok(pause, 'пауза начата')

        tap.eq(
            shift.pause_ends_at(pause),
            shift.closes_at,
            'ограничена сменой'
        )


async def test_force_user_duration(tap, dataset):
    with tap.plan(2, 'пользователь: пользовательское продолжение главнее'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                {
                    'user_id': user.user_id,
                    'type': 'paused',
                    'detail': {'duration': 100},
                },
            ],
        )

        pause = shift.event_paused()
        tap.ok(pause, 'пауза начата')

        tap.eq(
            shift.pause_ends_at(pause, max_pause_duration=999999),
            pause.created + timedelta(seconds=100),
            'без продолжительности до конца смены'
        )


async def test_pause_courier(tap, dataset):
    with tap.plan(2, 'курьер: пауза без ограничений'):
        store = await dataset.store()
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                },
            ],
        )

        pause = shift.event_paused()
        tap.ok(pause, 'пауза начата')

        tap.eq(
            shift.pause_ends_at(pause),
            shift.closes_at,
            'без продолжительности до конца смены'
        )
