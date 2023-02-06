from stall.model.stash import Stash


# pylint: disable=too-many-locals
async def test_add_stores(tap, dataset, api, make_csv_str, job,
                          push_events_cache):
    with tap.plan(8):
        company = await dataset.company()
        sample1 = await dataset.sample(company_id=company.company_id)
        sample2 = await dataset.sample(company_id=company.company_id)
        store1 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample1.sample_id])
        store2 = await dataset.store(company_id=company.company_id,
                                     samples_ids=[sample2.sample_id])
        sample = await dataset.sample(company_id=company.company_id)

        t = await api(role='admin')

        await t.post_ok('api_admin_samples_add_stores',
                        json={
                            'sample_id': sample.sample_id,
                            'csv': make_csv_str(
                                ['external_id'],
                                [{'external_id': store1.external_id},
                                 {'external_id': store2.external_id}],
                            ),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stash_id')

        stash = await Stash.load(t.res['json']['stash_id'])
        tap.ok(stash, 'stash loaded')
        await push_events_cache(stash, job_method='add_sample_to_stores')

        task = await job.take()
        tap.ok(task, 'task taken')
        await job.call(task)

        await store1.reload()
        await store2.reload()

        tap.eq(
            sorted(store1.samples_ids),
            sorted([sample.sample_id, sample1.sample_id]),
            'Samples in store1',
        )
        tap.eq(
            sorted(store2.samples_ids),
            sorted([sample.sample_id, sample2.sample_id]),
            'Samples in store2',
        )


async def test_another_company(tap, dataset, api, make_csv_str, job, uuid,
                               push_events_cache):
    with tap.plan(9):
        company1 = await dataset.company()
        company2 = await dataset.company()
        sample1 = await dataset.sample(company_id=company1.company_id)
        sample2 = await dataset.sample(company_id=company2.company_id)
        store1 = await dataset.store(company_id=company1.company_id,
                                     samples_ids=[sample1.sample_id])
        store2 = await dataset.store(company_id=company2.company_id,
                                     samples_ids=[sample2.sample_id],
                                     user_id=uuid())
        old_user_id = store2.user_id
        sample = await dataset.sample(company_id=company1.company_id)

        user = await dataset.user(role='admin')
        t = await api(user=user)

        await t.post_ok('api_admin_samples_add_stores',
                        json={
                            'sample_id': sample.sample_id,
                            'csv': make_csv_str(
                                ['external_id'],
                                [{'external_id': store1.external_id},
                                 {'external_id': store2.external_id}],
                            ),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stash_id')
        stash = await Stash.load(t.res['json']['stash_id'])
        await push_events_cache(stash, job_method='add_sample_to_stores')

        task = await job.take()
        tap.ok(task, 'task taken')
        await job.call(task)

        await store1.reload()
        await store2.reload()

        tap.eq(
            sorted(store1.samples_ids),
            sorted([sample.sample_id, sample1.sample_id]),
            'Samples in store1',
        )
        tap.eq(store1.user_id, user.user_id,
               'user_id of updated store changed')
        tap.eq(
            sorted(store2.samples_ids),
            sorted([sample2.sample_id]),
            'Samples in store2 did not change (another company)',
        )
        tap.eq(store2.user_id, old_user_id,
               'user_id of store2 did not change')


async def test_out_of_company(tap, dataset, api, make_csv_str):
    with tap.plan(3):
        company1 = await dataset.company()
        company2 = await dataset.company()

        sample = await dataset.sample(company_id=company2.company_id)
        store = await dataset.store(company_id=company1.company_id)

        user = await dataset.user(role='admin',
                                  company_id=company1.company_id)

        with user.role as role:
            role.remove_permit('out_of_company')
            t = await api(user=user)

            await t.post_ok('api_admin_samples_add_stores',
                            json={
                                'sample_id': sample.sample_id,
                                'csv': make_csv_str(
                                    ['external_id'],
                                    [{'external_id': store.external_id}],
                                ),
                            })
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
