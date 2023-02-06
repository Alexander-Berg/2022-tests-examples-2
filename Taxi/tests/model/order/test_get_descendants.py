async def test_get_descendants(tap, dataset):
    with tap.plan(4):
        o1 = await dataset.order()
        o2 = await dataset.order(store_id=o1.store_id, parent=[o1.order_id])

        o1_descs = await o1.get_descendants()

        tap.eq(
            {o.order_id for o in o1_descs},
            {o2.order_id},
            'один потомок',
        )

        o3 = await dataset.order(store_id=o2.store_id, parent=[o2.order_id])

        o1_descs = await o1.get_descendants()

        tap.eq(
            {o.order_id for o in o1_descs},
            {o2.order_id, o3.order_id},
            'два потомка',
        )

        o1.parent = [o3.order_id]
        tap.ok(await o1.save(), 'правнука делаем родителем прадедушки')

        o1_descs = await o1.get_descendants()

        tap.eq(
            {o.order_id for o in o1_descs},
            {o2.order_id, o3.order_id},
            'два потомка все равно',
        )


async def test_order_types(tap, dataset):
    with tap.plan(2, 'Проверяем order_types'):
        parent = await dataset.order()

        acceptance_child = await dataset.order(
            store_id=parent.store_id,
            type='acceptance',
            parent=[parent.order_id]
        )

        check_child = await dataset.order(
            store_id=parent.store_id,
            type='check_product_on_shelf',
            parent=[parent.order_id]
        )

        sale_stowage_child = await dataset.order(
            store_id=parent.store_id,
            type='sale_stowage',
            parent=[parent.order_id]
        )

        child_orders = await parent.get_descendants(
            order_types=['acceptance', 'sale_stowage']
        )

        tap.eq(
            {child.order_id for child in child_orders},
            {acceptance_child.order_id, sale_stowage_child.order_id},
            'Два потомка с указанными типами'
        )

        stowage_from_check = await dataset.order(
            store_id=parent.store_id,
            type='sale_stowage',
            parent=[check_child.order_id]
        )

        child_orders = await parent.get_descendants(
            order_types=['acceptance', 'sale_stowage']
        )

        tap.eq(
            {child.order_id for child in child_orders},
            {
                acceptance_child.order_id,
                sale_stowage_child.order_id,
                stowage_from_check.order_id
            },
            'Три потомка с указанными типами'
        )
