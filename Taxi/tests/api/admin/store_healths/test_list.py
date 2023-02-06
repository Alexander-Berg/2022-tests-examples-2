import pytest


async def generate_health(dataset):
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

    supervisor = await dataset.user(
        role='supervisor', store=my_store,
    )

    await dataset.store_health(
            store=my_store,
            supervisor_id=supervisor.user_id,
            recalculate=True,
        )

    for store in [
            my_cluster_store,
            other_cluster_store,
            other_company_store,
    ]:
        await dataset.store_health(
            store=store,
            recalculate=True,
        )

    return {
        'my_store': my_store,
        'my_cluster_store': my_cluster_store,
        'other_cluster_store': other_cluster_store,
        'other_company_store': other_company_store,
    }

async def test_companies(tap, api, dataset):
    with tap.plan(12, 'Доступ к здоровью своей компании'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_company', False)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_companies', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'company',
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('store_healths', 'OK')
            t.json_has('store_healths.0')
            t.json_is('store_healths.0.entity', 'company')
            t.json_is(
                'store_healths.0.entity_id', stores['my_store'].company_id
            )
            t.json_is(
                'store_healths.0.company_id', stores['my_store'].company_id
            )
            t.json_is('store_healths.0.cluster_id', None)
            t.json_is('store_healths.0.store_id', None)
            t.json_hasnt('store_healths.1')


async def test_companies_all(tap, api, dataset):
    with tap.plan(7, 'Доступ к здоровью всех компаний'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_company', True)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_companies', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'company',
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('store_healths', 'OK')
            t.json_has('store_healths.0')
            t.json_has('store_healths.1')


@pytest.mark.parametrize(
    'permits',
    (
        (
            ('out_of_company', True),
            ('store_healths_seek', False),
            ('store_healths_companies', True),
        ),
        (
            ('out_of_company', True),
            ('store_healths_seek', True),
            ('store_healths_companies', False),
        ),
    )
)
async def test_companies_bad(tap, api, dataset, permits):
    with tap.plan(3, 'Проблемы с доступом'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            for permit in permits:
                role.add_permit(*permit)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'company',
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_clusters_other_company(tap, api, dataset):
    with tap.plan(3, 'Доступ к здоровью кластера в чужой компании'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_company', False)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_clusters', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'cluster',
                    'company_id': stores['other_company_store'].company_id,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize(
    'permits',
    (
        (
            ('out_of_company', True),
            ('store_healths_seek', False),
            ('store_healths_clusters', True),
        ),
        (
            ('out_of_company', True),
            ('store_healths_seek', True),
            ('store_healths_clusters', False),
        ),
    )
)
async def test_clusters_bad(tap, api, dataset, permits):
    with tap.plan(3, 'Проблемы с доступом'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            for permit in permits:
                role.add_permit(*permit)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'cluster',
                    'company_id': stores['my_store'].company_id,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_supervisors(tap, api, dataset):
    with tap.plan(15, 'Доступ к здоровью супервизора по кластеру лавки'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_store', False)
            role.add_permit('out_of_company', False)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_stores', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'supervisor',
                    'company_id': stores['my_store'].company_id,
                    'cluster_id': stores['my_store'].cluster_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('store_healths', 'OK')
            t.json_has('store_healths.0')
            t.json_is('store_healths.0.entity', 'supervisor')
            t.json_is(
                'store_healths.0.company_id', stores['my_store'].company_id
            )
            t.json_is(
                'store_healths.0.cluster_id', stores['my_store'].cluster_id
            )
            t.json_is('store_healths.0.store_id', None)
            t.json_is('store_healths.1.entity', 'supervisor')
            t.json_is(
                'store_healths.1.company_id', stores['my_store'].company_id
            )
            t.json_is(
                'store_healths.1.cluster_id', stores['my_store'].cluster_id
            )
            t.json_is('store_healths.1.store_id', None)
            t.json_hasnt('store_healths.2')


async def test_stores(tap, api, dataset):
    with tap.plan(12, 'Доступ к здоровью своей лавки'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'], role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_store', False)
            role.add_permit('out_of_company', False)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_stores', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'store',
                    'company_id': stores['my_store'].company_id,
                    'cluster_id': stores['my_store'].cluster_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('store_healths', 'OK')
            t.json_has('store_healths.0')
            t.json_is('store_healths.0.entity', 'store')
            t.json_is('store_healths.0.entity_id', stores['my_store'].store_id)
            t.json_is(
                'store_healths.0.company_id', stores['my_store'].company_id
            )
            t.json_is(
                'store_healths.0.cluster_id', stores['my_store'].cluster_id
            )
            t.json_is('store_healths.0.store_id', stores['my_store'].store_id)
            t.json_hasnt(
                'store_healths.1', 'Другая лавка из кластера не доступна'
            )


async def test_stores_allow(tap, api, dataset):
    with tap.plan(8, 'Доступ к здоровью своих лавок'):
        stores = await generate_health(dataset)
        user = await dataset.user(
            store=stores['my_store'],
            stores_allow=[
                stores['my_store'].store_id,
                stores['my_cluster_store'].store_id,
                stores['other_cluster_store'].store_id
            ],
            role='executer'
        )
        with user.role as role:
            role.add_permit('out_of_store', True)
            role.add_permit('out_of_company', False)
            role.add_permit('store_healths_seek', True)
            role.add_permit('store_healths_stores', True)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'store',
                    'company_id': stores['my_store'].company_id,
                    'cluster_id': stores['my_store'].cluster_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('store_healths', 'OK')
            result = {
                it['entity_id']: it for it in t.res['json']['store_healths']
            }
            tap.ok(result.get(stores['my_store'].store_id), 'Моя лавка есть')
            tap.ok(
                result.get(stores['my_cluster_store'].store_id),
                'Лавка кластера из allow есть'
            )
            tap.eq(len(result), 2, 'Большие ничего нет')


@pytest.mark.parametrize(
    'permits',
    (
        (
            ('out_of_company', True),
            ('store_healths_seek', False),
            ('store_healths_stores', True),
        ),
        (
            ('out_of_company', True),
            ('store_healths_seek', True),
            ('store_healths_stores', False),
        ),
    )
)
async def test_stores_bad(tap, api, dataset, permits):
    with tap.plan(3, 'Проблемы с доступом'):
        stores = await generate_health(dataset)
        user = await dataset.user(store=stores['my_store'], role='executer')
        with user.role as role:
            for permit in permits:
                role.add_permit(*permit)
            t = await api(user=user)

            await t.post_ok(
                'api_admin_store_healths_list',
                json={
                    'entity': 'store',
                    'company_id': stores['my_store'].company_id,
                    'cluster_id': stores['my_store'].cluster_id,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize(
    'code,note,body',
    (
        (
            400,
            'entity is required',
            {}
        ),
        (
            400,
            'invalid entity',
            {'entity': 'invalid'}
        ),
        (
            200,
            'company - without params',
            {'entity': 'company'}
        ),
        (
            400,
            'cluster - company_id is required',
            {'entity': 'cluster'}
        ),
        (
            200,
            'cluster - company_id is required',
            {'entity': 'cluster', 'company_id': ''}
        ),
        (
            400,
            'supervisor - company_id and cluster_id is required',
            {'entity': 'supervisor', 'cluster_id': ''}
        ),
        (
            400,
            'supervisor - company_id and cluster_id is required',
            {'entity': 'supervisor', 'company_id': ''}
        ),
        (
            200,
            'supervisor - company_id and cluster_id is required',
            {'entity': 'supervisor', 'company_id': '', 'cluster_id': ''}
        ),
        (
            400,
            'store - company_id and cluster_id is required',
            {'entity': 'store', 'cluster_id': ''}
        ),
        (
            400,
            'store - company_id and cluster_id is required',
            {'entity': 'store', 'company_id': ''}
        ),
        (
            200,
            'store - company_id and cluster_id is required',
            {'entity': 'store', 'company_id': '', 'cluster_id': ''}
        ),
    )
)
async def test_not_valid(tap, api, code, note, body):
    with tap.plan(2, note):
        t = await api(role='admin')
        await t.post_ok(
            'api_admin_store_healths_list',
            json=body
        )
        t.status_is(code, diag=True)
