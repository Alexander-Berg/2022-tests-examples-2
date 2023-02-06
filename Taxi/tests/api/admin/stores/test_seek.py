# pylint: disable=unused-variable

import pytest

from stall.config import cfg


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_seek(tap, api, uuid, dataset, role):
    with tap.plan(30):
        stores = []
        for _ in range(5):
            store = await dataset.store(title='Склад %s' % uuid())
            tap.ok(store, 'Склад создан')
            stores.append(store)

        t = await api(role=role)

        await t.post_ok('api_admin_stores_seek', json={'limit': 3})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores.0.store_id')
        t.json_has('stores.0.external_id')
        t.json_has('stores.0.print_id')
        t.json_has('stores.0.assortment_id')
        t.json_has('stores.0.kitchen_assortment_id')
        t.json_has('stores.0.markdown_assortment_id')
        t.json_has('stores.0.price_list_id')
        t.json_has('stores.0.title')
        t.json_has('stores.0.slug')
        t.json_has('stores.0.created')
        t.json_has('stores.0.updated')
        t.json_has('stores.0.tz')
        t.json_has('stores.0.lang')
        t.json_has('stores.0.currency')
        t.json_has('stores.0.address')
        t.json_has('stores.0.location')
        t.json_has('stores.0.region_id')
        t.json_has('stores.0.source')
        t.json_has('stores.0.group_id')
        t.json_has('stores.0.errors')
        t.json_has('stores.0.user_id')


# pylint: disable=too-many-locals
async def test_clusters_allow(tap, dataset, api, uuid):
    with tap.plan(24, 'проверяем разные доступные кластера'):
        cluster1_name = uuid()
        cluster2_name = uuid()

        user1 = await dataset.user(
            role='support', clusters_allow=[cluster1_name]
        )
        user2 = await dataset.user(
            role='support', clusters_allow=[]
        )

        store1 = await dataset.store(
            cluster=cluster1_name,
            title=cluster1_name,
        )
        store2 = await dataset.store(
            cluster=cluster2_name,
            title=cluster2_name,
        )

        cases = [(user1, None), (user2, None), (user2, store2.cluster)]
        answers = [[store1], [store1, store2], [store2]]

        for i, (u, c) in enumerate(cases):
            json = {'cluster': c} if c else {}
            res = []
            for tt in [cluster1_name, cluster2_name]:
                json['title'] = tt
                t = await api(user=u)
                await t.post_ok(
                    'api_admin_stores_seek',
                    json=json
                )
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                res += t.res['json']['stores']

            ans = {s.store_id for s in answers[i]}
            res_set = {st['store_id'] for st in res}
            tap.eq(
                res_set,
                ans,
                'Пришли правильные ассортименты'
            )
        t = await api(user=user1)
        await t.post_ok(
            'api_admin_stores_seek',
            json={'cluster': store2.cluster}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_cluster_id(tap, dataset, api, uuid):
    with tap.plan(21, 'Проверяем доступные кластера по cluster_id'):
        _location = {'lat': 8.0001, 'lon': 4.0001}
        clusters = [await dataset.cluster() for _ in range(5)]
        stores = [
            await dataset.store(cluster=cluster, location=_location)
            for cluster in clusters
        ]
        alien_stores = [
            await dataset.store(location=_location)
            for _ in range(5)
        ]
        user1 = await dataset.user(clusters_allow=[c.title for c in clusters])
        user2 = await dataset.user(clusters_allow=[])

        #
        tap.note('Пользователь со списком разрешенных кластеров')
        t = await api(user=user1)

        # кластер не задан, но в allow прописаны доступные
        await t.post_ok('api_admin_stores_seek', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq(
            sorted(s['store_id'] for s in t.res['json']['stores']),
            sorted(s.store_id for s in stores),
            'лавки правильные'
        )
        # кластер задан, allow задан и кластер НАЙДЕН среди них
        await t.post_ok('api_admin_stores_seek',
                        json={'cluster_id': stores[0].cluster_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('stores.0.cluster_id', stores[0].cluster_id, 'лавка найдена')
        t.json_hasnt('courier_shifts.1', 'лишних лавок нет')

        # кластер задан, allow задан, но кластер НЕ найден среди них
        await t.post_ok('api_admin_stores_seek',
                        json={'cluster_id': alien_stores[0].cluster_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        #
        tap.note('Пользователь БЕЗ clusters_allow, поэтому доступ не ограничен')
        t = await api(user=user2)

        # кластер задан, в allow ничего не указано и кластер НАЙДЕН
        await t.post_ok('api_admin_stores_seek',
                        json={'cluster_id': alien_stores[0].cluster_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('stores.0.cluster_id', alien_stores[0].cluster_id, 'найдена')
        t.json_hasnt('courier_shifts.1', 'лишних лавок нет')

        # кластер задан, в allow ничего не указано и кластер НЕ НАЙДЕН
        await t.post_ok('api_admin_stores_seek',
                        json={'cluster_id': uuid()})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('courier_shifts.0', 'лавка не найдена')


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_seek_by_title(tap, api, uuid, dataset, role):
    with tap.plan(11):
        stores = []
        for _ in range(5):
            store = await dataset.store(title='Склад %s' % uuid())
            tap.ok(store, 'Склад создан')
            stores.append(store)

        t = await api(role=role)

        store_to_find = stores[2]
        await t.post_ok('api_admin_stores_seek',
                        json={'title': store_to_find.title})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('stores.0', 'Найдены склады')
        t.json_hasnt('stores.1', 'Найден только один склад')
        t.json_is('stores.0.store_id', store_to_find.store_id,
                  'Найден нужный склад')


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_cursor_pagination(tap, api, uuid, dataset, role):
    with tap.plan(2):
        cluster = uuid()
        store_ids = []
        for _ in range(cfg('cursor.limit') + 131):
            store = await dataset.store(cluster=cluster)
            store_ids.append(store.store_id)
        t = await api(role=role)
        ret_store_ids = []
        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps
            cursor = ''
            while True:
                await t.post_ok('api_admin_stores_seek',
                                json={'cluster': cluster, 'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
                t.json_hasnt('stores.%s' % cfg('cursor.limit'),
                             'Не больше %s складов за раз' % cfg(
                                 'cursor.limit'))
                ret_store_ids += [s['store_id']
                                  for s in t.res['json']['stores']]
                if not t.res['json']['cursor']:
                    break
                cursor = t.res['json']['cursor']
        t.tap = tap

        tap.eq_ok(
            sorted(ret_store_ids),
            sorted(store_ids),
            'Склады прочитаны правильно'
        )


@pytest.mark.parametrize('role', ['admin', 'support'])
async def test_seek_title(tap, api, uuid, dataset, role):
    with tap.plan(6, 'Поиск склада по первым буквам'):
        store_title = uuid()

        store = await dataset.store(title=store_title)
        tap.ok(store, 'Склад создан')

        t = await api(role=role)

        await t.post_ok('api_admin_stores_seek',
                        json={'limit': 3, 'title': store_title[:-5]})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        t.json_is('stores.0.store_id', store.store_id, 'Склад есть в выдаче')


async def test_seek_by_eid(tap, api, dataset):
    with tap.plan(7, 'Если ввели external_id то ищем по нему'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        t = await api(role='admin')

        await t.post_ok('api_admin_stores_seek',
                        json={'limit': 3,
                              'external_id': store.external_id}
                        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        t.json_has('stores.0')
        t.json_is('stores.0.store_id', store.store_id)


async def test_seek_wrong_eid(tap, api, dataset):
    with tap.plan(6, 'Если ввели external_id то ищем по нему'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        t = await api(role='admin')

        await t.post_ok('api_admin_stores_seek',
                        json={'limit': 3,
                              'external_id': "12345" }
                        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        t.json_hasnt('stores.0')


async def test_seek_by_stores_allow(tap, api, dataset):
    with tap.plan(8, 'показываем только разрешенные лавки, если они заданы'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        supervisor = await dataset.user(
            role='admin', stores_allow=[store1.store_id],
        )
        tap.eq_ok(supervisor.stores_allow, [store1.store_id], 'лавка разрешена')

        t = await api()
        t.set_user(supervisor)

        await t.post_ok('api_admin_stores_seek', json={})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        t.json_has('stores.0')
        t.json_is('stores.0.store_id', store1.store_id)
        t.json_hasnt('stores.1')


@pytest.mark.parametrize(
    'role,alien_company',
    (
        ('admin',       True),
        ('expansioner', False),
    )
)
async def test_seek_company(tap, dataset, api, uuid, role, alien_company):
    with tap.plan(8, f'Доступ только к своим/чужим компаниям ({role})'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        # Задаем кластер, чтобы не мешались лавки, добавленные другими тестами
        target_cluster = uuid()
        store1 = await dataset.store(company=company1, cluster=target_cluster)
        store2 = await dataset.store(company=company1, cluster=target_cluster)
        store3 = await dataset.store(company=company2, cluster=target_cluster)

        user = await dataset.user(
            role=role,
            store=store1,
            clusters_allow=[target_cluster]
        )
        tap.ok(user.has_permit('stores_seek'), 'Можно фильтровать список лавок')
        tap.ok(user.has_permit('out_of_store'), 'Может смотреть чужие лавки')
        tap.eq(user.has_permit('out_of_company'), alien_company, 'чужая комп.')

        result = [
            store1.store_id,    # своя лавка и своя компания
            store2.store_id     # чужая лавка, но своя компания
        ]

        # чужая лавка и чужая компания
        if alien_company:
            result.append(store3.store_id)

        t = await api(user=user)
        await t.post_ok('api_admin_stores_seek', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        tap.eq_ok(
            sorted([s['store_id'] for s in t.res['json']['stores']]),
            sorted(result),
            'Пришли правильные объекты'
        )


async def test_seek_by_sample_id(tap, api, dataset):
    with tap.plan(5):
        sample1 = await dataset.sample()
        sample2 = await dataset.sample()
        sample3 = await dataset.sample()

        await dataset.store(
            samples_ids=[sample1.sample_id, sample2.sample_id])
        store2 = await dataset.store(
            samples_ids=[sample2.sample_id, sample3.sample_id])
        store3 = await dataset.store(
            samples_ids=[sample3.sample_id])

        t = await api(role='admin')

        await t.post_ok('api_admin_stores_seek',
                        json={'sample_id': sample3.sample_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')

        stores = t.res['json']['stores']

        tap.eq(
            sorted([s['store_id'] for s in stores]),
            sorted([store2.store_id, store3.store_id]),
            'Правильные склады',
        )


async def test_seek_incorrect_sample(tap, api, dataset, uuid):
    with tap.plan(5):
        await dataset.sample()
        t = await api(role='admin')

        await t.post_ok('api_admin_stores_seek',
                        json={'sample_id': uuid()})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_is('stores', [])


async def test_seek_by_status(tap, api, dataset):
    with tap.plan(6):

        store1 = await dataset.store(status='active')
        store2 = await dataset.store(status='disabled')

        t = await api(role='admin')

        await t.post_ok('api_admin_stores_seek',
                        json={'status': 'disabled'})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        results = t.res['json']['stores']

        tap.in_ok(store2, results,
                  'Искомый склад найден',)
        tap.not_in_ok(store1, results,
                      'Лишних складов нет',)
