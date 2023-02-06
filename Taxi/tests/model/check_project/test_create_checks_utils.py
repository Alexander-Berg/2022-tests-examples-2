from stall.model.check_project import collect_stores, collect_products


async def test_collect_stores(tap, dataset, uuid):
    # pylint: disable=too-many-locals
    with tap.plan(6, 'тестируем collect_stores'):
        company_id = uuid()
        cluster_id = uuid()
        company_stores = [
            await dataset.store(company_id=company_id)
            for _ in range(3)
        ]
        cluster_stores = [
            await dataset.store(cluster_id=cluster_id)
            for _ in range(3)
        ]
        both_store = await dataset.store(
            company_id=company_id, cluster_id=cluster_id,
        )
        none_stores = [await dataset.store() for _ in range(3)]

        cp1 = await dataset.check_project(company_id=company_id)
        cp2 = await dataset.check_project(cluster_id=cluster_id)
        cp3 = await dataset.check_project(store_id=both_store.store_id)
        cp4 = await dataset.check_project(
            stores={
                'store_id': [x.store_id for x in [*none_stores, both_store]],
                'company_id': [company_id],
            },
        )
        cp5 = await dataset.check_project(
            stores={
                'store_id': [x.store_id for x in [*none_stores, both_store]],
                'cluster_id': [cluster_id],
            },
        )
        cp6 = await dataset.check_project(
            stores={
                'company_id': [company_id],
                'cluster_id': [cluster_id],
            },
        )
        cp7 = await dataset.check_project(
            stores={
                'store_id': [x.store_id for x in [*none_stores, both_store]],
                'company_id': [company_id],
                'cluster_id': [cluster_id],
            },
        )

        stores, cp_id2stores = await collect_stores(
            {cp.check_project_id: cp for cp in (cp1, cp2)}
        )
        tap.eq(
            stores,
            {
                s.store_id: s
                for s in [*company_stores, *cluster_stores, both_store]
            },
            'stores ok',
        )
        tap.eq(
            cp_id2stores,
            {
                cp1.check_project_id: {
                    s.store_id
                    for s in [*company_stores, both_store]
                },
                cp2.check_project_id: {
                    s.store_id
                    for s in [*cluster_stores, both_store]
                },
            },
            'check_project2stores ok',
        )

        stores, cp_id2stores = await collect_stores(
            {cp.check_project_id: cp for cp in (cp3, cp4, cp5)}
        )
        all_stores = [
            *company_stores, *cluster_stores, *none_stores, both_store
        ]
        tap.eq(
            stores,
            {s.store_id: s for s in all_stores},
            'stores ok',
        )
        tap.eq(
            cp_id2stores,
            {
                cp3.check_project_id: {both_store.store_id},
                cp4.check_project_id: {
                    s.store_id
                    for s in [*none_stores, *company_stores, both_store]
                },
                cp5.check_project_id: {
                    s.store_id
                    for s in [*none_stores, *cluster_stores, both_store]
                },
            },
            'check_project2stores ok',
        )

        stores, cp_id2stores = await collect_stores(
            {cp.check_project_id: cp for cp in (cp6, cp7)}
        )
        tap.eq(
            stores,
            {s.store_id: s for s in all_stores},
            'stores ok',
        )
        tap.eq(
            cp_id2stores,
            {
                cp6.check_project_id: {
                    s.store_id
                    for s in [both_store, *company_stores, *cluster_stores]
                },
                cp7.check_project_id: {s.store_id for s in all_stores}
            },
            'check_project2stores ok',
        )


async def test_collect_products_basic(tap, dataset):
    # pylint: disable=too-many-locals
    with tap.plan(10, 'тестируем collect_products базовый кейс'):
        #    X
        #   / \
        #  X   X
        #     / \
        #    X   X
        root_pg = await dataset.product_group()
        left_1pg = await dataset.product_group(
            parent_group_id=root_pg.group_id
        )
        right_1pg = await dataset.product_group(
            parent_group_id=root_pg.group_id
        )
        left_2pg = await dataset.product_group(
            parent_group_id=right_1pg.group_id
        )
        right_2pg = await dataset.product_group(
            parent_group_id=right_1pg.group_id
        )
        ps_left1 = [
            await dataset.product(groups=[left_1pg.group_id])
            for _ in range(3)
        ]
        ps_left2 = [
            await dataset.product(groups=[left_2pg.group_id])
            for _ in range(3)
        ]
        ps_right2 = [
            await dataset.product(groups=[right_2pg.group_id])
            for _ in range(3)
        ]

        ans = {
            root_pg.group_id: ps_left1 + ps_left2 + ps_right2,
            left_1pg.group_id: ps_left1,
            right_1pg.group_id: ps_left2 + ps_right2,
            left_2pg.group_id: ps_left2,
            right_2pg.group_id: ps_right2,
        }
        for pg_id, products in ans.items():
            cp = await dataset.check_project(product_group_id=pg_id)
            cache_products, pg_dict = await collect_products(
                {cp.check_project_id: cp})
            product_ids = set(p.product_id for p in products)
            tap.eq(
                set(cache_products.keys()),
                product_ids,
                'В продуктах все ключи'
            )
            tap.eq(pg_dict[pg_id], product_ids, 'продукты собрались ок')


async def test_collect_products_few(tap, dataset):
    with tap.plan(13, 'тестим collect_products в случае не дерева'):
        #     0         7
        #    / \       / \
        #   1   2     8   9
        #  / \ / \    |   |
        # 3  4 5  6   10  11
        pgs = [await dataset.product_group()]
        pgs += [
            await dataset.product_group(parent_group_id=pgs[0].group_id)
            for _ in range(2)
        ]
        pgs += [
            await dataset.product_group(parent_group_id=pgs[1].group_id)
            for _ in range(2)
        ]
        pgs += [
            await dataset.product_group(parent_group_id=pgs[2].group_id)
            for _ in range(2)
        ]
        pgs += [await dataset.product_group()]
        pgs += [
            await dataset.product_group(parent_group_id=pgs[7].group_id)
            for _ in range(2)
        ]
        pgs += [await dataset.product_group(parent_group_id=pgs[8].group_id)]
        pgs += [await dataset.product_group(parent_group_id=pgs[9].group_id)]

        ps_dict = {}
        all_products = []
        for num in [3, 4, 5, 6, 10, 11]:
            products = [
                await dataset.product(groups=[pgs[num].group_id])
                for _ in range(3)
            ]
            ps_dict[num] = products
            all_products.extend(products)
        ps_dict[1] = ps_dict[3] + ps_dict[4]
        ps_dict[2] = ps_dict[5] + ps_dict[6]
        ps_dict[0] = ps_dict[1] + ps_dict[2]
        ps_dict[8] = ps_dict[10]
        ps_dict[9] = ps_dict[11]
        ps_dict[7] = ps_dict[8] + ps_dict[9]

        cps = [await dataset.check_project(product_group=pg) for pg in pgs]

        products_cache, pg_dict = await collect_products(
            {cp.check_project_id: cp for cp in cps}
        )
        tap.eq(
            set(products_cache.keys()),
            {
                product.product_id for product in all_products
            },
            'Все продукты в кэше'
        )
        for i, pg in enumerate(pgs):
            tap.eq(
                pg_dict[pg.group_id],
                {p.product_id for p in ps_dict[i]},
                'правильно загрузились продукты',
            )
