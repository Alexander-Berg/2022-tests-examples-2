import pytest


@pytest.mark.parametrize('role', ['admin_ro', 'admin'])
async def test_cluster_stat(tap, api, dataset, role):
    with tap.plan(13, 'Запросы за статистикой по кластерам'):
        store = await dataset.store()
        tap.ok(store.cluster, 'Склад с кластером создан')

        t = await api(role=role)

        await t.post_ok('api_admin_stores_cluster_stat', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stat.0', 'есть статистика')
        await t.post_ok('api_admin_stores_cluster_stat',
                        json={'cluster': store.cluster})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stat.0', 'есть статистика')
        t.json_hasnt('stat.1', 'ограничено фильтром')

        t.json_is('stat.0.cluster', store.cluster)
        t.json_is('stat.0.status', store.status)
        t.json_is('stat.0.count', 1)


async def test_company_filter(tap, api, dataset):
    with tap.plan(11, 'Статистика по кластерам с фильтром по чужой компании'):
        company_1 = await dataset.company()
        store_1 = await dataset.store(company=company_1)
        tap.ok(store_1.company_id, 'Склад с компанией 1 создан')

        company_2 = await dataset.company()
        store_2 = await dataset.store(company=company_2)
        tap.ok(store_2.company_id, 'Склад с компанией 2 создан')

        user = await dataset.user(role='support_it', store_id=store_1.store_id)
        tap.eq_ok(
            user.store_id,
            store_1.store_id,
            'Пользователь со склада 1 с пермитами stores_cluster_stat и '
            'out_of_company создан'
        )
        t = await api(user=user)

        await t.post_ok('api_admin_stores_cluster_stat',
                        json={'company_id': company_2.company_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stat.0', 'есть статистика')
        t.json_hasnt('stat.1', 'ограничено фильтром')

        t.json_is('stat.0.cluster', store_2.cluster)
        t.json_is('stat.0.status', store_2.status)
        t.json_is('stat.0.count', 1)


async def test_company_filter_no_permit(tap, api, dataset):
    with tap.plan(11, 'Статистика по кластерам с фильтром по чужой компании '
                      '(нет пермита out_of_company)'):
        company_1 = await dataset.company()
        store_1 = await dataset.store(company=company_1)
        tap.ok(store_1.company_id, 'Склад с компанией 1 создан')

        company_2 = await dataset.company()
        store_2 = await dataset.store(company=company_2)
        tap.ok(store_2.company_id, 'Склад с компанией 2 создан')

        user = await dataset.user(role='expansioner', store_id=store_1.store_id)
        tap.eq_ok(
            user.store_id,
            store_1.store_id,
            'Пользователь со склада 1 с пермитом stores_cluster_stat, но без '
            'out_of_company создан'
        )
        t = await api(user=user)

        await t.post_ok('api_admin_stores_cluster_stat',
                        json={'company_id': company_2.company_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stat.0', 'есть статистика')
        t.json_hasnt('stat.1', 'ограничено фильтром')

        t.json_is('stat.0.cluster', store_1.cluster)
        t.json_is('stat.0.status', store_1.status)
        t.json_is('stat.0.count', 1)


async def test_user_has_no_company(tap, api, dataset):
    with tap.plan(2, 'Статистика по кластерам, у пользователя нет компании'):
        user = await dataset.user(role='expansioner', company_id=None)
        t = await api(user=user)

        await t.post_ok('api_admin_stores_cluster_stat', json={})
        t.status_is(403, diag=True)


# pylint: disable=too-many-locals
async def test_clusters_allow(tap, api, dataset, uuid):
    with tap.plan(18, 'проверяем разные доступные кластера'):
        cluster1_name = uuid()
        cluster2_name = uuid()
        user1 = await dataset.user(
            role='admin', clusters_allow=[cluster1_name]
        )
        user2 = await dataset.user(
            role='admin', clusters_allow=[]
        )

        await dataset.store(cluster=cluster1_name)
        await dataset.store(cluster=cluster2_name)

        cluster1 = await dataset.cluster(title=cluster1_name)
        cluster2 = await dataset.cluster(title=cluster2_name)

        answers = [[cluster1], [cluster1, cluster2], [cluster2]]

        for i, (u, c) in enumerate(
                [(user1, None), (user2, None), (user2, cluster2.title)]
        ):
            t = await api(user=u)
            await t.post_ok(
                'api_admin_stores_cluster_stat',
                json={'cluster': c} if c else {}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('stat.0', 'есть статистика')

            res = t.res['json']['stat']
            ans = {cc.title for cc in answers[i]}
            all_clusters = {cluster1.title, cluster2.title}
            res_set = {cl['cluster'] for cl in res}
            tap.eq(
                res_set & all_clusters,
                ans,
                'Пришли правильные ассортименты'
            )
        t = await api(user=user1)
        await t.post_ok(
            'api_admin_stores_cluster_stat',
            json={'cluster': cluster2.title}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

