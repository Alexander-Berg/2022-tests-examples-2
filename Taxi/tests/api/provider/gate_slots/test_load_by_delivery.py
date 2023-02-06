# pylint: disable=unused-variable,too-many-locals

from datetime import timedelta


async def test_slots_by_delivery(api, dataset, now, tap):
    with tap.plan(10, 'Список слотов доставок'):
        store = await dataset.store()

        provider1 = await dataset.provider(stores=[store.store_id])

        gate1 = await dataset.gate(store=store, title='A1')
        gate2 = await dataset.gate(store=store, title='A2')

        delivery1 = await dataset.delivery(store=store, provider=provider1)
        delivery2 = await dataset.delivery(store=store, provider=provider1)

        slot1 = await dataset.gate_slot(
            gate=gate1,
            delivery=delivery1,
            begin=now() - timedelta(days=1),
            end=now(),
        )
        slot2 = await dataset.gate_slot(
            gate=gate2,
            delivery=delivery2,
            begin=now() + timedelta(days=2),
            end=now() + timedelta(days=3),
        )

        user = await dataset.user(
            provider=provider1,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_gate_slots_load_by_delivery',
            json={
                'delivery_id': [delivery1.delivery_id, delivery2.delivery_id],
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('slots.0.gate_slot_id', slot1.gate_slot_id, '1')
        t.json_is('slots.0.provider_id', slot1.provider_id, 'Принадлежность')
        t.json_is('slots.0.delivery_id', slot1.delivery_id, 'Принадлежность')
        t.json_is('slots.1.gate_slot_id', slot2.gate_slot_id, '1')
        t.json_is('slots.1.provider_id', slot2.provider_id, 'Принадлежность')
        t.json_is('slots.1.delivery_id', slot2.delivery_id, 'Принадлежность')
        t.json_hasnt('slots.2', 'только указанные')
