import pytest

from stall.model.order import Order


# pylint: disable=too-many-branches,too-many-statements
@pytest.mark.parametrize('order_data', [
    {
        'required': [{
            'count': 21,
            'price': '1512.74',
            'price_unit': 22,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000001',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
        'source': '1c'
    },
    {
        'required': [{
            'count': 21,
            'price': '1512.74',
            'price_unit': 22,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000001',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
            'trust_code': 'some_code',
        },
        'source': '1c'
    },
    {
        'required': [{
            'weight': 3333,
            'price': '1512.74',
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000001',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
        'source': '1c'
    },
    {
        'required': [{
            'weight': 784374,
            'price': '151.7',
            'price_unit': 21,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000002',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 21,
            'price': '1512.73',
            'price_unit': 21,
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000002',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 23,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000003',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 23,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000003',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'weight': 23,
            'valid': '2012-11-10',
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000003',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 11,
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000004',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 11,
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000004',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
        },
    },
    {
        'required': [{
            'count': 10,
            'valid': '2020-03-31',
            'price': '1',
            'price_unit': 1
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000005',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
            'ignore_assortment': True,
        },
    },
    {
        'required': [{
            'count': 10,
            'valid': '2020-03-31',
            'price': '1',
            'price_unit': 1
        }],
        'type': 'acceptance',
        'approved': True,
        'attr': {
            'doc_number': '700303-000005',
            'doc_date': '1970-03-03',
            'contractor': 'some_contractor',
            'ignore_assortment': False,
        },
    },
    {
        'type': 'check_valid_short',
        'approved': True,
        'attr': {
            'doc_number': '700303-000006',
            'doc_date': '1970-03-03',
        },
    },
    {
        'type': 'check_valid_short',
        'approved': True,
        'attr': {
            'doc_number': '700303-000006',
            'doc_date': '1970-03-03',
        },
        'mode': 'store2markdown',
    },
    {
        'type': 'check_valid_regular',
        'approved': True,
        'attr': {
            'doc_number': '700303-000007',
            'doc_date': '1970-03-03',
        },
    },
    {
        'type': 'check_valid_regular',
        'approved': True,
        'attr': {
            'doc_number': '700303-000007',
            'doc_date': '1970-03-03',
        },
        'mode': 'store2markdown',
    },
    {
        'type': 'writeoff_prepare_day',
        'approved': True,
        'attr': {
            'doc_number': '700303-000008',
            'doc_date': '1970-03-03',
        },
    },
    {
        'type': 'writeoff_prepare_day',
        'approved': True,
        'attr': {
            'doc_number': '700303-000008',
            'doc_date': '1970-03-03',
        },
        'mode': 'store2markdown',
    },
    {
        'type': 'writeoff',
        'approved': True,
        'attr': {
            'doc_number': '700303-000009',
            'doc_date': '1970-03-03',
        },
        'shelves': None,
    },
    {
        'type': 'writeoff',
        'approved': True,
        'attr': {
            'doc_number': '700303-000009',
            'doc_date': '1970-03-03',
        },
        'shelves': None,
    },
    {
        'type': 'shipment',
        'approved': True,
        'attr': {
            'doc_number': '700303-000010',
            'doc_date': '1970-03-03',
        },
        'required': [
            {'count': 10},
            {'count': 20, 'price_type': 'office'},
        ],
    },
    {
        'type': 'shipment',
        'attr': {
            'doc_number': '700303-000010',
            'doc_date': '1970-03-03',
        },
        'required': [{
            'count': 21,
        }],
    },
    {
        'type': 'collect',
        'attr': {
            'doc_number': '700303-000010',
            'doc_date': '1970-03-03',
        },
        'required': [{
            'count': 21,
        }],
    },
    {
        'type': 'visual_control',
        'approved': True,
        'attr': {
            'doc_number': '700303-000006',
            'doc_date': '1970-03-03',
        },

    },
])
async def test_create(tap, dataset, api, uuid, order_data):
    with tap:
        tap.note(order_data.get('type', 'какой-то заказ'))

        product = await dataset.product()
        store = await dataset.store()

        t = await api(role='token:web.external.tokens.0')

        order_data['external_id'] = uuid()
        order_data['store_id'] = store.store_id
        if 'shelves' in order_data:
            shelf = await dataset.shelf(store=store, type='trash')
            order_data['shelves'] = [shelf.shelf_id]
        if 'required' in order_data:
            for i, _ in enumerate(order_data['required']):
                order_data['required'][i]['product_id'] = product.product_id

        await t.post_ok('api_integration_orders_create',
                        json=order_data)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', order_data['external_id'])
        t.json_is('order.source', order_data.get('source', 'integration'))
        if order_data.get('shelves'):
            t.json_is('order.shelves.0', shelf.shelf_id)
        else:
            t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        if order_data.get('approved'):
            t.json_like('order.approved', r'\d{4}(-\d{2}){2}.+')
        else:
            t.json_is('order.approved', None)
        t.json_is('order.acks', [], 'acks')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        attr = order_data.get('attr') or {
            'doc_date': order_data['doc_date'],
            'doc_number': order_data['doc_number'],
            'contractor': order_data.get('contractor'),
        }
        t.json_is('order.attr.doc_date', attr['doc_date'])
        t.json_is('order.attr.doc_number', attr['doc_number'])
        if attr.get('contractor'):
            t.json_is('order.attr.contractor', attr['contractor'])
        if attr.get('ignore_assortment'):
            t.json_is('order.attr.ignore_assortment', attr['ignore_assortment'])

        if 'required' in order_data:
            if 'valid' in order_data['required'][0]:
                t.json_is('order.required.0.valid',
                          order_data['required'][0]['valid'])
            else:
                t.json_hasnt('order.required.0.valid')
            if 'price' in order_data['required'][0]:
                t.json_is(
                    'order.required.0.price',
                    '{:.2f}'.format(float(order_data['required'][0]['price'])))
            else:
                t.json_hasnt('order.required.0.price')
            if 'price_unit' in order_data['required'][0]:
                t.json_is('order.required.0.price_unit',
                          order_data['required'][0]['price_unit'])
            elif 'price' in order_data['required'][0]:
                t.json_is('order.required.0.price_unit', 1)
            else:
                t.json_hasnt('order.required.0.price_unit')
            if 'count' in order_data['required'][0]:
                t.json_is('order.required.0.count',
                          order_data['required'][0]['count'])
            elif 'weight' in order_data['required'][0]:
                t.json_is('order.required.0.weight',
                          order_data['required'][0]['weight'])
            t.json_is('order.required.0.product_id',
                      order_data['required'][0]['product_id'])

        await t.post_ok('api_integration_orders_create',
                        json=order_data)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Повторный запрос успешен')
        t.json_has('order')
        t.json_is('order.external_id', order_data['external_id'])
        t.json_is('order.source', order_data.get('source', 'integration'))
        if order_data.get('shelves'):
            t.json_is('order.shelves.0', shelf.shelf_id)
        else:
            t.json_is('order.shelves', [], 'shelves пока не заполнены job')
        t.json_has('order.approved', 'approved')
        t.json_is('order.acks', [], 'acks')
        t.json_is('order.store_id', store.store_id, 'store')
        t.json_is('order.attr.doc_date', attr['doc_date'])
        t.json_is('order.attr.doc_number', attr['doc_number'])
        if attr.get('contractor'):
            t.json_is('order.attr.contractor', attr.get('contractor'))

        if 'required' in order_data:
            if 'valid' in order_data['required'][0]:
                t.json_is('order.required.0.valid',
                          order_data['required'][0]['valid'])
            else:
                t.json_hasnt('order.required.0.valid')
            if 'price' in order_data['required'][0]:
                t.json_is(
                    'order.required.0.price',
                    '{:.2f}'.format(float(order_data['required'][0]['price'])))
            else:
                t.json_hasnt('order.required.0.price')
            if 'price_unit' in order_data['required'][0]:
                t.json_is('order.required.0.price_unit',
                          order_data['required'][0]['price_unit'])
            elif 'price' in order_data['required'][0]:
                t.json_is('order.required.0.price_unit', 1)
            else:
                t.json_hasnt('order.required.0.price_unit')

            if 'count' in order_data['required'][0]:
                t.json_is('order.required.0.count',
                          order_data['required'][0]['count'])
            elif 'weight' in order_data['required'][0]:
                t.json_is('order.required.0.weight',
                          order_data['required'][0]['weight'])
            t.json_is('order.required.0.product_id',
                      order_data['required'][0]['product_id'])

            order_data['required'].append({'product_id': uuid(), 'count': 2})
            await t.post_ok('api_integration_orders_create',
                            json=order_data)
            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')

        order = await Order.load([store.store_id, order_data['external_id']],
                                 by='external')
        order.status = 'complete'
        await order.save()
        await t.post_ok('api_integration_orders_create',
                        json=order_data)
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


@pytest.mark.parametrize('required, expected', [
    [
        {
            'product_id': 'fakeidhere',
            'count': 2,
            'weight': 10
        },
        'BAD_REQUEST'
    ],
    [
        {
            'product_id': 'fakeidhere',
            'weight': 0
        },
        'BAD_REQUEST'
    ],
    [
        [
            {
                'product_id': 'samefakeid',
                'count': 1
            },
            {
                'product_id': 'samefakeid',
                'count': 2
            },
        ],
        'ER_BAD_REQUEST'
    ]
])
async def test_create_incorrect_required(
        tap, dataset, api, required, expected, uuid):
    with tap.plan(3, 'Неправильные продукты'):
        store = await dataset.store()

        t = await api(role='token:web.external.tokens.0')
        order_data = {
            'external_id': uuid(),
            'store_id': store.store_id,
            'required': required,
            'type': 'acceptance',
            'approved': True,
            'attr': {
                'doc_number': '700303-000005',
                'doc_date': '1970-03-03',
                'contractor': 'some_contractor',
            },
        }

        await t.post_ok('api_integration_orders_create',
                        json=order_data)
        t.status_is(400, diag=True)
        t.json_is('code', expected)


async def test_create_company(tap, dataset, api, uuid):
    with tap.plan(8, 'Создание заказа по ключу компании'):

        product = await dataset.product()
        company = await dataset.company()
        store   = await dataset.store(company=company)

        external_id = uuid()

        t = await api(token=company.token)

        await t.post_ok(
            'api_integration_orders_create',
            json={
                'external_id': external_id,
                'store_id': store.store_id,

                'required': [{
                    'product_id': product.product_id,
                    'count': 10,
                    'valid': '2020-03-31',
                    'price': '1',
                    'price_unit': 1
                }],
                'type': 'acceptance',
                'approved': True,
                'attr': {
                    'doc_number': '700303-000005',
                    'doc_date': '1970-03-03',
                    'contractor': 'some_contractor',
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_is('order.external_id', external_id)
        t.json_is('order.source', 'integration')
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


async def test_create_access(tap, dataset, api, uuid):
    with tap.plan(3, 'Создание заказа по неизвестному ключу'):

        product = await dataset.product()
        store   = await dataset.store()

        external_id = uuid()

        t = await api(token=uuid())

        await t.post_ok(
            'api_integration_orders_create',
            json={
                'external_id': external_id,
                'store_id': store.store_id,

                'required': [{
                    'product_id': product.product_id,
                    'count': 10,
                    'valid': '2020-03-31',
                    'price': '1',
                    'price_unit': 1
                }],
                'type': 'acceptance',
                'approved': True,
                'attr': {
                    'doc_number': '700303-000005',
                    'doc_date': '1970-03-03',
                    'contractor': 'some_contractor',
                },
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_create_unknown(tap, dataset, api, uuid):
    with tap.plan(3, 'Создание заказа в неизвестном складе'):

        product = await dataset.product()

        external_id = uuid()

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_integration_orders_create',
            json={
                'external_id': external_id,
                'store_id': uuid(),

                'required': [{
                    'product_id': product.product_id,
                    'count': 10,
                    'valid': '2020-03-31',
                    'price': '1',
                    'price_unit': 1
                }],
                'type': 'acceptance',
                'approved': True,
                'attr': {
                    'doc_number': '700303-000005',
                    'doc_date': '1970-03-03',
                    'contractor': 'some_contractor',
                },
            },
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')


async def test_create_not_owner(tap, dataset, api, uuid):
    with tap.plan(3, 'Создание заказа в на чужом складе'):

        product = await dataset.product()
        company1 = await dataset.company()
        company2 = await dataset.company()
        store   = await dataset.store(company=company1)

        external_id = uuid()

        t = await api(token=company2.token)

        await t.post_ok(
            'api_integration_orders_create',
            json={
                'external_id': external_id,
                'store_id': store.store_id,

                'required': [{
                    'product_id': product.product_id,
                    'count': 10,
                    'valid': '2020-03-31',
                    'price': '1',
                    'price_unit': 1
                }],
                'type': 'acceptance',
                'approved': True,
                'attr': {
                    'doc_number': '700303-000005',
                    'doc_date': '1970-03-03',
                    'contractor': 'some_contractor',
                },
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')



async def test_create_with_contractor_id(tap, dataset, api, uuid):
    with tap.plan(6, 'создаем заказ с contractor_id'):

        product = await dataset.product()
        company = await dataset.company()
        store = await dataset.store(company=company)

        external_id = uuid()

        t = await api(token=company.token)

        await t.post_ok(
            'api_integration_orders_create',
            json={
                'external_id': external_id,
                'store_id': store.store_id,

                'required': [{
                    'product_id': product.product_id,
                    'count': 10,
                    'valid': '2020-03-31',
                    'price': '1',
                    'price_unit': 1
                }],
                'type': 'acceptance',
                'approved': True,
                'attr': {
                    'doc_number': '700303-000005',
                    'doc_date': '1970-03-03',
                    'contractor': 'some_contractor',
                    'contractor_id': 'some_contractor_id',
                },
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')
        t.json_has('order.attr.contractor_id')
        t.json_is('order.attr.contractor_id', 'some_contractor_id')

@pytest.mark.parametrize('source', ['dispatcher', 'tsd', 'eda', '1c',
                                    'integration', 'external', 'woody',
                                    'tristero', 'bababoy'])
async def test_source(tap, dataset, api, uuid, source):
    with tap:
        order_data = {
            'required': [{
                'count': 21,
                }],
            'type': 'acceptance',
            'attr': {
                'doc_number': '700303-000001',
                'doc_date': '1970-03-03',
                'contractor': 'some_contractor',
            },
            'source': source
        }
        store = await dataset.store()
        t = await api(role='token:web.external.tokens.0')
        order_data['external_id'] = uuid()
        order_data['store_id'] = store.store_id
        if 'required' in order_data:
            for i, _ in enumerate(order_data['required']):
                order_data['required'][i]['product_id'] = uuid() + '1'
        await t.post_ok('api_integration_orders_create',
                        json=order_data)
        if source != 'bababoy':
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
        else:
            t.status_is(400, diag=True)
            t.json_is('code', 'BAD_REQUEST')


@pytest.mark.parametrize('required', [
    [{'product_id': '123123'}],
    [{'shelf_id': '234234'}],
    [{'product_id': '345345', 'shelf_id': '456456'}],
    [{'product_id': '567567', 'shelf_id': None}, {'shelf_id': '678678'}],
])
async def test_create_stop_list(tap, dataset, api, uuid, required):
    with tap:
        store = await dataset.store()
        tap.ok(store, 'store created')

        external_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_integration_orders_create', json={
            'store_id': store.store_id,
            'external_id': external_id,
            'type': 'stop_list',
            'required': required,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order')

        order_id = t.res['json']['order']['order_id']
        order = await dataset.Order.load(order_id)
        tap.ok(order, 'order fetched')

        tap.eq(order.external_id, external_id, 'external_id ok')
        tap.eq(order.type, 'stop_list', 'type ok')
        tap.eq(order.store_id, store.store_id, 'store_id ok')
        tap.eq(order.company_id, store.company_id, 'company_id ok')
        tap.is_ok(order.user_id, None, 'user_id ok')
        tap.eq(order.required, required, 'required ok')


@pytest.mark.parametrize('required', [
    [],
    [{}],
    [{'product_id': None}],
    [{'shelf_id': '123123'}, {'shelf_id': None}]
])
async def test_create_stop_list_badreq(tap, dataset, api, uuid, required):
    with tap:
        store = await dataset.store()
        tap.ok(store, 'store created')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_integration_orders_create', json={
            'store_id': store.store_id,
            'external_id': uuid(),
            'type': 'stop_list',
            'required': [required],
        })
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
