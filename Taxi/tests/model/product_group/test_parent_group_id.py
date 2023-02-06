from stall.model.product_group import ProductGroup


async def test_self_ref(tap, dataset):
    with tap.plan(1):
        group = await dataset.product_group()
        is_valid = await ProductGroup.is_valid_parent_group_id(
            group.group_id, group.group_id
        )
        tap.is_ok(is_valid, False, 'parent group self ref')


async def test_not_found(tap, uuid):
    with tap.plan(1):
        is_valid = await ProductGroup.is_valid_parent_group_id(uuid(), uuid())
        tap.is_ok(is_valid, False, 'parent group not found')


async def test_circular_ref(tap, dataset):
    with tap.plan(5):
        group_a = await dataset.product_group()
        tap.is_ok(group_a.parent_group_id, None, 'no parent group')

        group_b = await dataset.product_group(parent_group_id=group_a.group_id)
        tap.eq_ok(
            group_b.parent_group_id,
            group_a.group_id,
            'with parent group a',
        )

        group_c = await dataset.product_group(parent_group_id=group_b.group_id)
        tap.eq_ok(
            group_c.parent_group_id,
            group_b.group_id,
            'with parent group b',
        )

        is_valid = await ProductGroup.is_valid_parent_group_id(
            group_b.group_id, group_a.group_id,
        )
        tap.is_ok(is_valid, False, 'circular ref: a -> b -> a')

        is_valid = await ProductGroup.is_valid_parent_group_id(
            group_c.group_id, group_a.group_id,
        )
        tap.is_ok(is_valid, False, 'circular ref: a -> b -> c -> a')


async def test_resolve_tree(tap, dataset):
    with tap.plan(9):
        group_a = await dataset.product_group()
        group_b = await dataset.product_group(parent_group_id=group_a.group_id)
        group_c = await dataset.product_group(parent_group_id=group_b.group_id)

        groups = await ProductGroup.resolve_tree(group_c.group_id)

        tap.eq_ok(len(groups), 3, 'все на месте')
        tap.eq_ok(groups[0].group_id, group_c.group_id, 'внук')
        tap.eq_ok(groups[1].group_id, group_b.group_id, 'сын')
        tap.eq_ok(groups[2].group_id, group_a.group_id, 'отец')

        groups = await ProductGroup.resolve_tree(group_b.group_id)
        tap.eq_ok(len(groups), 2, 'все на месте')
        tap.eq_ok(groups[0].group_id, group_b.group_id, 'сын')
        tap.eq_ok(groups[1].group_id, group_a.group_id, 'отец')

        groups = await ProductGroup.resolve_tree(group_a.group_id)
        tap.eq_ok(len(groups), 1, 'все на месте')
        tap.eq_ok(groups[0].group_id, group_a.group_id, 'отец')
