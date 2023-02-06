# pylint: disable=unused-variable,too-many-locals

from datetime import timedelta
from libstall.timetable import TimeTable, TimeTableItem
from libstall.util import time2iso_utc


async def test_reserve(api, dataset, now, tap, uuid, cfg):
    cfg.set('business.gate_slot.admin.slot.max_lingth',   60*60*24*100)
    cfg.set('business.gate_slot.admin.slot.min_begin',   -60*60*24*100)
    cfg.set('business.gate_slot.admin.slot.max_end',      60*60*24*100)

    with tap.plan(10, 'Резервирование слота'):
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

        begin       = now() + timedelta(minutes=15)
        end         = begin + timedelta(hours=1)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_gate_slots_reserve',
            json={
                'external_id': uuid(),
                'gate_id': gate.gate_id,
                'type': 'disabled',
                'begin': begin,
                'end': end,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('slot.gate_slot_id', 'gate_slot_id')
        t.json_is('slot.provider_id', None, 'provider_id')
        t.json_is('slot.delivery_id', None, 'delivery_id')
        t.json_is('slot.gate_id', gate.gate_id, 'gate_id')
        t.json_is('slot.begin', time2iso_utc(begin), 'begin')
        t.json_is('slot.end', time2iso_utc(end), 'end')
        t.json_is('slot.type', 'disabled', 'type')
