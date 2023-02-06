async def test_item(tap, dataset, uuid):
    with tap.plan(3, 'Тесты инстанцирования/сохранения'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        item = dataset.Item({
            'store_id': store.store_id,
            'external_id': uuid(),

            'title': 'Тестовый экземпляр',
            'type': 'parcel',

        })
        tap.ok(item, 'инстанцирован')
        tap.ok(await item.save(), 'сохранён')


async def test_dataset(tap, dataset, uuid):
    with tap.plan(6, 'создание через dataset'):
        tap.ok(await dataset.item(), 'Создан через dataset')
        tap.ok(await dataset.item(type='parcel'), 'Создан через dataset')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store, barcode=[uuid()])
        tap.eq(item.store_id, store.store_id, 'создан на складе')

        bb = await dataset.Item.list_by_barcode(item.store_id, item.barcode)
        tap.eq(len(bb), 1, 'выбрано по ШК')
        tap.eq(bb[0].item_id, item.item_id, 'тот самый')

