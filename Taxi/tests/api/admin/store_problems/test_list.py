
class DictWithEnter(dict):
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass


async def generate_problems(dataset):
    my_company = await dataset.company()
    other_company = await dataset.company()

    my_cluster = await dataset.cluster()
    my_company_cluster = await dataset.cluster()
    other_cluster = await dataset.cluster()

    my_store = await dataset.store(
        company=my_company,
        cluster=my_cluster,
    )
    my_cluster_store = await dataset.store(
        company=my_company,
        cluster=my_cluster,
    )
    other_cluster_store = await dataset.store(
        company=my_company,
        cluster=my_company_cluster,
    )
    other_company_store = await dataset.store(
        company=other_company,
        cluster=other_cluster,
    )

    my_supervisor = await dataset.user(
        role='supervisor', store=my_store,
    )
    my_company_supervisor = await dataset.user(
        role='supervisor', store=other_cluster_store,
    )
    other_company_supervisor = await dataset.user(
        role='supervisor', store=other_company_store,
    )

    await dataset.store_problem(
        store=my_store,
        supervisor_id=my_supervisor.user_id,
    )
    await dataset.store_problem(
        store=my_cluster_store,
        supervisor_id=my_supervisor.user_id,
    )
    await dataset.store_problem(
        store=other_cluster_store,
        supervisor_id=my_company_supervisor.user_id,
    )
    await dataset.store_problem(
        store=other_company_store,
        supervisor_id=other_company_supervisor.user_id,
    )

    return {
        'my_store': my_store,
        'my_cluster_store': my_cluster_store,
        'other_cluster_store': other_cluster_store,
        'other_company_store': other_company_store,
    }, {
        'my_supervisor': my_supervisor,
        'my_company_supervisor': my_company_supervisor,
        'other_company_supervisor': other_company_supervisor,
    }


async def test_empty(api, tap, dataset):
    with tap.plan(5, 'Тестируем пустой список'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': store.cluster_id,
                'store_id': store.store_id,
            }
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is('store_problems', [], 'Пустой список')
        t.json_is('cursor', None, 'Пустой курсор')


async def test_not_empty(api, tap, dataset, uuid):
    with tap.plan(9, 'Тестируем список'):
        store = await dataset.store()
        store_problem_1 = await dataset.store_problem(
            store=store,
            reason='count',
            details=[{
                "reason": 'count',
                "order_ids": [],
                "count": 10,
                "count_threshold": 2
            }],
        )
        store_problem_2 = await dataset.store_problem(
            store=store,
            details=[{
                'reason': 'duration_total',
                'order_id': uuid(),
                'duration': 10,
                'duration_threshold': 5,
            }],
        )
        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': store.cluster_id,
                'store_id': store.store_id
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_hasnt('store_problems.2')
        t.json_is('cursor', None, 'Пустой курсор')

        store_problems = {
            it['store_problem_id']: DictWithEnter(it)
            for it in t.res['json']['store_problems']
        }
        with store_problems[store_problem_1.store_problem_id] as problem:
            tap.ok(problem, 'Первая проблема есть')
            tap.eq(
                problem['details'][0]['reason'],
                'count',
                'Верная причина первой проблемы'
            )
        with store_problems[store_problem_2.store_problem_id] as problem:
            tap.ok(problem, 'Вторая проблема есть')
            tap.eq(
                problem['details'][0]['reason'],
                'duration_total',
                'Верная причина второй проблемы'
            )


async def test_cursor(api, tap, dataset, cfg):
    with tap.plan(11, 'Тестируем список c курсором'):
        cfg.set('cursor.limit', 3)
        store = await dataset.store()

        for _ in range(5):
            await dataset.store_problem(store=store)

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': store.cluster_id,
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('store_problems.2')
        t.json_hasnt('store_problems.3')

        cursor = t.res['json']['cursor']
        tap.ok(cursor, 'Курсор есть')

        tap.note('Вторая итерация')
        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': store.cluster_id,
                'store_id': store.store_id,
                'cursor': cursor,
            },
        )
        t.json_is('code', 'OK', 'code')
        t.json_has('store_problems.1')
        t.json_hasnt('store_problems.2')
        t.json_is('cursor', None, 'Пустой курсор')


async def test_permit(api, tap, dataset):
    with tap.plan(7, 'Загрузка данных по пермиту'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')
        await dataset.store_problem(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': store.cluster_id,
                'store_id': store.store_id,
            },
        )
        t.status_is(403, diag=True)

        with user.role as role:
            tap.note('Добавим пермит и попробуем ещё раз')
            role.add_permit('store_problems_seek', True)
            await t.post_ok(
                'api_admin_store_problems_list',
                json={
                    'cluster_id': store.cluster_id,
                    'store_id': store.store_id,
                },
            )
            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'code')
            t.json_has('store_problems.0')
            t.json_hasnt('store_problems.1')


async def test_other_store_id(api, tap, dataset):
    with tap.plan(8, 'Нельзя посмотреть проблемы в чужой лавке'):
        stores, _ = await generate_problems(dataset)
        user = await dataset.user(store=stores['my_store'], role='admin')
        with user.role as role:
            role.add_permit('out_of_company', False)
            t = await api(user=user)
            await t.post_ok(
                'api_admin_store_problems_list',
                json={
                    'cluster_id': stores['other_company_store'].cluster_id,
                    'store_id': stores['other_company_store'].store_id,
                },
            )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        prob = {
            it['store_id']: it for it in t.res['json']['store_problems']
        }
        tap.eq(len(prob), 0, 'Нет лишних проблем')
        tap.not_in_ok(
            stores['my_store'].store_id, prob, 'my_store'
        )
        tap.not_in_ok(
            stores['my_cluster_store'].store_id, prob, 'my_cluster_store'
        )
        tap.not_in_ok(
            stores['other_cluster_store'].store_id, prob, 'other_cluster_store'
        )
        tap.not_in_ok(
            stores['other_company_store'].store_id, prob, 'other_company_store'
        )


async def test_cluster_id(api, tap, dataset):
    with tap.plan(8, 'Смотрим проблемы по чужому кластеру'):
        stores, _ = await generate_problems(dataset)
        user = await dataset.user(store=stores['my_store'], role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': stores['other_cluster_store'].cluster_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        prob = {
            it['store_id']: it for it in t.res['json']['store_problems']
        }
        tap.eq(len(prob), 1, 'Нет лишних проблем')
        tap.not_in_ok(
            stores['my_store'].store_id, prob, 'my_store'
        )
        tap.not_in_ok(
            stores['my_cluster_store'].store_id, prob, 'my_cluster_store'
        )
        tap.in_ok(
            stores['other_cluster_store'].store_id, prob, 'other_cluster_store'
        )
        tap.not_in_ok(
            stores['other_company_store'].store_id, prob, 'other_company_store'
        )


async def test_supervisor_id(api, tap, dataset):
    with tap.plan(8, 'Смотрим проблемы по супервизору'):
        stores, supervisors = await generate_problems(dataset)
        user = await dataset.user(store=stores['my_store'], role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': stores['my_store'].cluster_id,
                'supervisor_id': supervisors['my_supervisor'].user_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        prob = {
            it['store_id']: it for it in t.res['json']['store_problems']
        }
        tap.eq(len(prob), 2, 'Нет лишних проблем')
        tap.in_ok(
            stores['my_store'].store_id, prob, 'my_store'
        )
        tap.in_ok(
            stores['my_cluster_store'].store_id, prob, 'my_cluster_store'
        )
        tap.not_in_ok(
            stores['other_cluster_store'].store_id, prob, 'other_cluster_store'
        )
        tap.not_in_ok(
            stores['other_company_store'].store_id, prob, 'other_company_store'
        )

async def test_empty_supervisor_id(api, tap, dataset):
    with tap.plan(8, 'Смотрим проблемы по супервизору'):
        stores, _ = await generate_problems(dataset)
        user = await dataset.user(store=stores['my_store'], role='admin')

        await dataset.store_problem(
            store=stores['my_store'],
            supervisor_id=None,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_store_problems_list',
            json={
                'cluster_id': stores['my_store'].cluster_id,
                'supervisor_id': 'EMPTY::',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        prob = {
            it['store_id']: it for it in t.res['json']['store_problems']
        }
        tap.eq(len(t.res['json']['store_problems']), 1, 'Нет лишних проблем')
        tap.in_ok(
            stores['my_store'].store_id, prob, 'my_store'
        )
        tap.not_in_ok(
            stores['my_cluster_store'].store_id, prob, 'my_cluster_store'
        )
        tap.not_in_ok(
            stores['other_cluster_store'].store_id, prob, 'other_cluster_store'
        )
        tap.not_in_ok(
            stores['other_company_store'].store_id, prob, 'other_company_store'
        )
