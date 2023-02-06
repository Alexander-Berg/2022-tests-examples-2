from stall.model.gate import Gate


async def test_instance(tap, dataset):
    with tap.plan(3):

        store = await dataset.store()

        gate = Gate({
            'title': 'A1',
            'store_id': store.store_id,
            'tags': ['freezer'],
        })
        tap.ok(gate, 'Объект создан')
        tap.ok(await gate.save(), 'сохранение')
        tap.ok(await gate.save(), 'обновление')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        gate = await dataset.gate()
        tap.ok(gate, 'Объект создан')
