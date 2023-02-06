from stall.model.zone import job_turn_on_zones, job_turn_off_zones, Zone


async def test_job_turn_off_store(tap, dataset):
    with tap.plan(13, 'включение/отключение зон у склада'):
        store = await dataset.store(
            vars={
                'zones_status': 'request_off'
            }
        )
        other_store = await dataset.store()
        zones = [await dataset.zone(store=store) for _ in range(3)]
        other_zone = await dataset.zone(store=other_store)

        stash = await dataset.stash(
            name=f'turn_off:store:{store.store_id}',
            group='turn_off',
            value={
                'cluster_id': None,
                'company_id': None,
                'store_id': store.store_id,
                'status': 'request',
                'zones': []
                }
        )

        await job_turn_off_zones(stash.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'disabled', 'Проставился статус у зоны')

        await other_zone.reload()
        tap.eq_ok(other_zone.status, 'active', 'статус поменялся у нужных зон')

        await stash.reload()
        tap.ne_ok(len(stash.value['zones']), 0,
                  'В стеше появились отключенные зоны')
        for zone in zones:
            tap.ok(zone.zone_id in stash.value['zones'],
                   'Все отключенные зоны записались')

        await store.reload()
        tap.eq_ok(store.vars['zones_status'], 'off',
                  'В варсы помещается статус зон "off"')

        stash_on = await dataset.stash(
            group='turn_on',
            value={
                'cluster_id': None,
                'company_id': None,
                'store_id': store.store_id,
                'status': 'request',
                'zones': stash.value['zones']
            }
        )
        store.vars['zones_status'] = 'request_on'
        await store.save()

        await job_turn_on_zones(stash_on.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'active', 'Проставился статус у зоны')

        await store.reload()
        tap.eq_ok(store.vars['zones_status'], 'on',
                  'В варсы помещается статус зон "on"')


async def test_job_turn_off_company(tap, dataset):
    with tap.plan(13, 'включение/отключение зон у компании'):
        company = await dataset.company(
            vars={
                'zones_status': 'request_off'
            }
        )
        store = await dataset.store()
        other_company = await dataset.company()
        zones = [await dataset.zone(company=company,
                                    store=store) for _ in range(3)]
        other_zone = await dataset.zone(company=other_company, store=store)

        stash = await dataset.stash(
            name=f'turn_off:company:{company.company_id}',
            group='turn_off',
            value={
                'cluster_id': None,
                'company_id': company.company_id,
                'store_id': None,
                'status': 'request',
                'zones': []
                }
        )

        await job_turn_off_zones(stash.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'disabled', 'Проставился статус у зоны')

        await other_zone.reload()
        tap.eq_ok(other_zone.status, 'active', 'статус поменялся у нужных зон')

        await stash.reload()
        tap.ne_ok(len(stash.value['zones']), 0,
                  'В стеше появились отключенные зоны')
        for zone in zones:
            tap.ok(zone.zone_id in stash.value['zones'],
                   'Все отключенные зоны записались')

        await company.reload()
        tap.eq_ok(company.vars['zones_status'], 'off',
                  'В варсы помещается статус зон "off"')

        stash_on = await dataset.stash(
            group='turn_on',
            value={
                'cluster_id': None,
                'company_id': company.company_id,
                'store_id': None,
                'status': 'request',
                'zones': stash.value['zones']
            }
        )

        company.vars['zones_status'] = 'request_on'
        await company.save()

        await job_turn_on_zones(stash_on.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'active', 'Проставился статус у зоны')

        await company.reload()
        tap.eq_ok(company.vars['zones_status'], 'on',
                  'В варсы помещается статус зон "on"')


async def test_job_turn_off_cluster(tap, dataset):
    with tap.plan(13, 'включение/отключение зон у кластера'):
        cluster = await dataset.cluster(
            vars={
                'zones_status': 'request_off'
            }
        )
        store_1 = await dataset.store(cluster=cluster)
        store_2 = await dataset.store(cluster=cluster)
        store_3 = await dataset.store(cluster=cluster)
        zones = [await dataset.zone(store=store_1),
                 await dataset.zone(store=store_2),
                 await dataset.zone(store=store_3)]

        store_4 = await dataset.store()

        other_zone = await dataset.zone(store=store_4)

        stash = await dataset.stash(
            name=f'turn_off:cluster:{cluster.cluster_id}',
            group='turn_off',
            value={
                'cluster_id': cluster.cluster_id,
                'company_id': None,
                'store_id': None,
                'status': 'request',
                'zones': []
                }
        )

        await job_turn_off_zones(stash.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'disabled', 'Проставился статус у зоны')

        await other_zone.reload()
        tap.eq_ok(other_zone.status, 'active', 'статус поменялся у нужных зон')

        await stash.reload()
        tap.ne_ok(len(stash.value['zones']), 0,
                  'В стеше появились отключенные зоны')
        for zone in zones:
            tap.ok(zone.zone_id in stash.value['zones'],
                   'Все отключенные зоны записались')

        await cluster.reload()
        tap.eq_ok(cluster.vars['zones_status'], 'off',
                  'В варсы помещается статус зон "off"')

        stash_on = await dataset.stash(
            group='turn_on',
            value={
                'cluster_id': cluster.cluster_id,
                'company_id': None,
                'store_id': None,
                'status': 'request',
                'zones': stash.value['zones']
            }
        )

        cluster.vars['zones_status'] = 'request_on'
        await cluster.save()

        await job_turn_on_zones(stash_on.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'active', 'Проставился статус у зоны')

        await cluster.reload()
        tap.eq_ok(cluster.vars['zones_status'], 'on',
                  'В варсы помещается статус зон "on"')


async def test_failed_zones_status(tap, dataset):
    with tap.plan(7, 'попытка отключить вкл/выкл '
                     'при неправильном zones_status'):
        store = await dataset.store()
        zones = [await dataset.zone(store=store) for _ in range(3)]

        stash = await dataset.stash(
            name=f'turn_off:store:{store.store_id}',
            group='turn_off',
            value={
                'cluster_id': None,
                'company_id': None,
                'store_id': store.store_id,
                'status': 'request',
                'zones': []
                }
        )

        await job_turn_off_zones(stash.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'active', 'У зоны не изменился статус')
            # меняю для проверки job_turn_on_zones
            zone.status = 'disabled'
            await zone.save()

        await store.reload()
        tap.eq_ok(store.vars.get('zones_status', 'on'),
                  'on', 'статус не проставился')

        stash_on = await dataset.stash(
            group='turn_on',
            value={
                'cluster_id': None,
                'company_id': None,
                'store_id': store.store_id,
                'status': 'request',
                'zones': stash.value['zones']
            }
        )

        await job_turn_on_zones(stash_on.stash_id)

        for zone in zones:
            await zone.reload()
            tap.eq_ok(zone.status, 'disabled', 'Не изменился статус у зоны')

        await store.reload()


# pylint: disable=unused-variable
async def test_store_without_zones(tap, dataset):
    with tap.plan(1, 'ничего не падает при пустом списке отключенных зон'):
        store = await dataset.store(vars={'zones_status': 'request_on'})
        store_1 = await dataset.store()
        zones = []
        async for zone in Zone.ilist(
                by='look',
                conditions=[('store_id', store.store_id)]
        ):
            zone.store_id = store_1.store_id
            zone.status = 'disabled'
            await zone.save()
            zones.append(zone.zone_id)

        stash_on = await dataset.stash(
            group='turn_on',
            value={
                'cluster_id': None,
                'company_id': None,
                'store_id': store.store_id,
                'status': 'request',
                'zones': []
            }
        )

        stash = await dataset.stash(
            name=f'turn_off:store:{store.store_id}'
        )
        await job_turn_on_zones(stash_on.stash_id)
        async for zone in Zone.ilist(
                by='look',
                conditions=[('zone_id', zones)]
        ):
            tap.eq_ok(zone.status, 'disabled', 'чужие зоны не меняются')

