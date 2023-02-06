from datetime import timedelta


async def test_simple(api, dataset, tap):
    with tap.plan(5, 'У курьера нет смен'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        courier = await dataset.courier(cluster=cluster)

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_support_info',
            form={'courier_id': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('courier_id', courier.external_id)
        t.json_hasnt('current_slot_shift_id')
        t.json_hasnt('last_slot_shift_id')


async def test_active_shift(api, dataset, tap, now, time2iso):
    with tap.plan(13, 'Получаем текущую смену курьера и активную паузу'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)
        real_start = _now - timedelta(hours=1, minutes=45)
        shift = await dataset.courier_shift(
            status='processing',
            courier=courier,
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
                'created': real_start,
            }, {
                'courier_id': courier.courier_id,
                'type': 'paused',
                'location': {'lon': 33, 'lat': 55},
                'created': _now - timedelta(minutes=10),
            }],
        )

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_support_info',
            form={'courier_id': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('courier_id', courier.external_id)
        t.json_is('current_slot_shift_id', shift.courier_shift_id)
        t.json_is('current_slot_started_at', time2iso(shift.started_at))
        t.json_is('current_slot_closes_at', time2iso(shift.closes_at))
        t.json_is('current_slot_real_started_at', time2iso(real_start))
        t.json_hasnt('current_slot_real_closes_at')
        t.json_is('current_slot_status', 'processing')
        t.json_is('current_slot_store_id', shift.store_id)
        t.json_is('current_slot_delivery_type', shift.delivery_type)
        t.json_is('current_slot_active_pause', True)
        t.json_hasnt('last_slot_shift_id')


async def test_last_shift(api, dataset, tap, now, time2iso):
    with tap.plan(12, 'Получаем последнюю смену курьера'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)
        real_start = _now - timedelta(hours=3, minutes=45)
        real_stop = _now - timedelta(hours=2, minutes=15)
        shift = await dataset.courier_shift(
            status='complete',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=2),
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
                'created': real_start,
            }, {
                'courier_id': courier.courier_id,
                'type': 'stopped',
                'created': real_stop,
            }],
        )

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_support_info',
            form={'courier_id': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('courier_id', courier.external_id)
        t.json_hasnt('current_slot_shift_id')
        t.json_is('last_slot_shift_id', shift.courier_shift_id)
        t.json_is('last_slot_started_at', time2iso(shift.started_at))
        t.json_is('last_slot_closes_at', time2iso(shift.closes_at))
        t.json_is('last_slot_real_started_at', time2iso(real_start))
        t.json_is('last_slot_real_closes_at', time2iso(real_stop))
        t.json_is('last_slot_status', 'complete')
        t.json_is('last_slot_store_id', shift.store_id)
        t.json_is('last_slot_delivery_type', shift.delivery_type)


async def test_complex(api, dataset, tap, now, time2iso):
    with tap.plan(20, 'Закрытые, активная и запланированная смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        courier = await dataset.courier(cluster=cluster)
        _now = now().replace(microsecond=0)

        # Прошедшие слоты

        await dataset.courier_shift(
            status='complete',
            courier=courier,
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(hours=4),
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
                'created': _now - timedelta(hours=5, minutes=45),
            }, {
                'courier_id': courier.courier_id,
                'type': 'stopped',
                'created': _now - timedelta(hours=4, minutes=15),
            }],
        )

        last_real_start = _now - timedelta(hours=3, minutes=45)
        last_real_stop = _now - timedelta(hours=2, minutes=15)
        shift_last = await dataset.courier_shift(
            status='leave',
            courier=courier,
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=2),
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
                'created': last_real_start,
            }, {
                'courier_id': courier.courier_id,
                'type': 'stopped',
                'created': last_real_stop,
            }],
        )

        # Текущий слот
        current_real_start = _now - timedelta(hours=1, minutes=45)
        shift_current = await dataset.courier_shift(
            status='processing',
            courier=courier,
            started_at=_now - timedelta(hours=2),
            closes_at=_now + timedelta(hours=2),
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
                'created': current_real_start,
            }],
        )

        # Будущий слот
        await dataset.courier_shift(
            status='waiting',
            courier=courier,
            started_at=_now + timedelta(hours=2),
            closes_at=_now + timedelta(hours=6),
        )

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_support_info',
            form={'courier_id': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('courier_id', courier.external_id)
        t.json_is('current_slot_shift_id', shift_current.courier_shift_id)
        t.json_is('current_slot_started_at', time2iso(shift_current.started_at))
        t.json_is('current_slot_closes_at', time2iso(shift_current.closes_at))
        t.json_is('current_slot_real_started_at', time2iso(current_real_start))
        t.json_hasnt('current_slot_real_closes_at')
        t.json_is('current_slot_status', 'processing')
        t.json_is('current_slot_store_id', shift_current.store_id)
        t.json_is('current_slot_delivery_type', shift_current.delivery_type)
        t.json_is('current_slot_active_pause', False)
        t.json_is('last_slot_shift_id', shift_last.courier_shift_id)
        t.json_is('last_slot_started_at', time2iso(shift_last.started_at))
        t.json_is('last_slot_closes_at', time2iso(shift_last.closes_at))
        t.json_is('last_slot_real_started_at', time2iso(last_real_start))
        t.json_is('last_slot_real_closes_at', time2iso(last_real_stop))
        t.json_is('last_slot_status', 'leave')
        t.json_is('last_slot_store_id', shift_last.store_id)
        t.json_is('last_slot_delivery_type', shift_last.delivery_type)
