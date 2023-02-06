# pylint: disable=unused-variable,too-many-locals,too-many-statements

from datetime import datetime, time, timedelta
from libstall.timetable import TimeTable, TimeTableItem


async def test_list(api, dataset, now, tap, cfg):
    cfg.set('business.gate_slot.provider.list.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.list.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.list.max_end',      60*60*24*100)

    with tap.plan(23, 'Список слотов склада'):
        store = await dataset.store()

        provider1 = await dataset.provider(stores=[store.store_id])
        provider2 = await dataset.provider(stores=[store.store_id])

        gate1 = await dataset.gate(
            store=store,
            title='A1',
            timetable=TimeTable([
                TimeTableItem({
                    'type': 'everyday',
                    'begin': '08:00',
                    'end': '20:00',
                })
            ])
        )
        gate2 = await dataset.gate(
            store=store,
            title='A2',
            timetable=TimeTable([
                TimeTableItem({
                    'type': 'everyday',
                    'begin': '00:00',
                    'end': '00:00',
                })
            ])
        )

        d_past = await dataset.delivery(store=store, provider=provider1)
        d_future = await dataset.delivery(store=store, provider=provider1)

        delivery1 = await dataset.delivery(store=store, provider=provider1)
        delivery2 = await dataset.delivery(store=store, provider=provider2)
        delivery3 = await dataset.delivery(store=store, provider=provider1)

        delivery = await dataset.delivery(store=store, provider=provider1)

        tomorrow   = now() + timedelta(days=1)
        begin_time = datetime.combine(tomorrow, time(12, 0, 0), tomorrow.tzinfo)
        end_time   = begin_time + timedelta(hours=1)

        slot_past = await dataset.gate_slot(
            store=store,
            gate=gate1,
            delivery=d_past,
            begin=begin_time - timedelta(days=10),
            end=end_time - timedelta(days=10),
        )
        slot1 = await dataset.gate_slot(
            store=store,
            gate=gate1,
            delivery=delivery1,
            begin=begin_time + timedelta(hours=1),
            end=end_time + timedelta(hours=1),
        )
        slot2 = await dataset.gate_slot(
            store=store,
            gate=gate2,
            delivery=delivery2,
            begin=begin_time + timedelta(hours=1),
            end=end_time + timedelta(hours=1),
        )
        slot3 = await dataset.gate_slot(
            store=store,
            gate=gate2,
            delivery=delivery3,
            begin=begin_time + timedelta(hours=2),
            end=end_time + timedelta(hours=2),
        )
        slot_future = await dataset.gate_slot(
            store=store,
            gate=gate2,
            delivery=d_future,
            begin=begin_time + timedelta(days=10),
            end=end_time + timedelta(days=10),
        )

        user = await dataset.user(
            provider=provider1,
            store_id=None,
            role='provider',
        )

        today       = begin_time.replace(hour=0, minute=0, second=0)
        yesterday_begin = today - timedelta(days=1)
        tomorrow_end  = today + timedelta(days=2)

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_schedule',
            json={
                'delivery_id': delivery.delivery_id,
                'begin': yesterday_begin,
                'end': tomorrow_end,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        tap.note('Gate 1')
        t.json_is('schedule.0.gate_id', gate1.gate_id, 'gate_id')
        t.json_is('schedule.0.title', gate1.title, 'title')
        t.json_is('schedule.0.slots.0.type', 'offhours', 'Склад не работает')
        t.json_is('schedule.0.slots.1.type', 'offhours', 'Склад не работает')
        t.json_is('schedule.0.slots.2.type', 'offhours', 'Склад не работает')
        t.json_is('schedule.0.slots.3.type', 'delivery', 'Доставка')
        t.json_is('schedule.0.slots.4.type', 'offhours', 'Склад не работает')
        t.json_is('schedule.0.slots.5.type', 'offhours', 'Склад не работает')
        t.json_is('schedule.0.slots.6.type', 'offhours', 'Склад не работает')
        t.json_hasnt('schedule.0.slots.7.type', 'Все слоты')

        tap.note('Gate 2')
        t.json_is('schedule.1.gate_id', gate2.gate_id, 'gate_id')
        t.json_is('schedule.1.title', gate2.title, 'title')
        t.json_is('schedule.1.slots.0.type', 'delivery', 'Доставка')
        t.json_is(
            'schedule.1.slots.0.provider_id',
            None,
            'Принадлежность очищена'
        )
        t.json_is(
            'schedule.1.slots.0.delivery_id',
            None,
            'Принадлежность очищена'
        )
        t.json_is('schedule.1.slots.1.type', 'delivery', 'Доставка')
        t.json_is(
            'schedule.1.slots.1.provider_id',
            slot3.provider_id,
            'Принадлежность'
        )
        t.json_is(
            'schedule.1.slots.1.delivery_id',
            slot3.delivery_id,
            'Принадлежность'
        )
        t.json_hasnt('schedule.1.slots.2.type', 'Все слоты')

        tap.note('Завершение')
        t.json_hasnt('gates.2', 'Все ворота')


async def test_store_closed(api, dataset, now, tap, cfg):
    cfg.set('business.gate_slot.provider.list.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.list.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.list.max_end',      60*60*24*100)

    with tap.plan(4, 'Склад отключен и по нему не возвращаем информацию'):
        store = await dataset.store(status='closed')
        gate  = await dataset.gate(store=store, title='A1')

        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_schedule',
            json={
                'delivery_id': delivery.delivery_id,
                'begin': now() - timedelta(days=1),
                'end': now() + timedelta(days=1),
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('schedule', [], 'Ворот нет')


async def test_no_gates(api, dataset, now, tap, cfg):
    cfg.set('business.gate_slot.provider.list.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.provider.list.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.provider.list.max_end',      60*60*24*100)

    with tap.plan(4, 'Нет подходящих врат'):
        store = await dataset.store()
        gate  = await dataset.gate(store=store, title='A1')

        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(
            store=store,
            provider=provider,
            tags=['freezer'],
        )

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_schedule',
            json={
                'delivery_id': delivery.delivery_id,
                'begin': now() - timedelta(days=1),
                'end': now() + timedelta(days=1),
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('schedule', [], 'Ворот нет')
