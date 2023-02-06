

async def test_check_contractor(tap, api, dataset, uuid):
    with tap.plan(12, 'проверяем базовые кейсы'):
        store = await dataset.store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store=store)
        product = await dataset.product()
        assortment = await dataset.assortment_contractor(store=store)
        acp = await dataset.assortment_contractor_product(
            assortment=assortment,
            product=product,
            status='removed',
        )
        order = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'contractor_id': assortment.contractor_id},
        )

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': uuid(),
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        order.required = [{'product_id': product.product_id, 'count': 300}]
        await order.save()
        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        order.required = []
        await order.save()
        acp.status = 'active'
        await acp.save()
        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_check_contractor_bad_user(tap, api, dataset, uuid):
    with tap.plan(6, 'проверяем 403 при плохом юзере'):
        store = await dataset.store(options={'exp_schrodinger': True})
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'contractor_id': uuid()},
        )

        user1 = await dataset.user(role='authen_guest')
        user2 = await dataset.user(role='admin', store_id=None)

        for user in [user1, user2]:
            t = await api(user=user)
            await t.post_ok(
                'api_tsd_check_contractor',
                json={
                    'order_id': order.order_id,
                    'product_id': product.product_id
                },
            )
            t.status_is(403)
            t.json_is('code', 'ER_ACCESS')


async def test_check_contractor_store(tap, api, dataset, uuid):
    with tap.plan(6, 'фейковая лавка/лавка без эксперимента'):
        user = await dataset.user(role='admin', store_id=uuid())
        product = await dataset.product()
        order = await dataset.order(
            type='acceptance',
            status='complete',
            estatus='begin',
        )
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            },
        )
        t.status_is(403)
        t.json_is('code', 'ER_ACCESS')

        store = await dataset.store(options={'exp_schrodinger': False})

        user.store_id = store.store_id
        user.company_id = store.company_id
        await user.save()
        order = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'contractor_id': uuid()},
        )

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id
            },
        )
        t.status_is(200)
        t.json_is('code', 'OK')


async def test_check_contractor_order(tap, api, dataset, uuid):
    with tap.plan(9, 'плохой ордер/ордер с ignore_assortment'):
        store1 = await dataset.store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store_id=store1.store_id)
        product = await dataset.product()

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_contractor',
            json={'order_id': uuid(), 'product_id': product.product_id},
        )
        t.status_is(403)
        t.json_is('code', 'ER_ACCESS')

        order1 = await dataset.order(
            store=store1,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'ignore_assortment': True},
        )

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order1.order_id,
                'product_id': product.product_id
            },
        )
        t.status_is(200)
        t.json_is('code', 'OK')

        store2 = await dataset.store(options={'exp_schrodinger': True})
        order2 = await dataset.order(
            store_id=store2.store_id,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'ignore_assortment': True},
        )

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order2.order_id,
                'product_id': product.product_id,
            },
        )
        t.status_is(403)
        t.json_is('code', 'ER_ACCESS')


async def test_check_contractor_no_assortment(tap, api, dataset):  # pylint: disable=invalid-name
    with tap.plan(5, 'разные кейсы с ассортиментом'):
        store = await dataset.store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store_id=store.store_id)
        product = await dataset.product()

        t = await api(user=user)

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='begin',
        )

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            },
        )
        t.status_is(200)

        assortment = await dataset.assortment_contractor(store=store)
        order.attr['contractor_id'] = assortment.contractor_id
        await order.save()

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id
            },
        )
        t.status_is(404)
        t.json_is('code', 'ER_NOT_FOUND')


async def test_child_in_assortment(tap, api, dataset):
    with tap.plan(3, 'В ассортименте только родитель'):
        store = await dataset.store(options={'exp_schrodinger': True})
        user = await dataset.user(role='admin', store=store)
        parent_product = await dataset.product()
        product = await dataset.product(parent_id=parent_product.product_id)
        assortment = await dataset.assortment_contractor(store=store)
        await dataset.assortment_contractor_product(
            assortment=assortment,
            product=parent_product,
            status='active',
        )
        order = await dataset.order(
            store=store,
            type='acceptance',
            status='complete',
            estatus='begin',
            attr={'contractor_id': assortment.contractor_id},
        )

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_contractor',
            json={
                'order_id': order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
