from scripts.dev.clean_db_phones import clean_phones


async def test_all(tap, dataset, uuid):
    with tap.plan(9, 'зачистка телефона кура в заказе'):
        store = await dataset.store()

        data = [
            dict(courier=None, type='order'),
            dict(courier={'icq': '300'}, type='order'),
            dict(courier={'phone': None}, type='order'),
            dict(courier={'phone': '+301', 'a': 'b'}, type='hand_move'),
            dict(courier={'phone': '+301', 'a': 'b'}, type='order'),
        ]

        for o in data:
            order = await dataset.order(
                order_id=dataset.Order.shard_module.eid_for_shard(0),
                store_id=store.store_id,
                **o,
            )

        # последний
        tap.eq(order.type, 'order', 'клиентский заказ')
        tap.ok(order.courier.phone, 'есть телефон')

        orders = (
            await dataset.Order.list(
                by='full',
                conditions=('store_id', store.store_id),
            )
        ).list
        tap.eq(len(orders), 5, 'всего 5')

        stash_name = uuid()

        count, updated_count = await clean_phones(
            stash_name, 0, store_id=store.store_id
        )
        tap.eq(count, 4, '4 ордера с нужным типом')
        tap.eq(updated_count, 1, 'снесли телефон у одного')

        count, updated_count = await clean_phones(
            stash_name, 0, store_id=store.store_id
        )
        tap.eq(count + updated_count, 5, 'ничего не изменилось')

        stash = await dataset.Stash.load(stash_name, by='name')
        tap.eq(stash.value['serial'], order.serial, 'тот самый serial')

        tap.eq(order.lsn, (await order.reload()).lsn, 'lsn не изменился')
        tap.ok(order.courier.phone is None, 'телефона нет')
