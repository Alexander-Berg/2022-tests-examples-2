import libstall.model.storable.exception

async def test_order_id(tap, dataset):
    with tap.plan(8, 'работа с lsn при сохранении'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        order = await dataset.order(
            store=store,
            required=[{'product_id': product.product_id, 'count': 11}],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.order_id, None, 'пока ордер не назначен')

        with tap.raises(libstall.model.storable.exception.EmptyRowsetError,
                        'Выбрасывает исключение при фильтре по lsn'):
            await shelf.save(
                conditions=(
                    ('lsn', shelf.lsn + 10),
                )
            )

        shelf.order_id = order.order_id
        tap.ok(
            await shelf.save(
                conditions=(
                    ('lsn', shelf.lsn),
                )
            ),
            'сохранено'
        )
        tap.ok(shelf.order_id, 'order_id установлен')
