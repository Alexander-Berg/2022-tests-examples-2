from ymlcfg.jpath import JPath


async def test_virtual_parent(tap, prod_sync, dataset, load_json, uuid):
    with tap.plan(4, 'Проверяем что можно менять виртуального родителя'):
        parent_external = uuid()
        a_product = load_json('data/product.pigeon.json')
        a_product['attributes']['virtual_product'] = True
        a_product['skuId'] = parent_external
        parent_product = await prod_sync.prepare_obj(JPath(a_product))
        await parent_product.save()

        tap.eq_ok(
            parent_product.vars['imported']['virtual_product'],
            True,
            'родитель виртуален',
        )

        child_external = uuid()
        child_product = await dataset.product(
            external_id=child_external,
            parent_id=parent_product.product_id,
            vars={'imported': {'grade_values': []}},
        )

        tap.eq_ok(
            child_product.parent_id,
            parent_product.product_id,
            'нужный родитель',
        )

        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = child_external
        a_product['attributes']['parentItem'] = child_external
        child_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            child_product.parent_id,
            child_product.product_id,
            'родитель поменялся',
        )

        parent_external_2 = uuid()
        new_parent = await dataset.product(
            external_id=parent_external_2,
            vars={'imported': {'grade_values': []}},
        )
        a_product['attributes']['parentItem'] = parent_external_2
        child_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            child_product.parent_id,
            new_parent.product_id,
            'родитель поменялся',
        )


async def test_remove_parent(tap, prod_sync, dataset, load_json, uuid):
    with tap.plan(5, 'Проверяем что можно менять виртуального родителя'):
        parent_external = uuid()
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = parent_external
        parent_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            parent_product.vars['imported']['virtual_product'],
            False,
            'родитель не виртуален',
        )

        child_external = uuid()
        child_product = await dataset.product(
            external_id=child_external,
            parent_id=parent_product.product_id,
            vars={'imported': {'grade_values': []}},
        )

        tap.eq_ok(
            child_product.parent_id,
            parent_product.product_id,
            'нужный родитель',
        )
        parent_product_id = parent_product.product_id

        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = child_external
        a_product['attributes']['parentItem'] = None
        await prod_sync.prepare_obj(JPath(a_product))
        await child_product.reload()

        tap.eq(
            child_product.parent_id, parent_product_id, 'родитель тот же'
        )

        parent_product.vars['imported']['virtual_product'] = True
        parent_product.rehashed('vars', True)
        await parent_product.save()
        tap.eq_ok(
            parent_product.vars['imported']['virtual_product'],
            True,
            'родитель виртуален',
        )

        child_product = await prod_sync.prepare_obj(JPath(a_product))
        tap.ok(not child_product.parent_id, 'родитель поменялся')
