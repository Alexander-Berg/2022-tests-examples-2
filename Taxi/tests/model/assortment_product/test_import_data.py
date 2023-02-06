from stall.model.assortment_product import AssortmentProduct, import_data


async def test_parent_assortment(tap, dataset):
    with tap:
        products = [await dataset.product() for _ in range(5)]

        s = await dataset.store()
        u = await dataset.user(store=s)
        a = await dataset.assortment()

        s_value = {
            'store_id': s.store_id,
            'user_id': u.user_id,
            'assortment_id': a.assortment_id,
            'products': [{'external_id': i.external_id} for i in products],
            'status': 'active',
        }

        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps1 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps1
            },
            {
                (i.product_id, i.ttl_show, i.order, 'active')
                for i in products
            },
            'Assortment has correct products',
        )

        new_product = await dataset.product()
        products.append(new_product)

        tap.eq_ok(len(products), 6, 'New product added')

        s_value['products'].append({'external_id': new_product.external_id})
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps2 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps2
            },
            {
                (i.product_id, i.ttl_show, i.order, 'active')
                for i in products
            },
            'New product imported',
        )

        s_value['status'] = 'excluded'
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps3 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps3
            },
            {
                (i.product_id, i.ttl_show, i.order, 'active')
                for i in products
            },
            'Set excluded ignored',
        )

        s_value['status'] = 'removed'
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps4 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps4
            },
            {
                (i.product_id, i.ttl_show, i.order, 'removed')
                for i in products
            },
            'Set removed accepted',
        )

        s_value['status'] = 'active'
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps5 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps5
            },
            {
                (i.product_id, i.ttl_show, i.order, 'active')
                for i in products
            },
            'Set active accepted',
        )


async def test_child_assortment(tap, dataset):
    with tap:
        products = [await dataset.product() for _ in range(5)]

        s = await dataset.store()
        u = await dataset.user(store=s)

        a = await dataset.assortment()
        child_a = await dataset.assortment(parents=[a.assortment_id])

        tap.eq_ok(child_a.parents[0], a.assortment_id, 'With parent')

        s_value = {
            'store_id': s.store_id,
            'user_id': u.user_id,
            'assortment_id': a.assortment_id,
            'products': [{'external_id': i.external_id} for i in products],
            'status': 'active',
        }

        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        added_aps = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in added_aps
            },
            {
                (i.product_id, i.ttl_show, i.order, 'active')
                for i in products
            },
            'Parent assortment has correct products',
        )

        s_value['assortment_id'] = child_a.assortment_id
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        child_added_aps1 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', child_a.assortment_id),
        )

        tap.eq_ok(len(list(child_added_aps1)), 0, 'Nothing added to child')

        new_product = await dataset.product()
        products.append(new_product)
        s_value['products'].append({'external_id': new_product.external_id})
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        child_added_aps2 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', child_a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in child_added_aps2
            },
            {
                (
                    new_product.product_id,
                    new_product.ttl_show,
                    new_product.order,
                    'active',
                ),
            },
            'Child assortment has 1 active product',
        )

        s_value['status'] = 'excluded'
        s = await dataset.stash(value=s_value)

        await import_data(s.stash_id)

        child_added_aps3 = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', child_a.assortment_id),
        )

        tap.eq_ok(
            {
                (i.product_id, i.ttl_show, i.order, i.status)
                for i in child_added_aps3
            },
            {
                (i.product_id, i.ttl_show, i.order, 'excluded')
                for i in products
            },
            'Child assortment has excluded products',
        )


async def test_import_thresholds(tap, dataset):
    with tap.plan(21, 'заливаем пороги'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        ass = await dataset.assortment()

        ps = [await dataset.product() for _ in range(2)]

        stash_dict = {
            'store_id': store.store_id,
            'user_id': user.user_id,
            'assortment_id': ass.assortment_id,
            'products': [
                {
                    'external_id': p.external_id,
                    'min': '2',
                }
                for p in ps
            ],
            'status': 'active',
        }

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )
        tap.ok(not aps.list, 'нету ассортиментов')
        for p in stash_dict['products']:
            p.pop('min')
            p['max'] = '2'

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )
        for ap in aps:
            tap.eq(ap.trigger_threshold, 0, 'триггер 0')
            tap.eq(ap.target_threshold, 2, 'таргет 2')

        for p in stash_dict['products']:
            p['max'] = '69'

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )
        for ap in aps:
            tap.eq(ap.trigger_threshold, 0, 'триггер тот же')
            tap.eq(ap.target_threshold, 69, 'таргет nice')

        for p in stash_dict['products']:
            p.pop('max')
            p['min'] = ''

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )
        for ap in aps:
            tap.eq(ap.trigger_threshold, 0, 'триггер тот же')
            tap.eq(ap.target_threshold, 69, 'таргет тот же')

        stash_dict['products'][0]['min'] = '111'
        stash_dict['products'][1]['max'] = 'zhopka22'
        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        ap = await AssortmentProduct.load(
            (ass.assortment_id, ps[0].product_id),
            by='product',
        )
        tap.eq(ap.trigger_threshold, 0, 'триггер тот же')
        tap.eq(ap.target_threshold, 69, 'таргет тот же')

        ap = await AssortmentProduct.load(
            (ass.assortment_id, ps[1].product_id),
            by='product',
        )
        tap.eq(ap.trigger_threshold, 0, 'триггер тот же')
        tap.eq(ap.target_threshold, 69, 'таргет тот же')

        stash_dict['products'][0]['min'] = '11'
        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        ap = await AssortmentProduct.load(
            (ass.assortment_id, ps[0].product_id),
            by='product',
        )
        tap.eq(ap.trigger_threshold, 11, 'триггер 11')
        tap.eq(ap.target_threshold, 69, 'таргет тот же')

        ap = await AssortmentProduct.load(
            (ass.assortment_id, ps[1].product_id),
            by='product',
        )
        tap.eq(ap.trigger_threshold, 0, 'триггер тот же')
        tap.eq(ap.target_threshold, 69, 'таргет тот же')


async def test_import_ttl_show(tap, dataset):
    with tap.plan(6, 'тестим залив ttl_show'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        ass = await dataset.assortment()

        ps = [await dataset.product(ttl_show=10) for _ in range(2)]

        stash_dict = {
            'store_id': store.store_id,
            'user_id': user.user_id,
            'assortment_id': ass.assortment_id,
            'products': [
                {
                    'external_id': p.external_id,
                }
                for p in ps
            ],
            'status': 'active',
        }

        stash_dict['products'][0]['ttl_show'] = '20'

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = (await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )).list
        if aps[0].product_id != ps[0].product_id:
            aps[0], aps[1] = aps[1], aps[0]

        tap.eq(aps[0].ttl_show, 20, 'ttl_show 20')
        tap.eq(aps[1].ttl_show, 10, 'ttl_show 10')

        stash_dict['products'][0]['ttl_show'] = '-1'
        stash_dict['products'][1]['ttl_show'] = '22'
        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        for ap in aps:
            await ap.reload()
        tap.eq(aps[0].ttl_show, 20, 'ttl_show 20')
        tap.eq(aps[1].ttl_show, 22, 'ttl_show 22')

        stash_dict['products'][0]['ttl_show'] = '32'
        stash_dict['products'][1].pop('ttl_show')
        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        for ap in aps:
            await ap.reload()
        tap.eq(aps[0].ttl_show, 32, 'ttl_show 32')
        tap.eq(aps[1].ttl_show, 22, 'ttl_show тот же')


async def test_import_ttl_show_assortment(tap, dataset):
    with tap.plan(5, 'тестим ttl_show проставляется верно'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        ass = await dataset.assortment(ttl_show=12)

        ttl_show = [0, 34, 34, 34]
        p_list = [await dataset.product(ttl_show=ttl_show[i]) for i in range(4)]

        stash_dict = {
            'store_id': store.store_id,
            'user_id': user.user_id,
            'assortment_id': ass.assortment_id,
            'products': [
                {
                    'external_id': p_list[0].external_id,
                },
                {
                    'external_id': p_list[1].external_id,
                },
                {
                    'external_id': p_list[2].external_id,
                    'ttl_show': '56'
                },
                {
                    'external_id': p_list[3].external_id,
                    'ttl_show': '0'
                },

            ],
            'status': 'active',
        }

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = (await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass.assortment_id),
        )).list
        aps_dict = {ap.product_id: ap.ttl_show for ap in aps}
        tap.eq_ok(aps_dict[p_list[0].product_id], 12,
                  'ttl_show как у ассортимента')
        tap.eq_ok(aps_dict[p_list[1].product_id], 34,
                  'ttl_show как у продукта')
        tap.eq_ok(aps_dict[p_list[2].product_id], 56,
                  'ttl_show переданный в csv')
        tap.eq_ok(aps_dict[p_list[3].product_id], 0,
                  'ttl_show переданный в csv')

        ass_1 = await dataset.assortment(ttl_show=0)

        p = await dataset.product(ttl_show=0)

        stash_dict = {
            'store_id': store.store_id,
            'user_id': user.user_id,
            'assortment_id': ass_1.assortment_id,
            'products': [
                {
                    'external_id': p.external_id,
                },
            ],
            'status': 'active',
        }

        stash = await dataset.stash(value=stash_dict)
        await import_data(stash.stash_id)

        aps = (await AssortmentProduct.list(
            by='full',
            conditions=('assortment_id', ass_1.assortment_id),
        )).list
        tap.eq_ok(aps[0].ttl_show, 0, 'ttl_show как у ассортимента')

