from stall.model.product_sample import ProductSample
from stall.model.store import Store


async def test_samples(tap, dataset):
    with tap.plan(4):
        store = await dataset.store(
            samples=[
                {'product_id': '0'},
                {'product_id': '1', 'mode': 'disabled'},
                {'product_id': '2', 'mode': 'required', 'count': 1},
                {
                    'product_id': '2',
                    'mode': 'required',
                    'count': 1,
                    'tags': ['packaging'],
                },
            ]
        )

        tap.eq(len(store.samples), 4, 'samples for store')
        tap.isa_ok(store.samples[0], ProductSample, 'Correct sample type')
        tap.ok(await store.save(), 'Store saved')

        loaded = await Store.load(store.store_id)
        tap.eq(
            store.samples, loaded.samples, 'With correct samples'
        )


async def test_sampling_conditions(tap, dataset):
    with tap.plan(4):
        store = await dataset.store(
            samples=[
                {
                    'product_id': 'product_id_1',
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
                                'condition_type': 'group_present',
                                'group_id': 'group_id_2',
                            },
                        ],
                    },
                },
                {
                    'product_id': 'product_id_2',
                    'mode': 'optional',
                    'count': 1,
                    'tags': ['sampling'],
                    'condition': {
                        'condition_type': 'total_price_above',
                        'total_price': '321.12'
                    },
                },
                {
                    'product_id': 'product_id_3',
                    'mode': 'optional',
                    'count': 1,
                    'tags': ['sampling'],
                    'condition': {
                        'condition_type': 'group_present',
                        'group_id': 'group_id_3',
                    },
                },
            ],
        )

        tap.eq(len(store.samples), 3, 'samples for store')
        tap.isa_ok(store.samples[0], ProductSample, 'Correct sample type')
        tap.ok(await store.save(), 'Store saved')

        loaded = await Store.load(store.store_id)
        tap.eq(
            store.samples, loaded.samples, 'With correct samples'
        )


async def test_load_samples(tap, dataset, uuid):
    with tap.plan(19, 'Получение сэмплов склада'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        samples_data = [
            {
                'product_id': product1.product_id,
                'mode': 'optional',
                'count': 1,
                'tags': ['packaging'],
                'title': uuid(),
            },
            {
                'product_id': product2.product_id,
                'mode': 'disabled',
                'count': 2,
                'tags': ['sampling'],
                'title': uuid(),
            },
            {
                'product_id': product3.product_id,
                'mode': 'required',
                'count': 3,
                'tags': ['sampling'],
                'title': uuid(),
            },
        ]
        product_samples = [await dataset.sample(**s) for s in samples_data]
        store = await dataset.store(
            samples_ids=[s.sample_id for s in product_samples])

        loaded_samples = await store.load_samples()
        tap.eq(len(loaded_samples), 3, 'samples for store')

        for i, sample in enumerate(loaded_samples):
            tap.isa_ok(sample, ProductSample, f'sample #{i}')
            tap.eq(sample.product_id, product_samples[i]['product_id'],
                   'product_id')
            tap.eq(sample.mode, product_samples[i]['mode'], 'mode')
            tap.eq(sample.count, product_samples[i]['count'], 'count')
            tap.eq(sample.tags, product_samples[i]['tags'], 'tags')
            tap.eq(sample.title, product_samples[i]['title'], 'title')
