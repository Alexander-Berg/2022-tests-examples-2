from stall.model.provider import Provider


async def test_instance(tap, uuid):
    with tap.plan(3):
        provider = Provider({
            'title': f'Поставщик {uuid()}',
            'cluster': 'Москва',
            'tags': ['freezer'],
        })
        tap.ok(provider, 'Объект создан')
        tap.ok(await provider.save(), 'сохранение')
        tap.ok(await provider.save(), 'обновление')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        provider = await dataset.provider()
        tap.ok(provider, 'Объект создан')
