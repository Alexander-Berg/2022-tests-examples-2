# pylint: disable=unused-variable,too-many-locals

from datetime import timedelta
from libstall.timetable import TimeTable, TimeTableItem


async def test_unreserve(api, dataset, now, tap):
    with tap.plan(4, 'Разрезервирование слота'):
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
        user = await dataset.user(store=store)
        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        begin       = now() + timedelta(minutes=15)
        end         = begin + timedelta(hours=1)

        slot = await dataset.gate_slot(
            store=store,
            gate=gate,
            delivery=delivery,
            begin=begin,
            end=end,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_gate_slots_unreserve',
            json={'gate_slot_id': slot.gate_slot_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')

        tap.ok(
            not await dataset.GateSlot.load(slot.gate_slot_id),
            'Слот удален',
        )


async def test_used(api, dataset, now, tap):
    with tap.plan(4, 'Слоты кторые в прошлом удалять нельзя'):
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
        user = await dataset.user(store=store)
        provider = await dataset.provider(stores=[store.store_id])
        delivery = await dataset.delivery(store=store, provider=provider)

        begin       = now() - timedelta(minutes=15)
        end         = begin + timedelta(hours=1)

        slot = await dataset.gate_slot(
            store=store,
            gate=gate,
            delivery=delivery,
            begin=begin,
            end=end,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_gate_slots_unreserve',
            json={'gate_slot_id': slot.gate_slot_id},
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_SLOT_ALREADY_USED')

        tap.ok(
            await dataset.GateSlot.load(slot.gate_slot_id),
            'Слот не удален',
        )
