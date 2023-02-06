from datetime import timedelta, timezone

from stall.model.product_sample import ProductSample
from stall.model.sampling_condition import SamplingCondition


async def test_create(tap, dataset, api, uuid):
    with tap.plan(15):
        group = await dataset.product_group()
        product = await dataset.product()
        t = await api(role='admin')

        external_id = uuid()
        title = uuid()
        await t.post_ok('api_admin_samples_save',
                        json={
                            'external_id': external_id,
                            'title': title,
                            'product_id': product.product_id,
                            'mode': 'optional',
                            'count': 2,
                            'tags': ['sampling'],
                            'condition': {
                                'condition_type': 'group_present',
                                'group_id': group.group_id,
                                'children': None,
                            },
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('sample.sample_id')
        t.json_is('sample.product_id', product.product_id)
        t.json_is('sample.mode', 'optional')
        t.json_is('sample.count', 2)
        t.json_is('sample.tags', ['sampling'])
        t.json_is('sample.condition.condition_type', 'group_present')
        t.json_is('sample.condition.group_id', group.group_id)
        t.json_is('sample.condition.children', [])
        sample_id = t.res['json']['sample']['sample_id']

        await t.post_ok('api_admin_samples_save',
                        json={
                            'external_id': external_id,
                            'title': title,
                            'product_id': product.product_id,
                            'mode': 'optional',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('sample.sample_id', sample_id, 'The same sample returned')


async def test_update(tap, dataset, api):
    with tap.plan(18):
        product = await dataset.product()
        sample = await dataset.sample()

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_save',
                        json={
                            'sample_id': sample.sample_id,
                            'product_id': product.product_id,
                            'mode': 'optional',
                            'count': 3,
                            'tags': ['sampling'],
                            'condition': {
                                'condition_type': 'constant_true',
                            },
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('sample.sample_id', sample.sample_id)
        t.json_is('sample.product_id', product.product_id)
        t.json_is('sample.mode', 'optional')
        t.json_is('sample.count', 3)
        t.json_is('sample.tags', ['sampling'])
        t.json_is('sample.condition.condition_type', 'constant_true')

        await t.post_ok('api_admin_samples_save',
                        json={
                            'sample_id': sample.sample_id,
                            'count': 2,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('sample.sample_id', sample.sample_id)
        t.json_is('sample.product_id', product.product_id)
        t.json_is('sample.mode', 'optional')
        t.json_is('sample.count', 2)
        t.json_is('sample.tags', ['sampling'])
        t.json_is('sample.condition.condition_type', 'constant_true')


async def test_bad_sampling_conditions(api, dataset, tap):
    with tap.plan(5):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role='store_admin', store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        await t.post_ok(
            'api_admin_samples_save',
            json={
                'product_id': '13',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'and',
                },
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


async def test_sampling_conditions(api, dataset, tap, uuid):
    with tap.plan(56, 'Создание сэмплов с разными условиями'):
        store = await dataset.store()
        product = await dataset.product(compnay_id=store.company_id)
        tap.ok(store, 'Store created')

        user = await dataset.user(role='admin', store=store)
        tap.ok(user, 'User created')

        t = await api(user=user)

        samples = [
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'total_price_above',
                    'total_price': '1234.56',

                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'group_present',
                    'group_id': '12',
                    'children': None,  # это поле должно быть проигнорировано
                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'product_present',
                    'product_id': '12',
                    'count': 3,
                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'product_present',
                    'product_id': '12',
                    'count': None,  # означает то же, что и 1
                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'and',
                    'children': [
                        {
                            'condition_type': 'total_price_above',
                            'total_price': '1234.56'
                        },
                        {
                            'condition_type': 'or',
                            'children': [
                                {
                                    'condition_type': 'group_present',
                                    'group_id': '213',
                                },
                                {
                                    'condition_type': 'group_present',
                                    'group_id': '7131',
                                },
                            ],
                        },
                    ],
                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
            {
                'product_id': product.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'tag_present',
                    'client_tag': 'some_tag0',

                },
                'company_id': store.company_id,
                'external_id': uuid(),
                'title': uuid(),
            },
        ]

        for i, s in enumerate(samples):
            await t.post_ok(
                'api_admin_samples_save',
                json=s,
            )
            t.status_is(200, diag=True)
            t.json_has('sample.sample_id')

            sample_id = t.res['json']['sample']['sample_id']
            sample = await ProductSample.load(sample_id)

            tap.eq(sample.company_id, user.company_id,
                   f'sample #{i}, company_id')
            tap.eq(sample.product_id, s['product_id'],
                   f'sample #{i}, product_id')
            tap.eq(sample.mode, s['mode'],
                   f'sample #{i}, mode')
            tap.eq(sample.count, s['count'],
                   f'sample #{i}, count')
            tap.eq(sample.tags, s['tags'],
                   f'sample #{i}, tags')
            tap.eq(sample.condition,
                   SamplingCondition(s['condition']),
                   f'sample #{i}, condition')


async def test_samples_with_ttl(api, dataset, tap, uuid):
    with tap.plan(12, 'Создание сэмплов с same_client_ttl'):
        store = await dataset.store()
        product1 = await dataset.product(company_id=store.company_id)
        product2 = await dataset.product(company_id=store.company_id)
        tap.ok(store, 'Store created')

        user = await dataset.user(role='admin', store=store)
        tap.ok(user, 'User created')

        t = await api(user=user)

        samples = [{
            'product_id': product1.product_id,
            'mode': 'required',
            'count': 1,
            'tags': [],
            'same_client_ttl': 10,
            'company_id': store.company_id,
            'external_id': uuid(),
            'title': uuid(),
        }, {
            'product_id': product2.product_id,
            'mode': 'optional',
            'count': 2,
            'tags': [],
            'same_client_ttl': 14,
            'company_id': store.company_id,
            'external_id': uuid(),
            'title': uuid(),
        }]

        for i, s in enumerate(samples):
            await t.post_ok(
                'api_admin_samples_save',
                json=s,
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('sample.sample_id')

            sample_id = t.res['json']['sample']['sample_id']
            sample = await ProductSample.load(sample_id)

            tap.eq(sample.same_client_ttl, s['same_client_ttl'],
                   f'ttl for sample {i}')


async def test_sample_with_date(api, dataset, tap, now, uuid):
    with tap.plan(8, 'Создание сэмпла с ограниченным сроком действия'):
        store = await dataset.store()
        product = await dataset.product(company_id=store.company_id)
        tap.ok(store, 'Store created')

        user = await dataset.user(role='admin', store=store)
        tap.ok(user, 'User created')

        t = await api(user=user)

        sample_data = {
            'product_id': product.product_id,
            'mode': 'required',
            'count': 1,
            'tags': [],
            # не храним микросекунды в базе (TIMESTAMP(0) WITH TIMEZONE )
            'dttm_start': now().replace(microsecond=0) + timedelta(days=1),
            'dttm_till': now().replace(microsecond=0) + timedelta(days=12),
            'company_id': store.company_id,
            'external_id': uuid(),
            'title': uuid(),
        }

        await t.post_ok(
            'api_admin_samples_save',
            json=sample_data,
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('sample.sample_id')

        sample_id = t.res['json']['sample']['sample_id']
        sample = await ProductSample.load(sample_id)

        date_res = sample['dttm_start']
        date_exp = sample_data['dttm_start'].astimezone(timezone.utc)
        tap.eq(date_res, date_exp, 'start date for sample')

        date_res = sample['dttm_till']
        date_exp = sample_data['dttm_till'].astimezone(timezone.utc)
        tap.eq(date_res, date_exp, 'till date for sample')


async def test_sampling_condition_nested(tap, dataset, api, uuid):
    with tap.plan(15):
        product = await dataset.product()
        t = await api(role='admin')

        external_id = uuid()
        title = uuid()
        await t.post_ok('api_admin_samples_save',
                        json={
                            'external_id': external_id,
                            'title': title,
                            'product_id': product.product_id,
                            'mode': 'optional',
                            'count': 2,
                            'tags': ['sampling'],
                            'condition': {
                                'condition_type': 'and',
                                'children': [
                                    {
                                        'condition_type': 'tag_present',
                                        'client_tag': 'tag1',
                                    }
                                ]
                            },
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('sample.sample_id')
        t.json_is('sample.product_id', product.product_id)
        t.json_is('sample.mode', 'optional')
        t.json_is('sample.count', 2)
        t.json_is('sample.tags', ['sampling'])
        t.json_is('sample.condition.condition_type', 'and')
        t.json_is('sample.condition.children.0.condition_type',
                  'tag_present')
        t.json_is('sample.condition.children.0.client_tag', 'tag1')
        sample_id = t.res['json']['sample']['sample_id']

        await t.post_ok('api_admin_samples_save',
                        json={
                            'external_id': external_id,
                            'title': title,
                            'product_id': product.product_id,
                            'mode': 'optional',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('sample.sample_id', sample_id, 'The same sample returned')
