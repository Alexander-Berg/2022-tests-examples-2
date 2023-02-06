from asyncpg.exceptions import CheckViolationError

async def test_instance(tap, dataset):
    with tap.plan(8, 'Инстанс создается стеллажа'):
        store = await dataset.store()
        rack_zone = await dataset.rack_zone(store=store)
        rack = dataset.Rack({
            'store_id': store.store_id,
            'company_id': store.company_id,
            'barcode': 'bestbarcodeevar',
            'title': 'best title evar',
            'rack_zone_id': rack_zone.rack_zone_id,
            'rack_zone_type': rack_zone.type,
        })
        tap.ok(rack, 'Стеллаж создан')
        tap.eq(rack.title, 'best title evar', 'Название то')
        tap.eq(rack.status, 'active', 'Статус')
        tap.eq(rack.barcode, 'bestbarcodeevar', 'Баркод тот')
        tap.eq(rack.rack_zone_id, rack_zone.rack_zone_id, 'Зона та')
        tap.eq(rack.rack_id, None, 'ID стеллажа')
        tap.ok(await rack.save(), 'Сохранили в базе')
        tap.ok(rack.rack_id, 'Появился ID стеллажа')


async def test_dataset(tap, dataset):
    with tap.plan(5, 'Датасет что-то делает'):
        rack = await dataset.rack()
        tap.ok(rack, 'Стеллаж есть')
        tap.ok(rack.rack_id, 'ID есть')
        rack_from_db = await dataset.Rack.load(rack.rack_id)
        tap.ok(rack_from_db, 'Достали из базы')
        tap.eq(
            rack_from_db.external_id,
            rack.external_id,
            'Айдишники совпадают'
        )
        tap.eq(
            rack_from_db.rack_id,
            rack.rack_id,
            'И внутренние тоже'
        )


async def test_capacity_check(tap, dataset):
    with tap.plan(2, 'Стеллажу не изковырять емкость'):
        rack = await dataset.rack(
            count=4,
            reserve=3
        )
        rack.capacity = 10
        tap.ok(await rack.save(), 'Успешно выставили емкость')

        rack.capacity = 5
        with tap.raises(CheckViolationError):
            await rack.save()
