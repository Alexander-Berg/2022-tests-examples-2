from stall.model.stash import Stash


# pylint: disable=too-many-locals
async def test_add_stores(tap, dataset, api, make_csv_str, job,
                          push_events_cache):
    with tap.plan(10):
        company = await dataset.company()
        sample1 = await dataset.sample(company_id=company.company_id)
        sample2 = await dataset.sample(company_id=company.company_id)
        sample3 = await dataset.sample(company_id=company.company_id)

        store1 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id,
                                                  sample2.sample_id])
        store2 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id,
                                                  sample2.sample_id,
                                                  sample3.sample_id])
        store3 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id])
        store4 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id,
                                                  sample2.sample_id])

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_remove_stores',
                        json={
                            'sample_id': sample2.sample_id,
                            'csv': make_csv_str(
                                ['external_id'],
                                [{'external_id': store1.external_id},
                                 {'external_id': store2.external_id},
                                 {'external_id': store3.external_id}],
                            ),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stash_id')

        stash = await Stash.load(t.res['json']['stash_id'])
        tap.ok(stash, 'stash loaded')
        await push_events_cache(stash, job_method='remove_sample_from_stores')

        task = await job.take()
        tap.ok(task, 'task taken')
        await job.call(task)

        await store1.reload()
        await store2.reload()
        await store3.reload()
        await store4.reload()

        tap.eq(
            sorted(store1.samples_ids),
            sorted([sample1.sample_id]),
            'Sample2 removed from store1',
        )
        tap.eq(
            sorted(store2.samples_ids),
            sorted([sample1.sample_id, sample3.sample_id]),
            'Sample2 removed from store2',
        )
        tap.eq(
            sorted(store3.samples_ids),
            sorted([sample1.sample_id]),
            'Samples in store3 did not changed',
        )
        tap.eq(
            sorted(store4.samples_ids),
            sorted([sample1.sample_id, sample2.sample_id]),
            'Samples in store4 did not changed',
        )
