# pylint: disable=unused-variable,too-many-locals

from datetime import timedelta, datetime, time
from libstall.timetable import TimeTable, TimeTableItem
from libstall.util import tzone, time2iso_utc


async def test_reserve(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(9, 'Резервирование слота'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])

        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        begin       = now() + timedelta(minutes=15)
        end         = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('slot.gate_slot_id', 'gate_slot_id')
        t.json_is('slot.provider_id', provider.provider_id, 'provider_id')
        t.json_is('slot.delivery_id', delivery.delivery_id, 'delivery_id')
        t.json_is('slot.gate_id', gate.gate_id, 'gate_id')
        t.json_is('slot.begin', time2iso_utc(begin), 'begin')
        t.json_is('slot.end', time2iso_utc(end), 'end')


async def test_exists(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Возможно создать только один слот на поставку'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)
        await dataset.gate_slot(
            gate=gate,
            delivery=delivery,
            begin=now() + timedelta(days=1),
            end=now() + timedelta(days=1, hours=1),
        )

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        begin       = now() + timedelta(minutes=15)
        end         = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_SLOT_ALREADY_RESERVED')


async def test_store_closed(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Лавка отключена'):
        store = await dataset.store(status='closed')
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])

        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_STORE_IS_INACTIVE')


async def test_already_reserved(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Уже занято'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        delivery1 = await dataset.delivery(store=store, provider=provider)
        delivery2 = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)

        slot1 = await dataset.gate_slot(
            delivery=delivery1,
            gate=gate,
            begin=begin,
            end=end,
        )

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery2.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_SLOT_NOT_RESERVED')


async def test_tags_not_suitable(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Теги не совпадают'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer'],
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)
        with await dataset.delivery(
                store=store,
                provider=provider,
                tags=['freezer', 'heavy'],
        ) as delivery:
            await t.post_ok(
                'api_provider_gate_slots_reserve',
                json={
                    'external_id': uuid(),
                    'delivery_id': delivery.delivery_id,
                    'begin': begin,
                    'end': end,
                },
            )
            t.status_is(410, diag=True)
            t.json_is('code', 'ER_NO_SUITABLE_GATE')


async def test_tags_gate_disabled(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Ворота не активны'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer'],
            status='disabled',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)
        with await dataset.delivery(
                store=store,
                provider=provider,
                tags=['freezer'],
        ) as delivery:
            await t.post_ok(
                'api_provider_gate_slots_reserve',
                json={
                    'external_id': uuid(),
                    'delivery_id': delivery.delivery_id,
                    'begin': begin,
                    'end': end,
                },
            )
            t.status_is(410, diag=True)
            t.json_is('code', 'ER_NO_SUITABLE_GATE')


async def test_tags_ok(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(2, 'Теги совпадают'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer', 'heavy'],
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)
        with await dataset.delivery(
                store=store,
                provider=provider,
                tags=['freezer', 'heavy'],
        ) as delivery:
            await t.post_ok(
                'api_provider_gate_slots_reserve',
                json={
                    'external_id': uuid(),
                    'delivery_id': delivery.delivery_id,
                    'begin': begin,
                    'end': end,
                },
            )
            t.status_is(200, diag=True)


async def test_tags_priority(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Приоритет у более специализированных врат'):
        store = await dataset.store()
        gate1 = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer', 'heavy'],
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        gate2 = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer'],
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        gate3 = await dataset.gate(
            store=store,
            title='A1',
            tags=['freezer', 'heavy', 'usual'],
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        begin       = now() + timedelta(minutes=5)
        end         = begin + timedelta(hours=1)
        with await dataset.delivery(
                store=store,
                provider=provider,
                tags=['freezer'],
        ) as delivery:
            await t.post_ok(
                'api_provider_gate_slots_reserve',
                json={
                    'external_id': uuid(),
                    'delivery_id': delivery.delivery_id,
                    'begin': begin,
                    'end': end,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('slot.gate_id', gate2.gate_id, 'Ворота с меньшими тегами')


async def test_window_fail(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(3, 'Только в свободное время'):
        store = await dataset.store(tz='Europe/Moscow')
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '10:00',
                    'end':      '11:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        today = datetime.combine(now(), time(9, 0, 0), tzone('+04:00'))
        begin = today + timedelta(days=1) - timedelta(minutes=2)
        end   = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_SLOT_NOT_RESERVED')


async def test_window(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(14, 'Резервирование слота в свободный промежуток'):
        store = await dataset.store(tz='Europe/Moscow')
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '10:00',
                    'end':      '11:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        tomorrow = datetime.combine(
            now(), time(10, 0, 0), tzone('Europe/Moscow')
        ) + timedelta(days=1)
        begin = tomorrow
        end   = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('slot.gate_slot_id', 'gate_slot_id')
        t.json_is('slot.provider_id', provider.provider_id, 'provider_id')
        t.json_is('slot.delivery_id', delivery.delivery_id, 'delivery_id')
        t.json_is('slot.gate_id', gate.gate_id, 'gate_id')
        t.json_is('slot.begin', time2iso_utc(begin), 'begin')
        t.json_is('slot.end', time2iso_utc(end), 'end')

        tap.note('Повтор')
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': external_id,
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)

        tap.note('Новое на то же время')
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_SLOT_ALREADY_RESERVED')


async def test_beside(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(6, 'Резервирование слоты рядом друг с другом'):
        store = await dataset.store(tz='Europe/Moscow')
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )

        provider = await dataset.provider(stores=[store.store_id])
        delivery1 = await dataset.delivery(store=store, provider=provider)
        delivery2 = await dataset.delivery(store=store, provider=provider)
        delivery3 = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        tomorrow = datetime.combine(
            now(), time(12, 0, 0), tzone('Europe/Moscow')
        ) + timedelta(days=1)

        begin = tomorrow
        end   = begin + timedelta(hours=1)

        external_id = uuid()

        t = await api(user=user)

        tap.note('Один слот')
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'delivery_id': delivery1.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)

        tap.note('Слот сразу после зарезервированного')
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'delivery_id': delivery2.delivery_id,
                'begin': begin + timedelta(hours=1),
                'end': end + timedelta(hours=1),
            },
        )
        t.status_is(200, diag=True)

        tap.note('Слот прям перед зарезервированным')
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'delivery_id': delivery3.delivery_id,
                'begin': begin - timedelta(hours=1),
                'end': end - timedelta(hours=1),
            },
        )
        t.status_is(200, diag=True)


async def test_reserve_0_0(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.provider.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.slot.max_end',      60*60*24*100)

    with tap.plan(9, 'Резервирование слота переходящего в следующий день'):
        store = await dataset.store()
        gate = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type':     'everyday',
                    'begin':    '00:00',
                    'end':      '00:00',
                })
            ])
        )
        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        today   = now()
        begin   = datetime.combine(today, time(23, 45, 0), tzinfo=today.tzinfo)
        end     = begin + timedelta(minutes=30)

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'delivery_id': delivery.delivery_id,
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('slot.gate_slot_id', 'gate_slot_id')
        t.json_is('slot.provider_id', provider.provider_id, 'provider_id')
        t.json_is('slot.delivery_id', delivery.delivery_id, 'delivery_id')
        t.json_is('slot.gate_id', gate.gate_id, 'gate_id')
        t.json_is('slot.begin', time2iso_utc(begin), 'begin')
        t.json_is('slot.end', time2iso_utc(end), 'end')
