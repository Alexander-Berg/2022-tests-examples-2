async def test_load(tap, api, dataset):
    with tap.plan(5, 'Доступ к здоровью своей компании'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        await dataset.tablo_metric(
            slice='1h',
            store=store,
            recalculate=True,
        )
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)

            await t.post_ok(
                'api_report_data_tablo_metrics_load',
                json={
                    'slice': '1h',
                    'entity': 'cluster',
                    'entity_id': store.cluster_id,
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('metric', 'OK')
            t.json_is('metric.cluster_id', store.cluster_id)


async def test_no_permit(tap, api, dataset):
    with tap.plan(3, 'Доступ к здоровью своей компании'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')

        await dataset.tablo_metric(
            slice='1h',
            store=store,
            recalculate=True,
        )
        with user.role as role:
            role.add_permit('tablo_metrics', False)
            t = await api(user=user)

            await t.post_ok(
                'api_report_data_tablo_metrics_load',
                json={
                    'slice': '1h',
                    'entity': 'cluster',
                    'entity_id': store.cluster_id,
                }
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

async def test_not_found(tap, api, dataset, uuid):
    with tap.plan(3, 'Метрики не найдены'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='executer')
        with user.role as role:
            role.add_permit('tablo_metrics', True)
            t = await api(user=user)

            await t.post_ok(
                'api_report_data_tablo_metrics_load',
                json={
                    'slice': '1h',
                    'entity': 'cluster',
                    'entity_id': uuid(),
                }
            )

            t.status_is(404, diag=True)
            t.json_is('code', 'ER_NOT_FOUND')
