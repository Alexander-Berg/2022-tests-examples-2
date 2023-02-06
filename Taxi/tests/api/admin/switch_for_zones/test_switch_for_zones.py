"""
Тесты на обе handle (turn_off и turn_on)
"""
from stall.model.zone import Zone

# pylint: disable=too-many-locals
async def test_switch_success_store(tap, dataset, api, job):
    with tap.plan(18, 'рубильником туды-сюды ать'):
        store = await dataset.store()
        zones = [await dataset.zone(store=store, status='active')
                 for _ in range(3)]
        user = await dataset.user(store=store)
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'store_id': store.store_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        name = f'turn_off:store:{store.store_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.ok(stash, 'stash создался')
        tap.eq_ok(stash.value['store_id'], store.store_id,
                  'в stash проставился store_id')

        tap.eq_ok(stash.value['company_id'], None, 'в стеше нет компании')
        tap.eq_ok(stash.value['cluster_id'], None, 'в стеше нет кластера')

        await store.reload()

        tap.eq_ok(store.vars['zones_status'], 'request_off',
                  'проставился статус в варсы стора')

        # await job_turn_off_zones(stash.stash_id)
        await job.call(await job.take())
        await store.reload()
        tap.eq_ok(store.vars['zones_status'], 'off',
                  'статус проставился после выполнения джобы')

        user_2 = await dataset.user(store=store)
        t_2 = await api(user=user_2)

        await t_2.post_ok(
            'api_admin_switch_for_zones_turn_on',
            json={'store_id': store.store_id},
        )
        t_2.status_is(200, diag=True)
        t_2.json_is('code', 'OK')

        name_2 = f'turn_on:store:{store.store_id}'
        stash_2 = await dataset.Stash.load(name_2, by='name')

        tap.ok(stash_2, 'stash создался')
        zones_stash = stash_2.value['zones']

        for zone in zones:
            tap.ok(zone.zone_id in zones_stash, 'все измененные зоны в стеше')

        await store.reload()

        tap.eq_ok(store.vars['zones_status'], 'request_on',
                  'проставился статус в варсы стора')


async def test_switch_success_company(tap, dataset, api, job):
    with tap.plan(17, 'отключаем и включаем обратно зоны компании'):
        company = await dataset.company()
        store = await dataset.store()
        zones = [await dataset.zone(company=company, store=store,
                                    status='active') for _ in range(3)]
        user = await dataset.user(company=company)
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'company_id': company.company_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        name = f'turn_off:company:{company.company_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.ok(stash, 'stash создался')
        tap.eq_ok(stash.value['store_id'], None, 'в стеше нет склада')
        tap.eq_ok(stash.value['company_id'], company.company_id,
                  'в стеше проставилась компания')
        tap.eq_ok(stash.value['cluster_id'], None, 'в стеше нет кластера')

        await company.reload()

        tap.eq_ok(company.vars['zones_status'], 'request_off',
                  'проставился статус в варсы компании')

        # await job_turn_off_zones(stash.stash_id)
        await job.call(await job.take())

        user_2 = await dataset.user(company=company)
        t_2 = await api(user=user_2)

        await t_2.post_ok(
            'api_admin_switch_for_zones_turn_on',
            json={'company_id': company.company_id},
        )

        t_2.status_is(200, diag=True)
        t_2.json_is('code', 'OK')

        name_2 = f'turn_on:company:{company.company_id}'
        stash_2 = await dataset.Stash.load(name_2, by='name')

        tap.ok(stash_2, 'stash создался')
        zones_stash = stash_2.value['zones']

        for zone in zones:
            tap.ok(zone.zone_id in zones_stash, 'все измененные зоны в стеше')

        await company.reload()

        tap.eq_ok(company.vars['zones_status'], 'request_on',
                  'проставился статус в варсы компании')


async def test_switch_success_cluster(tap, dataset, api, job):
    with tap.plan(17, 'отключаем и включаем обратно зоны кластера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        zones = [await dataset.zone(cluster=cluster, store=store,
                                    status='active') for _ in range(3)]
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'cluster_id': cluster.cluster_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        name = f'turn_off:cluster:{cluster.cluster_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.ok(stash, 'stash создался')
        tap.eq_ok(stash.value['store_id'], None, 'в стеше нет склада')
        tap.eq_ok(stash.value['company_id'],None, 'в стеше нет компании')
        tap.eq_ok(stash.value['cluster_id'], cluster.cluster_id,
                  'в стеше проставился кластер')

        await cluster.reload()

        tap.eq_ok(cluster.vars['zones_status'], 'request_off',
                  'проставился статус в варсы кластера')

        # await job_turn_off_zones(stash.stash_id)
        await job.call(await job.take())

        user_2 = await dataset.user()
        t_2 = await api(user=user_2)

        await t_2.post_ok(
            'api_admin_switch_for_zones_turn_on',
            json={'cluster_id': cluster.cluster_id},
        )
        t_2.status_is(200, diag=True)
        t_2.json_is('code', 'OK')

        name_2 = f'turn_on:cluster:{cluster.cluster_id}'
        stash_2 = await dataset.Stash.load(name_2, by='name')

        tap.ok(stash_2, 'stash создался')
        zones_stash = stash_2.value['zones']

        for zone in zones:
            tap.ok(zone.zone_id in zones_stash, 'все измененные зоны в стеше')

        await cluster.reload()

        tap.eq_ok(cluster.vars['zones_status'], 'request_on',
                  'проставился статус в варсы кластера')


async def test_wrong_store(tap, dataset, api):
    with tap.plan(3, 'id несуществующего стора'):
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'store_id': '666'},
        )

        t.status_is(403, diag=True)
        name = 'turn_off:store:666'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None,
                  'для несуществующего стора не создается джоба и стэш')


async def test_failed_wrong_status(tap, dataset, api):
    with tap.plan(5, 'запускаем для объектов с неправильным zones_status'):
        store = await dataset.store(vars={'zones_status': 'off'})
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'store_id': store.store_id},
        )

        t.status_is(424, diag=True)
        name = f'turn_off:store:{store.store_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'для стора с неправильным zones_status'
                               ' не создается джоба и стэш')

        store.vars['zones_status'] = 'on'
        await store.save()

        await t.post_ok(
            'api_admin_switch_for_zones_turn_on',
            json={'store_id': store.store_id},
        )

        t.status_is(424, diag=True)


async def test_failed_args(tap, dataset, api):
    with tap.plan(4, 'неверное количество параметров'):
        store = await dataset.store()
        company = await dataset.company()
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'store_id': store.store_id,
                  'company_id': company.company_id},
        )

        t.status_is(400, diag=True)

        name = f'turn_off:store:{store.store_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'при неправильном количестве '
                               'параметров не создается стэш')

        name = f'turn_off:company:{company.company_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'при неправильном количестве '
                               'параметров не создается стэш')


async def test_failed_no_active_stores(tap, dataset, api):
    with tap.plan(5, 'Для кластра без активных сторов не выполняется'):
        cluster = await dataset.cluster()
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'cluster_id': cluster.cluster_id},
        )

        t.status_is(400, diag=True)
        t.json_has('message', 'Message was sent')
        t.json_is('message', 'The cluster has no active stores')

        name = f'turn_off:cluster:{cluster.cluster_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'Стэш не создался')


async def test_no_active_zones_cluster(tap, dataset, api):
    with tap.plan(5, 'Не выполняется для кластера без актиынх зон'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        async for zone in Zone.ilist(
                by='look',
                conditions=[
                    ('store_id', store.store_id),
                    ('status', 'active'),
                ]
        ):
            zone.status = 'disabled'
            await zone.save()

        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'cluster_id': cluster.cluster_id},
        )

        t.status_is(400, diag=True)
        t.json_has('message', 'Message was sent')
        t.json_is('message', 'Object has no active zones')

        name = f'turn_off:cluster:{cluster.cluster_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'Стэш не создался')


async def test_no_active_zones_company(tap, dataset, api):
    with tap.plan(5, 'Не выполняется для компании без актиынх зон'):
        company = await dataset.company()
        store = await dataset.store()
        for _ in range(3):
            await dataset.zone(company=company, store=store,
                               status='disabled')

        user = await dataset.user(company=company)
        t = await api(user=user)

        async for zone in Zone.ilist(
                by='look',
                conditions=[
                    ('company_id', company.company_id),
                    ('status', 'active'),
                ]
        ):
            zone.status = 'disabled'
            await zone.save()

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'company_id': company.company_id},
        )
        t.status_is(400, diag=True)
        t.json_has('message', 'Message was sent')
        t.json_is('message', 'Object has no active zones')

        name = f'turn_off:company:{company.company_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'Стэш не создался')


async def test_no_active_zones_store(tap, dataset, api):
    with tap.plan(5, 'Не выполняется для склада без актиынх зон'):
        store = await dataset.store()
        for _ in range(3):
            await dataset.zone(store=store,
                               status='disabled')

        user = await dataset.user(store=store)
        t = await api(user=user)

        async for zone in Zone.ilist(
                by='look',
                conditions=[
                    ('store_id', store.store_id),
                    ('status', 'active'),
                ]
        ):
            zone.status = 'disabled'
            await zone.save()

        await t.post_ok(
            'api_admin_switch_for_zones_turn_off',
            json={'store_id': store.store_id},
        )
        t.status_is(400, diag=True)
        t.json_has('message', 'Message was sent')
        t.json_is('message', 'Object has no active zones')

        name = f'turn_off:store:{store.store_id}'
        stash = await dataset.Stash.load(name, by='name')

        tap.eq_ok(stash, None, 'Стэш не создался')

