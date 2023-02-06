import argparse
from datetime import timedelta
from scripts.cron.clean_old_samples import main


# pylint: disable=too-many-locals
async def test_clean_old_samples(tap, dataset, now, cfg):
    with tap.plan(4, 'просроченные сэмплы должны удалиться'):
        sample1 = await dataset.product()
        sample2 = await dataset.product()
        sample3 = await dataset.product()
        sample4 = await dataset.product()
        sample5 = await dataset.product()
        cfg.set('business.sampling.removal_after_dttm_till', 7)

        store = await dataset.store(
            samples=[
                {
                    'product_id': sample1.product_id,
                    'mode': 'optional',
                    'count': 2,
                    'tags': ['packaging'],
                    'dttm_till': now() - timedelta(days=8),
                },
                {
                    'product_id': sample2.product_id,
                    'mode': 'optional',
                    'count': 3,
                    'tags': ['sampling'],
                    'dttm_till': now() + timedelta(days=35),
                },
                {
                    'product_id': sample3.product_id,
                    'mode': 'optional',
                    'count': 4,
                    'tags': ['sampling'],
                },
                {
                    'product_id': sample4.product_id,
                    'mode': 'optional',
                    'count': 7,
                    'tags': ['sampling'],
                    'dttm_till': now(),
                },
                {
                    'product_id': sample5.product_id,
                    'mode': 'optional',
                    'count': 7,
                    'tags': ['sampling'],
                    'dttm_till': now() - timedelta(days=6),
                },
            ],
        )
        tap.eq_ok(len(store.samples), 5,
                  'Создано необходимое количество сэмплов')
        args = argparse.Namespace(apply=True, store_id=store.store_id)
        await main(args=args)
        await store.reload()
        fresh_samples_id = [sample2.product_id, sample3.product_id,
                            sample4.product_id, sample5.product_id]

        tap.eq_ok(len(store.samples), 4, 'Удалены устаревшие сэмплы')
        list_sample_product_id = []
        for sample in store.samples:
            list_sample_product_id.append(sample['product_id'])
        tap.eq_ok(list_sample_product_id, fresh_samples_id,
                  'Удалены нужные сэплы')
        tap.eq(store.samples_ids, [], 'samples_ids не изменился')


async def test_error_store_id(tap):
    args = argparse.Namespace(apply=True, store_id='123')
    with tap.raises(AssertionError, 'Склад с переданным id не существует'):
        await main(args=args)


async def test_clean_old_samples_ids(tap, dataset, now, cfg):
    with tap.plan(3, 'просроченные сэмплы должны удалиться'):
        sample1 = await dataset.product()
        sample2 = await dataset.product()
        sample3 = await dataset.product()
        sample4 = await dataset.product()
        sample5 = await dataset.product()
        cfg.set('business.sampling.removal_after_dttm_till', 7)

        samples_data = [
            {
                'product_id': sample1.product_id,
                'mode': 'optional',
                'count': 2,
                'tags': ['packaging'],
                'dttm_till': now() - timedelta(days=8),
            },
            {
                'product_id': sample2.product_id,
                'mode': 'optional',
                'count': 3,
                'tags': ['sampling'],
                'dttm_till': now() + timedelta(days=35),
            },
            {
                'product_id': sample3.product_id,
                'mode': 'optional',
                'count': 4,
                'tags': ['sampling'],
            },
            {
                'product_id': sample4.product_id,
                'mode': 'optional',
                'count': 7,
                'tags': ['sampling'],
                'dttm_till': now(),
            },
            {
                'product_id': sample5.product_id,
                'mode': 'optional',
                'count': 7,
                'tags': ['sampling'],
                'dttm_till': now() - timedelta(days=6),
            },
        ]
        samples_ids = [(await dataset.sample(**s)).sample_id
                       for s in samples_data]

        store = await dataset.store(samples_ids=samples_ids,
                                    samples=samples_data)
        tap.eq_ok(len(store.samples_ids), 5,
                  'Создано необходимое количество сэмплов')
        args = argparse.Namespace(apply=True, store_id=store.store_id)
        await main(args=args)
        await store.reload()
        fresh_samples_id = [sample2.product_id, sample3.product_id,
                            sample4.product_id, sample5.product_id]

        tap.eq_ok(len(store.samples_ids), 4, 'Удалены устаревшие сэмплы')
        list_sample_product_id = []
        for sample in await store.load_samples():
            list_sample_product_id.append(sample['product_id'])
        tap.eq_ok(list_sample_product_id, fresh_samples_id,
                  'Удалены нужные сэплы')
