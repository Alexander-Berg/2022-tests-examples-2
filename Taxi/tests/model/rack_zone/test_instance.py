async def test_instance(tap, dataset):
    with tap.plan(7, 'Инстанс создается зоны'):
        store = await dataset.store()
        zone = dataset.RackZone({
            'store_id': store.store_id,
            'company_id': store.company_id,
            'barcode': 'bestbarcodeevar',
            'title': 'best title evar',
        })
        tap.ok(zone, 'Зона создана')
        tap.eq(zone.title, 'best title evar', 'Название то')
        tap.eq(zone.status, 'active', 'Статус')
        tap.eq(zone.barcode, 'bestbarcodeevar', 'Баркод тот')
        tap.eq(zone.rack_zone_id, None, 'ID зоны стеллажа')
        tap.ok(await zone.save(), 'Сохранили в базе')
        tap.ok(zone.rack_zone_id, 'Появился ID зоны стеллажа')


async def test_dataset(tap, dataset):
    with tap.plan(5, 'Датасет что-то делает'):
        zone = await dataset.rack_zone()
        tap.ok(zone, 'Зона есть')
        tap.ok(zone.rack_zone_id, 'ID есть')
        zone_from_db = await dataset.RackZone.load(zone.rack_zone_id)
        tap.ok(zone_from_db, 'Достали из базы')
        tap.eq(
            zone_from_db.external_id,
            zone.external_id,
            'Айдишники совпадают'
        )
        tap.eq(
            zone_from_db.rack_zone_id,
            zone.rack_zone_id,
            'И внутренние тоже'
        )
