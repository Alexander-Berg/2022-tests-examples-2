from stall.model.delivery import Delivery


async def test_instance(tap, dataset):
    with tap.plan(6):

        store       = await dataset.store()
        provider    = await dataset.provider()

        delivery = Delivery({
            'store_id': store.store_id,
            'provider_id': provider.provider_id,
            'attr': {'units': 1},
            'car': {'number': 'AA1111B'},
            'driver': {'name': 'Василий'},
        })
        tap.ok(delivery, 'Объект создан')
        tap.eq(delivery.attr['units'], 1, 'units')
        tap.eq(delivery.car['number'], 'AA1111B', 'car.number')
        tap.eq(delivery.driver['name'], 'Василий', 'driver.name')

        tap.ok(await delivery.save(), 'сохранение')
        tap.ok(await delivery.save(), 'обновление')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        store       = await dataset.store()
        provider    = await dataset.provider()
        delivery    = await dataset.delivery(store=store, provider=provider)
        tap.ok(delivery, 'Объект создан')
