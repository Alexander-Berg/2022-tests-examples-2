async def test_success(tap, dataset, api, job, push_events_cache):
    with tap.plan(15, 'Успешный запуск тригера обновлений'):
        t = await api(role='token:web.external.tokens.0')
        ass_con_1 = await dataset.assortment_contractor()
        ass_con_2 = await dataset.assortment_contractor()
        await t.post_ok(
            'api_integration_assortment_contractors_trigger_update',
            json={
                'assortment_keys': [
                    {
                        'store_id': ass_con_1.store_id,
                        'contractor_id': ass_con_1.contractor_id
                    },
                    {
                        'store_id': ass_con_2.store_id,
                        'contractor_id': ass_con_2.contractor_id
                    }
                ],
                'job_tube': job.name,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        stash_id = t.res['json']['stash_id']

        stash = await dataset.Stash.load(stash_id)
        tap.ok(stash, 'Стэш появился')
        tap.eq(
            stash.value['assortment_keys'],
            [
                {
                    'store_id': ass_con_1.store_id,
                    'contractor_id': ass_con_1.contractor_id
                },
                {
                    'store_id': ass_con_2.store_id,
                    'contractor_id': ass_con_2.contractor_id
                }
            ],
            'Ключики там'
        )
        tap.eq(
            stash.value['job_tube'],
            job.name,
            'Очередь передали правильную'
        )
        await push_events_cache(stash)
        task = await job.take()
        tap.eq(
            task.callback,
            'stall.model.assortment_contractor.job_trigger_update',
            'Колбэк правильный'
        )
        tap.eq(
            task.data.get('stash_id'),
            stash.stash_id,
            'Стэш прикопан правильный'
        )
        await job.call(task)
        stash = await dataset.Stash.load(stash_id)
        tap.ok(stash is None, 'Стэш пропал')
        task_1 = await job.take()
        task_2 = await job.take()

        if task_1.data.get('contractor_id') == ass_con_2.contractor_id:
            task_1, task_2 = task_2, task_1

        tap.eq(
            task_1.callback,
            'stall.model.assortment_contractor.'
            'job_update_assortment_contractor',
            'Правильный колбэк 1'
        )
        tap.eq(
            task_1.data.get('contractor_id'),
            ass_con_1.contractor_id,
            'Правильный контрактор'
        )
        tap.eq(
            task_1.data.get('store_id'),
            ass_con_1.store_id,
            'Правильный склад'
        )
        tap.eq(
            task_2.callback,
            'stall.model.assortment_contractor.'
            'job_update_assortment_contractor',
            'Правильный колбэк 2'
        )
        tap.eq(
            task_2.data.get('contractor_id'),
            ass_con_2.contractor_id,
            'Правильный контрактор'
        )
        tap.eq(
            task_2.data.get('store_id'),
            ass_con_2.store_id,
            'Правильный склад'
        )


async def test_wrong_company(tap, api, dataset):
    with tap.plan(3, 'Пытаемся достать чужую компанию'):
        company = await dataset.company()
        t = await api(token=company.token)
        store = await dataset.store(company_id=company.company_id)
        ass_con_1 = await dataset.assortment_contractor(
            store_id=store.store_id)
        ass_con_2 = await dataset.assortment_contractor()
        await t.post_ok(
            'api_integration_assortment_contractors_trigger_update',
            json={
                'assortment_keys': [
                    {
                        'store_id': ass_con_1.store_id,
                        'contractor_id': ass_con_1.contractor_id
                    },
                    {
                        'store_id': ass_con_2.store_id,
                        'contractor_id': ass_con_2.contractor_id
                    }
                ],
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_missing_store(tap, api, dataset, uuid):
    with tap.plan(3, 'Пытаемся достать несуществующий склад'):
        t = await api(role='token:web.external.tokens.0')
        ass_con_1 = await dataset.assortment_contractor()
        await t.post_ok(
            'api_integration_assortment_contractors_trigger_update',
            json={
                'assortment_keys': [
                    {
                        'store_id': ass_con_1.store_id,
                        'contractor_id': ass_con_1.contractor_id
                    },
                    {
                        'store_id': uuid(),
                        'contractor_id': uuid()
                    }
                ]
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
