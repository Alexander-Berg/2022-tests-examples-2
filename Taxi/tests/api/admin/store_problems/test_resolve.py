
async def test_resolve(api, tap, dataset):
    with tap.plan(5, 'Решим проблему'):
        store = await dataset.store()
        store_problem = await dataset.store_problem(
            store=store,
            is_resolved=False,
            reason='count',
            details=[{
                "reason": 'count',
                "order_ids": [],
                "count": 10,
                "count_threshold": 2
            }],
        )

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_store_problems_resolve',
            json={
                'store_problem_id': store_problem.store_problem_id
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('store_problem')
        t.json_is('store_problem.is_resolved', True, 'resolved')


async def test_permit(api, tap, dataset):
    with tap.plan(6, 'Решение проблемы по пермиту'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')
        store_problem = await dataset.store_problem(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_resolve',
            json={
                'store_problem_id': store_problem.store_problem_id,
            },
        )
        t.status_is(403, diag=True)

        tap.note('Добавим пермит и попробуем ещё раз')
        with user.role as role:
            role.add_permit('store_problems_save', True)
            await t.post_ok(
                'api_admin_store_problems_resolve',
                json={
                    'store_problem_id': store_problem.store_problem_id,
                },
            )
            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'code')
            t.json_has('store_problem')


async def test_other_store(api, tap, dataset):
    with tap.plan(2, 'В чужом сторе нельзя решать проблемы'):
        store = await dataset.store()
        not_my_store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        with user.role as role:
            role.add_permit('out_of_company', False)

            store_problem = await dataset.store_problem(store=not_my_store)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_store_problems_resolve',
                json={
                    'store_problem_id': store_problem.store_problem_id,
                },
            )
            t.status_is(403, diag=True)


async def test_not_found(api, tap, dataset, uuid):
    with tap.plan(2, 'Решение не существующей проблемы'):
        store = await dataset.store()
        await dataset.store_problem(store=store)

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_resolve',
            json={
                'store_problem_id': uuid(),
            },
        )
        t.status_is(403, diag=True)
