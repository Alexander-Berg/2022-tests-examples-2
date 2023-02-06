async def test_create_menu(tap, dataset):
    with tap.plan(12, 'Манипуляции с меню'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        menu = await dataset.StoreStock.kitchen_menu(store)
        tap.eq(menu, {}, 'меню пока нет')


        p1, p2 = await dataset.product(), await dataset.product()
        tap.ok(p1, 'товар 1 создан')
        tap.ok(p2, 'товар 2 создан')

        records = await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                p1.product_id: 10,
            }
        )
        tap.ok(records, 'меню создано')

        menu = await dataset.StoreStock.kitchen_menu(store, full=False)
        tap.eq(menu, {p1.product_id: 10}, 'Меню вычитано')

        records = await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                p1.product_id: 10,
            })
        tap.eq(records, [], 'нет обновления при повторе')


        records = await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                p1.product_id: 10,
                p2.product_id: 110,
            })
        tap.eq(len(records), 1, 'одна запись ещё добавилась')

        records = await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                p2.product_id: 10,
            })
        tap.eq(len(records), 2, 'Две записи изменилось')

        menu = await dataset.StoreStock.kitchen_menu(store, full=False)
        tap.eq(menu, {p2.product_id: 10}, 'Меню вычитано')

        records = await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                p1.product_id: 10,
            })
        tap.eq(len(records), 2, 'Две записи изменилось')

        menu = await dataset.StoreStock.kitchen_menu(store, full=False)
        tap.eq(menu, {p1.product_id: 10}, 'Меню вычитано')
