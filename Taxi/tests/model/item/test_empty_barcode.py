async def test_item(tap, dataset, uuid):
    with tap.plan(6, 'экземпляр без ШК'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        item = dataset.Item({
            'store_id': store.store_id,
            'external_id': uuid(),
            'type': 'parcel',
            'title': 'посылка',
        })
        tap.ok(not item.item_id, 'id до сохранения не назначен')
        tap.ok(item, 'инстанцирован')
        tap.eq(item.barcode, [], 'ШК нет')
        tap.ok(await item.save(), 'сохранено без ШК')
        tap.ok(item.item_id, 'id назначен')
