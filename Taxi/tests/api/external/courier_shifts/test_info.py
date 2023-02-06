async def test_simple(api, dataset, tap):
    with tap.plan(6, 'Получение флага активной смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store   = await dataset.store(cluster=cluster, company=company)

        courier = await dataset.courier(cluster=cluster)

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_info',
            form={'taxiId': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('isActive', False)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        await t.get_ok(
            'api_external_courier_shifts_info',
            form={'taxiId': courier.external_id},
        )

        t.status_is(200, diag=True)
        t.json_is('isActive', True)


async def test_wrong_courier(api, dataset, tap, uuid):
    with tap.plan(3, 'Неверный курьер'):
        company = await dataset.company()

        t = await api(token=company.token)

        await t.get_ok(
            'api_external_courier_shifts_info',
            form={'taxiId': uuid()},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_COURIER_NOT_FOUND')
