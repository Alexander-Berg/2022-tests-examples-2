from stall.model.zone import Zone


async def test_dataset(tap, dataset):
    with tap.plan(8):
        store = await dataset.store()
        zone = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id)
            ],
            sort=(),
        )
        tap.ok(len(zone.list), 1,  'Объект создан')
        zone = zone.list[0]
        tap.eq(zone.company_id, store.company_id, 'company_id')
        tap.eq(zone.store_id, store.store_id, 'store_id')
        tap.eq(zone.status, 'active', 'status')

        zone = await dataset.zone(store=store, status='template')

        tap.eq(zone.company_id, store.company_id, 'company_id')
        tap.eq(zone.store_id, store.store_id, 'store_id')
        tap.eq(zone.status, 'template', 'status')

        tap.ok(await zone.save(), 'пересохранение')
