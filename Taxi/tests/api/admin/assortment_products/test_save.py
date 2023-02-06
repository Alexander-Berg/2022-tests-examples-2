async def test_save_create(tap, api, dataset):
    with tap.plan(12):

        t = await api(role='admin')

        assortment = await dataset.assortment()
        product = await dataset.product()

        ap_data = {
            'status': 'active',
            'assortment_id': assortment.assortment_id,
            'product_id': product.product_id,
            'max': 10,
            'min': 0,
            'cob_time': 0,
            'order': 50,
        }

        await t.post_ok('api_admin_assortment_products_save', json=ap_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ap created')

        t.json_has('assortment_product.ap_id', 'ap_id')
        t.json_has('assortment_product.created', 'created')
        t.json_has('assortment_product.updated', 'updated')
        t.json_is(
            'assortment_product.assortment_id',
            ap_data['assortment_id'],
            'assortment_id',
        )
        t.json_is(
            'assortment_product.product_id',
            ap_data['product_id'],
            'product_id',
        )
        t.json_is('assortment_product.max', ap_data['max'], 'max')
        t.json_is('assortment_product.min', ap_data['min'], 'min')
        t.json_is(
            'assortment_product.cob_time', ap_data['cob_time'], 'cob_time',
        )
        t.json_is('assortment_product.order', ap_data['order'], 'order')

async def test_save_update(tap, api, dataset):
    with tap.plan(9):
        t = await api(role='admin')

        ap = await dataset.assortment_product(max=1, min=0)
        tap.ok(ap, 'ap created')

        # ok case

        ap_data = {
            'ap_id': ap.ap_id,
            'max': 100,
            'min': 10,
        }

        await t.post_ok('api_admin_assortment_products_save', json=ap_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ap updated')
        t.json_is('assortment_product.max', ap_data['max'], 'max')
        t.json_is('assortment_product.min', ap_data['min'], 'min')

        # err case: max, min

        ap_data['max'] = 10
        ap_data['min'] = 100

        await t.post_ok('api_admin_assortment_products_save', json=ap_data)

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')


# pylint: disable=invalid-name
async def test_save_update_by_assortment_id(tap, api, dataset):
    with tap.plan(9):
        t = await api(role='admin')

        ap = await dataset.assortment_product(max=1, min=0)
        tap.ok(ap, 'ap created')

        # ok case

        ap_data = {
            'product_id': ap.product_id,
            'assortment_id': ap.assortment_id,
            'max': 100,
            'min': 10,
        }

        await t.post_ok('api_admin_assortment_products_save', json=ap_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ap updated')
        t.json_is('assortment_product.max', ap_data['max'], 'max')
        t.json_is('assortment_product.min', ap_data['min'], 'min')

        # err case: max, min

        ap_data['max'] = 10
        ap_data['min'] = 100

        await t.post_ok('api_admin_assortment_products_save', json=ap_data)

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')

async def test_save_bad_data(tap, api):
    with tap.plan(3):

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_save',
            json={'spam': 'yes'},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')


async def test_save_bad_min_max(tap, api, dataset):
    with tap.plan(3, 'Проверка некорректно введенных данных min/max'):

        assortment = await dataset.assortment()
        product = await dataset.product()

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortment_products_save',
            json={
                'status': 'active',
                'assortment_id': assortment.assortment_id,
                'product_id': product.product_id,
                'cob_time': 0,
                'order': 50,
                'trigger_threshold': 2,
                'target_threshold': 1,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')
