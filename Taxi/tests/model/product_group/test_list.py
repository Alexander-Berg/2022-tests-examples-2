from stall.model.product_group import ProductGroup


async def test_list_by_ids(tap, dataset, uuid):
    with tap.plan(2):
        cursor = await ProductGroup.list(by='full', ids=[uuid()])
        tap.eq_ok(cursor.list, [], 'no groups')

        group_ids = []
        for _ in range(5):
            group = await dataset.product_group()
            group_ids.append(group.group_id)

        cursor = await ProductGroup.list(by='full', ids=group_ids)
        tap.eq_ok(
            {i.group_id for i in cursor.list},
            set(group_ids),
            'all groups',
        )


