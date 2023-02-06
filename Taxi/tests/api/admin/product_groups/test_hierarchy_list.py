async def test_hierarchy_list(tap, dataset, api):
    with tap.plan(8, 'тестим новенький list для групп'):
        parent = await dataset.product_group(order=1337)

        t = await api(role='admin')
        await t.post_ok('api_admin_product_groups_hierarchy_list', json={})
        t.status_is(200)
        t.json_has('product_groups.0', 'есть группа')

        got_parent = [
            g
            for g in t.res['json']['product_groups']
            if g['product_group']['group_id'] == parent.group_id
        ][0]

        tap.eq(got_parent['has_child'], False, 'нет детей')

        await dataset.product_group(parent_group_id=parent.group_id)
        await t.post_ok('api_admin_product_groups_hierarchy_list', json={})
        t.status_is(200)
        t.json_has('product_groups.0', 'есть группа')

        got_parent = [
            g
            for g in t.res['json']['product_groups']
            if g['product_group']['group_id'] == parent.group_id
        ][0]

        tap.eq(got_parent['has_child'], True, 'а теперь есть ребенок')


async def test_many_children(tap, dataset, api):
    with tap.plan(41, 'тестим сложные деревья'):
        parent1 = await dataset.product_group()
        parent2 = await dataset.product_group()

        children1 = [
            await dataset.product_group(parent_group_id=parent1.group_id)
            for _ in range(3)
        ]
        children2 = [
            await dataset.product_group(parent_group_id=parent2.group_id)
            for _ in range(2)
        ]

        for g in children1 + children2:
            await dataset.product_group(parent_group_id=g.group_id)

        t = await api(role='admin')
        await t.post_ok('api_admin_product_groups_hierarchy_list', json={})
        t.status_is(200)
        t.json_has('product_groups', 'есть группы')

        got_parents = [
            g
            for g in t.res['json']['product_groups']
            if g['product_group']['group_id'] in {parent1.group_id,
                                                  parent2.group_id}
        ]

        tap.eq(len(got_parents), 2, 'оба родителя')
        tap.eq(got_parents[0]['has_child'], True, 'есть дитя')
        tap.eq(got_parents[1]['has_child'], True, 'есть дитя')

        for p, c in zip([parent1, parent2], [children1, children2]):
            await t.post_ok(
                'api_admin_product_groups_hierarchy_list',
                json={'parent_group_id': p.group_id}
            )
            t.status_is(200)
            t.json_has('product_groups', 'есть группы')

            tap.eq(
                {
                    g['product_group']['group_id']
                    for g in t.res['json']['product_groups']
                },
                {g.group_id for g in c},
                'вытащили нужных детей'
            )
            tap.ok(
                all(g['has_child'] for g in t.res['json']['product_groups']),
                'у всех есть дети'
            )

        for c in children1 + children2:
            await t.post_ok(
                'api_admin_product_groups_hierarchy_list',
                json={'parent_group_id': c.group_id}
            )
            t.status_is(200)
            t.json_has('product_groups', 'есть группы')

            tap.eq(
                len(t.res['json']['product_groups']),
                1,
                'по одному ребенку'
            )
            tap.ok(
                not t.res['json']['product_groups'][0]['has_child'],
                'деток нет'
            )


async def test_not_found(tap, uuid, api):
    with tap.plan(2, 'проверяем кейс ненахода группы'):
        t = await api(role='admin')
        await t.post_ok(
            'api_admin_product_groups_hierarchy_list',
            json={'parent_group_id': uuid()}
        )
        t.status_is(404)
