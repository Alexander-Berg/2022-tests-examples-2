
async def test_dataset(tap, dataset):
    with tap.plan(8):
        store = await dataset.store()
        courier_shift = await dataset.courier_shift(store=store)
        courier_shift_by_id = await dataset.courier_shift(
            store_id=store.store_id
        )
        tap.ok(courier_shift, 'Объект создан')
        tap.eq(courier_shift.company_id, store.company_id, 'company_id')
        tap.eq(courier_shift.store_id, store.store_id, 'store_id')
        tap.eq(courier_shift_by_id.store_id, store.store_id, 'store_id by id')
        tap.eq(courier_shift.status, 'request', 'status')

        tap.ok(await courier_shift.save(), 'пересохранение')

        courier_shift.shift_events = [
            dataset.CourierShiftEvent({
                'type': 'accepted',
            }),
            dataset.CourierShiftEvent({
                'type': 'started',
            })
        ]

        tap.ok(await courier_shift.save(), 'пересохранение')
        tap.eq(len(courier_shift.shift_events), 2, 'события сохранены')


async def test_shift_events(tap, dataset, uuid):
    with tap.plan(19, 'shift_events всегда добавляется'):
        store = await dataset.store()

        with await dataset.courier_shift(store=store) as shift:
            tap.eq(shift.shift_events, [], 'события пусты')

        with await shift.save() as shift:
            tap.eq(shift.shift_events, [], 'события все еще пусты')

        id1 = uuid()
        id2 = uuid()

        # Сохраняем события
        with shift:
            shift.shift_events = [
                dataset.CourierShiftEvent({
                    'shift_event_id': id1,
                    'type': 'change',
                }),
                dataset.CourierShiftEvent({
                    'shift_event_id': id2,
                    'type': 'accepted',
                }),
            ]

            tap.ok(await shift.save(), 'смена сохранена')
            tap.eq(len(shift.shift_events), 2, 'события сохранены')

        # Пересохраняем
        with shift:
            shift.shift_events = [
                dataset.CourierShiftEvent({
                    'shift_event_id': id1,
                    'type': 'paused',
                }),
                dataset.CourierShiftEvent({
                    'shift_event_id': id2,
                    'type': 'paused',
                }),
            ]

            tap.ok(await shift.save(), 'смена сохранена')
            tap.eq(len(shift.shift_events), 2, 'события остались')

            with shift.shift_events[0] as event:
                tap.eq(event.shift_event_id, id1, 'Событие 1')
                tap.eq(event.type, 'change', 'Событие не менялось')

            with shift.shift_events[1] as event:
                tap.eq(event.shift_event_id, id2, 'Событие 2')
                tap.eq(event.type, 'accepted', 'Событие не менялось')

        id3 = uuid()

        # Смешанное сохранение
        with shift:
            shift.shift_events = [
                dataset.CourierShiftEvent({
                    'shift_event_id': id2,
                    'type': 'paused',
                }),
                dataset.CourierShiftEvent({
                    'shift_event_id': id3,
                    'type': 'rejected',
                }),
            ]

            tap.ok(await shift.save(), 'смена сохранена')
            tap.eq(len(shift.shift_events), 3, 'события созранены')

            with shift.shift_events[0] as event:
                tap.eq(event.shift_event_id, id1, 'Событие 1')
                tap.eq(event.type, 'change', 'Событие не менялось')

            with shift.shift_events[1] as event:
                tap.eq(event.shift_event_id, id2, 'Событие 2')
                tap.eq(event.type, 'accepted', 'Событие не менялось')

            with shift.shift_events[2] as event:
                tap.eq(event.shift_event_id, id3, 'Событие 3')
                tap.eq(event.type, 'rejected', 'Событие добавлено')

        with await shift.save() as shift:
            tap.eq(len(shift.shift_events), 3, 'события не изменились')


async def test_get_event_pair(tap, dataset):
    with tap.plan(15):
        store = await dataset.store()

        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                dataset.CourierShiftEvent({'type': 'started'}),
                dataset.CourierShiftEvent({'type': 'stopped'})
            ]
        )
        tap.ok(shift, 'Объект создан')

        tap.ok(await shift.save(), 'пересохранение')
        tap.eq(len(shift.shift_events), 2, 'события сохранены')

        # наличие сразу обоих событий
        e_1, e_2 = shift.get_event_pair('started')
        tap.eq(e_1.type, 'started', 'событие старт')
        tap.eq(e_2.type, 'stopped', 'событие стоп')

        # отсутствие обоих событий
        e_1, e_2 = shift.get_event_pair('paused')
        tap.is_ok(e_1, None, 'событие начало паузы')
        tap.is_ok(e_2, None, 'событие конец паузы')

        # наличие только первого события
        shift.shift_events = [
            dataset.CourierShiftEvent({'type': 'paused'})
        ]
        tap.ok(await shift.save(), 'пересохранение')
        tap.eq(len(shift.shift_events), 3, 'события сохранены')
        e_1, e_2 = shift.get_event_pair('paused')
        tap.eq(e_1.type, 'paused', 'событие начало паузы')
        tap.is_ok(e_2, None, 'событие конец паузы')

        # несколько одинаковых пар событий, но берется только последняя пара
        e_pause = dataset.CourierShiftEvent({'type': 'paused'})
        e_unpaused = dataset.CourierShiftEvent({'type': 'unpaused'})
        shift.shift_events = [
            dataset.CourierShiftEvent({'type': 'paused'}),
            dataset.CourierShiftEvent({'type': 'unpaused'}),
            dataset.CourierShiftEvent({'type': 'paused'}),
            dataset.CourierShiftEvent({'type': 'unpaused'}),
            dataset.CourierShiftEvent({'type': 'paused'}),
            dataset.CourierShiftEvent({'type': 'unpaused'}),
            e_pause,
            e_unpaused
        ]
        e_1, e_2 = shift.get_event_pair('paused')
        tap.eq(e_1.type, e_pause.type, 'событие paused')
        tap.eq(e_1.shift_event_id, e_pause.shift_event_id, 'событие paused')
        tap.eq(e_2.type, e_unpaused.type, 'событие unpaused')
        tap.eq(e_2.shift_event_id, e_unpaused.shift_event_id, 'соб. unpaused')


async def test_push_events(tap, dataset):
    with tap.plan(11):
        store = await dataset.store()

        shift = await dataset.courier_shift(store=store)
        tap.ok(shift, 'Объект создан')
        events_cache = await dataset.EventCache.list(
            tbl='courier_shifts',
            pk=shift.courier_shift_id,
            by='object',
            db={'shard': shift.shardno},
            full=True
        )
        tap.eq_ok(len(events_cache.list), 1, 'Создана 1 обёртка для ивентов')

        with events_cache.list[-1] as event_cache:
            tap.eq_ok(event_cache.tbl, 'courier_shifts', 'tbl')
            tap.eq_ok(event_cache.pk, shift.courier_shift_id, 'pk')
            tap.eq_ok(len(event_cache.events), 1, 'Создан 1 ивент')

            event = event_cache.events[0]
            tap.eq_ok(event['type'], 'lp', 'events.0.type')
            tap.eq_ok(
                event['key'],
                ['courier_shift', 'store', shift.store_id],
                'events.0.key'
            )
            tap.ok(event['data'], 'events.data')
            tap.eq_ok(event['data']['courier_shift_id'],
                      shift.courier_shift_id,
                      'В sql подставляется сохранённый id')

        tap.note('При пересохранении не генерируются новые ивенты')

        tap.ok(await shift.save(), 'Пересохранение')
        events_cache = await dataset.EventCache.list(
            tbl='courier_shifts',
            pk=shift.courier_shift_id,
            by='object',
            db={'shard': shift.shardno},
            full=True
        )
        tap.eq_ok(len(events_cache.list), 1, 'Всё ещё 1 обёртка для ивентов')
