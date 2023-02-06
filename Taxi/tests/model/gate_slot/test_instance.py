from datetime import timedelta
from stall.model.gate_slot import GateSlot


async def test_instance(tap, now, dataset):
    with tap.plan(3):

        store       = await dataset.store()
        gate        = await dataset.gate(store=store)
        provider    = await dataset.provider()

        begin = now() + timedelta(hours=1)

        slot = GateSlot({
            'gate_id': gate.gate_id,
            'store_id': store.store_id,
            'provider_id': provider.provider_id,
            'type': 'delivery',
            'begin': begin,
            'end': begin + timedelta(hours=1),
        })
        tap.ok(slot, 'Объект создан')
        tap.ok(await slot.save(), 'сохранение')
        tap.ok(await slot.save(), 'обновление')


async def test_dataset(tap, now, dataset):
    with tap.plan(1):

        gate        = await dataset.gate()
        provider    = await dataset.provider()
        begin       = now() + timedelta(hours=1)

        slot = await dataset.gate_slot(
            gate=gate,
            provider=provider,
            begin=begin,
            end=begin + timedelta(hours=1),
        )
        tap.ok(slot, 'Объект создан')
