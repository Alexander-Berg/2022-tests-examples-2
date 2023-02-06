async def test_items(tap, api, dataset):
    with tap.plan(8, 'Запрос за экземплярами'):

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role='executer',
                                  store=store,
                                  force_role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)


        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')


        await t.post_ok('api_tsd_items', json={'ids': [item.item_id]})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')

        t.json_is('items.0.item_id', item.item_id)
        t.json_is('items.0.external_id', item.external_id)
