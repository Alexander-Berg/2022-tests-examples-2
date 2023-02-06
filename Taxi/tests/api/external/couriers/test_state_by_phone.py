from datetime import timedelta


async def test_simple(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Нет активного слота'):
        pd_id = uuid()
        _now = now().replace(microsecond=0)

        courier = await dataset.courier(
            vars={
                'phone_pd_ids': [{
                    'pd_id': pd_id,
                }],
            },
        )
        await dataset.courier_shift(
            courier=courier,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
            status='waiting',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
        })

        t.status_is(200, diag=True)
        t.json_is('isActive', False, 'Не на смене')


async def test_active(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Активные слоты курьера по телефону'):
        pd_id = uuid()
        _now = now().replace(microsecond=0)

        courier = await dataset.courier(
            vars={
                'phone_pd_ids': [{
                    'pd_id': pd_id,
                }],
            },
        )
        await dataset.courier_shift(
            courier=courier,
            started_at=_now - timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
        })

        t.status_is(200, diag=True)
        t.json_is('isActive', True, 'Активная смена')


async def test_scheduled(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Запланирован слот'):
        pd_id = uuid()
        _now = now().replace(microsecond=0)

        courier = await dataset.courier(
            vars={
                'phone_pd_ids': [{
                    'pd_id': pd_id,
                }],
            },
        )
        await dataset.courier_shift(
            courier=courier,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
            status='waiting',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
            'minutes_before_shift': 90,
        })

        t.status_is(200, diag=True)
        t.json_is('isActive', True, 'Запланированная смена')


async def test_scheduled_late(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Запланирован слот поздно'):
        pd_id = uuid()
        _now = now().replace(microsecond=0)

        courier = await dataset.courier(
            vars={
                'phone_pd_ids': [{
                    'pd_id': pd_id,
                }],
            },
        )
        await dataset.courier_shift(
            courier=courier,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
            status='waiting',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
            'minutes_before_shift': 30,
        })

        t.status_is(200, diag=True)
        t.json_is('isActive', False, 'Нет запланированных смен')


async def test_wrong_courier(tap, api, uuid):
    with tap.plan(3, 'Нет активного слота'):
        pd_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
        })

        t.status_is(400, diag=True)
        t.json_is(
            'message',
            f'Courier by {pd_id} is not found',
            'Сообщение об ошибке'
        )


async def test_multi_phone(tap, dataset, api, uuid, now):
    with tap.plan(3, 'Несколько телефонных номеров'):
        pd_id = uuid()
        _now = now().replace(microsecond=0)

        courier = await dataset.courier(
            vars={
                'phone_pd_ids': [{
                    'pd_id': uuid(),
                }, {
                    'pd_id': pd_id,
                }, {
                    'pd_id': uuid(),
                }],
            },
        )
        await dataset.courier_shift(
            courier=courier,
            started_at=_now - timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_couriers_state_by_phone', json={
            'personal_phone_id': pd_id,
        })

        t.status_is(200, diag=True)
        t.json_is('isActive', True, 'Активная смена')
