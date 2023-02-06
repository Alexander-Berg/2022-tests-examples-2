
async def test_one(api, tap, dataset):
    with tap.plan(4, 'Загрузим проблему'):
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
            'api_admin_store_problems_load',
            json={
                'store_problem_id': store_problem.store_problem_id
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('store_problem')


async def test_several(api, tap, dataset):
    with tap.plan(6, 'Загрузим проблему'):
        store = await dataset.store()
        store_problem_1 = await dataset.store_problem(store=store)
        store_problem_2 = await dataset.store_problem(store=store)

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_store_problems_load',
            json={
                'store_problem_id': [
                    store_problem_1.store_problem_id,
                    store_problem_2.store_problem_id,
                ]
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('store_problem.0')
        t.json_has('store_problem.1')
        t.json_hasnt('store_problem.2')


async def test_permit(api, tap, dataset):
    with tap.plan(6, 'Проверка загрузки по пермиту'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')
        store_problem = await dataset.store_problem(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_load',
            json={
                'store_problem_id': store_problem.store_problem_id,
            },
        )
        t.status_is(403, diag=True)

        tap.note('Добавим пермит и попробуем ещё раз')
        with user.role as role:
            role.add_permit('store_problems_load', True)
            await t.post_ok(
                'api_admin_store_problems_load',
                json={
                    'store_problem_id': store_problem.store_problem_id,
                },
            )
            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'code')
            t.json_has('store_problem')


async def test_other_store(api, tap, dataset):
    with tap.plan(2, 'Нельзя загрузить проблемы из чужого стора'):
        store = await dataset.store()
        not_my_store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        with user.role as role:
            role.add_permit('out_of_company', False)

            store_problem = await dataset.store_problem(store=not_my_store)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_store_problems_load',
                json={
                    'store_problem_id': store_problem.store_problem_id,
                },
            )
            t.status_is(403, diag=True)


async def test_one_from_other_store(api, tap, dataset):
    with tap.plan(
            2,
            'Если хотя бы одна проблема из чужого стора, то тоже нельзя'
    ):
        store = await dataset.store()
        not_my_store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        with user.role as role:
            role.add_permit('out_of_company', False)

            store_problem_1 = await dataset.store_problem(store=store)
            store_problem_2 = await dataset.store_problem(store=not_my_store)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_store_problems_load',
                json={
                    'store_problem_id': [
                        store_problem_1.store_problem_id,
                        store_problem_2.store_problem_id,
                    ]
                },
            )
            t.status_is(403, diag=True)


async def test_not_found(api, tap, dataset, uuid):
    with tap.plan(2, 'Загрузка несуществующей проблемы'):
        store = await dataset.store()
        await dataset.store_problem(store=store)

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_load',
            json={
                'store_problem_id': uuid(),
            },
        )
        t.status_is(403, diag=True)
