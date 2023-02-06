from datetime import timedelta, timezone, datetime

import pytest

from stall.model.product import Product
from stall.model.product_sample import ProductSample
from stall.scripts.migrate_samples import migrate_samples
from stall.scripts.rename_samples import rename_samples


@pytest.fixture
async def product_sample(dataset):
    async def _product_sample(**kwargs):
        p = await dataset.product()
        kwargs.setdefault('product_id', p.product_id)
        kwargs.setdefault('mode', 'optional')
        kwargs.setdefault('count', 1)
        kwargs.setdefault('tags', ['sampling'])

        return ProductSample(kwargs)

    yield _product_sample


async def test_migrate(tap, dataset, product_sample):
    # pylint: disable=redefined-outer-name
    with tap.plan(58, 'Переносим сэмплы в отдельную таблицу'):
        start = datetime(2020, 10, 12, tzinfo=timezone.utc)
        samples = [
            {'mode': 'required', 'dttm_start': start},
            {'mode': 'optional', 'tags': ['packaging'],
             'dttm_start': start + timedelta(days=1)},
            {'mode': 'required', 'dttm_start': start + timedelta(days=2)},
            {'mode': 'required', 'tags': ['packaging'],
             'dttm_start': start + timedelta(days=3)},
            {'mode': 'required', 'dttm_start': start + timedelta(days=4)},
        ]
        samples = [await product_sample(**s) for s in samples]

        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store1.samples = samples[:2]
        await store1.save()

        store2 = await dataset.store(company=company)
        store2.samples = samples[2:]
        await store2.save()

        await migrate_samples(apply=True, companies=[company.company_id])

        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_start)

        tap.eq(len(db_samples), 5, 'Correct number (5) of samples written')

        for i, db_sample in enumerate(db_samples):
            tap.ok(db_sample.lsn, f'lsn present in sample #{i}')
            tap.ok(db_sample.serial, f'serial present in sample #{i}')
            tap.ok(db_sample.sample_id, f'sample_id present in sample #{i}')
            tap.ok(db_sample.external_id,
                   f'external_id present in sample #{i}')
            tap.eq(db_sample.company_id, company.company_id,
                   f'correct company in sample #{i}')
            tap.eq(db_sample.product_id, samples[i].product_id,
                   f'correct product in sample #{i}')
            tap.eq(db_sample.mode, samples[i].mode,
                   f'correct mode in sample #{i}')
            tap.eq(db_sample.count, samples[i].count,
                   f'correct count in sample #{i}')
            tap.eq(db_sample.tags, samples[i].tags,
                   f'correct tags in sample #{i}')
            tap.eq(db_sample.dttm_start, samples[i].dttm_start,
                   f'correct dttm_start in sample #{i}')

        samples_ids = [s.sample_id for s in db_samples]
        await store1.reload()
        tap.eq(store1.samples_ids, samples_ids[:2],
               'correct samples_ids in store1')

        await store2.reload()
        tap.eq(store2.samples_ids, samples_ids[2:],
               'correct samples_ids in store2')

        await rename_samples(apply=True, companies=[company.company_id])
        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_start)
        for i, db_sample in enumerate(db_samples):
            product = await Product.load(samples[i].product_id)
            start = '-inf'
            if db_sample.dttm_start:
                start = db_sample.dttm_start.isoformat()
            end = '+inf'
            if db_sample.dttm_till:
                end = db_sample.dttm_till.isoformat()
            tap.eq(db_sample.title, f'{product.title} ({start}, {end})',
                   f'correct title in sample #{i}')

async def test_squash_equal_samples(dataset, tap, product_sample):
    # pylint: disable=redefined-outer-name
    with tap.plan(25, 'Одинаковые сэмплы объединяются'):
        product1 = await dataset.product()
        product2 = await dataset.product()
        start = datetime(2020, 10, 12, tzinfo=timezone.utc)
        samples = [
            await product_sample(product_id=product1.product_id,
                                 dttm_start=start),
            await product_sample(product_id=product2.product_id,
                                 dttm_start=start + timedelta(days=1)),
            await product_sample(product_id=product1.product_id,
                                 dttm_start=start),
        ]

        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store1.samples = samples[:2]
        await store1.save()

        store2 = await dataset.store(company=company)
        store2.samples = samples[2:]
        await store2.save()

        await migrate_samples(apply=True, companies=[company.company_id])

        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_start)

        tap.eq(len(db_samples), 2, 'Correct number (2) of samples written')

        for i, db_sample in enumerate(db_samples):
            tap.ok(db_sample.lsn, f'lsn present in sample #{i}')
            tap.ok(db_sample.serial, f'serial present in sample #{i}')
            tap.ok(db_sample.sample_id, f'sample_id present in sample #{i}')
            tap.ok(db_sample.external_id,
                   f'external_id present in sample #{i}')
            tap.eq(db_sample.company_id, company.company_id,
                   f'correct company in sample #{i}')
            tap.eq(db_sample.product_id, samples[i].product_id,
                   f'correct product in sample #{i}')
            tap.eq(db_sample.mode, samples[i].mode,
                   f'correct mode in sample #{i}')
            tap.eq(db_sample.count, samples[i].count,
                   f'correct count in sample #{i}')
            tap.eq(db_sample.tags, samples[i].tags,
                   f'correct tags in sample #{i}')
            tap.eq(db_sample.dttm_start, samples[i].dttm_start,
                   f'correct dttm_start in sample #{i}')

        await store1.reload()
        tap.eq(store1.samples_ids,
               [db_samples[0].sample_id, db_samples[1].sample_id],
               'Correct samples_ids in store1')
        await store2.reload()
        tap.eq(store2.samples_ids, [db_samples[0].sample_id],
               'Correct samples_ids in store2')

        await rename_samples(apply=True, companies=[company.company_id])
        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_start)
        for i, db_sample in enumerate(db_samples):
            product = await Product.load(samples[i].product_id)
            start = '-inf'
            if db_sample.dttm_start:
                start = db_sample.dttm_start.isoformat()
            end = '+inf'
            if db_sample.dttm_till:
                end = db_sample.dttm_till.isoformat()
            tap.eq(db_sample.title, f'{product.title} ({start}, {end})',
                   f'correct title in sample #{i}')

async def test_disable_old_samples(tap, dataset, product_sample, now):
    # pylint: disable=redefined-outer-name
    with tap.plan(36, 'Cэмплы, у которых dttm_till в прошлом, выключаются'):
        samples = [
            await product_sample(
                mode='required',
                dttm_till=now().replace(microsecond=0) - timedelta(days=3)),
            await product_sample(
                mode='optional',
                dttm_till=now().replace(microsecond=0) - timedelta(days=2)),
            await product_sample(
                mode='optional',
                dttm_till=now().replace(microsecond=0) - timedelta(days=1)),
            await product_sample(
                mode='disabled',
                dttm_till=now().replace(microsecond=0) + timedelta(days=1)),
        ]

        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store1.samples = samples[:2]
        await store1.save()

        store2 = await dataset.store(company=company)
        store2.samples = samples[2:]
        await store2.save()

        store3 = await dataset.store(company=company)
        store3.samples = [samples[3]]
        await store3.save()

        await migrate_samples(apply=True, companies=[company.company_id])

        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_till)

        tap.eq(len(db_samples), 4, 'Correct number (4) of samples written')

        for i, db_sample in enumerate(db_samples):
            tap.ok(db_sample.lsn, f'lsn present in sample #{i}')
            tap.ok(db_sample.serial, f'serial present in sample #{i}')
            tap.ok(db_sample.sample_id, f'sample_id present in sample #{i}')
            tap.ok(db_sample.external_id,
                   f'external_id present in sample #{i}')
            tap.eq(db_sample.company_id, company.company_id,
                   f'correct company in sample #{i}')
            tap.eq(db_sample.mode, 'disabled',
                   f'sample #{i} disabled')
            tap.eq(db_sample.dttm_till, samples[i].dttm_till,
                   f'correct dttm_till in sample #{i}')

        await store1.reload()
        tap.eq(store1.samples_ids, [], 'empty samples_ids in store1')

        await store2.reload()
        tap.eq(store2.samples_ids, [], 'empty samples_ids in store2')

        await store3.reload()
        tap.eq(store3.samples_ids, [], 'empty samples_ids in store3')

        await rename_samples(apply=True, companies=[company.company_id])

        db_samples = await ProductSample.list(
            by='full',
            conditions=('company_id', company.company_id))
        db_samples = sorted(db_samples.list, key=lambda x: x.dttm_till)
        for i, db_sample in enumerate(db_samples):
            product = await Product.load(samples[i].product_id)
            start = '-inf'
            if db_sample.dttm_start:
                start = db_sample.dttm_start.isoformat()
            end = '+inf'
            if db_sample.dttm_till:
                end = db_sample.dttm_till.isoformat()
            tap.eq(db_sample.title, f'{product.title} ({start}, {end})',
                   f'correct title in sample #{i}')
