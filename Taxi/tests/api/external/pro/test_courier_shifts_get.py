# pylint: disable=unused-variable,too-many-lines

from datetime import timedelta


async def test_get_simple(tap, api, dataset, now, time2iso_utc):
    with tap.plan(12, 'Получение предложений'):
        day = (now() + timedelta(days=2)).replace(hour=0, minute=0, second=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        started_at = day.replace(hour=12, microsecond=0)
        closes_at  = day.replace(hour=13, microsecond=0)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': ['best'], 'time': now() - timedelta(hours=1)},
                {'tags': [], 'time': now() + timedelta(hours=1)},
            ],
            started_at=started_at,
            closes_at=closes_at,
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.opened.0.type', 'openedShift')
        t.json_is('data.opened.0.attributes.startsAt', time2iso_utc(started_at))
        t.json_is('data.opened.0.attributes.endsAt', time2iso_utc(closes_at))
        t.json_is('data.opened.0.attributes.startPoint.id', store.store_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_filter_by_zone(tap, api, dataset, now, time2iso_utc):
    with tap.plan(12, 'Фильтрация по лавкам'):
        day = (now() + timedelta(days=2)).replace(hour=0, minute=0, second=0)

        cluster = await dataset.cluster()
        store_1 = await dataset.store(cluster=cluster)
        store_2 = await dataset.store(cluster=cluster)

        started_at = day.replace(hour=12, microsecond=0)
        closes_at = day.replace(hour=13, microsecond=0)

        shifts = [
            await dataset.courier_shift(
                cluster=cluster,
                store=store,
                tags=[],
                status='request',
                schedule=[
                    {'tags': ['best'], 'time': now() - timedelta(hours=1)},
                    {'tags': [], 'time': now() + timedelta(hours=1)},
                ],
                started_at=started_at,
                closes_at=closes_at,
            ) for store in (store_1, store_2)
        ]

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': started_at.strftime('%d.%m.%Y'),
                'filters[zones][]': [store_1.store_id]
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shifts[0].group_id)
        t.json_is('data.opened.0.type', 'openedShift')
        t.json_is('data.opened.0.attributes.startsAt', time2iso_utc(started_at))
        t.json_is('data.opened.0.attributes.endsAt', time2iso_utc(closes_at))
        t.json_is('data.opened.0.attributes.startPoint.id', store_1.store_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_zone_not_found(tap, api, dataset, now):
    with tap.plan(8, 'Получение предложений по id едовой зоны, но ее нет'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        started_at = day.replace(hour=12, microsecond=0)
        closes_at  = day.replace(hour=13, microsecond=0)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': ['best'], 'time': now() - timedelta(hours=1)},
                {'tags': [], 'time': now() + timedelta(hours=1)},
            ],
            started_at=started_at,
            closes_at=closes_at,
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
                'filters[zones][]': [987654],
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


# pylint: disable=too-many-locals]
async def test_group(tap, api, dataset, now, time2iso_utc, uuid):
    with tap.plan(13, 'Только одно предложение в группе'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        started_at  = day.replace(hour=12, microsecond=0)
        closes_at   = day.replace(hour=13, microsecond=0)
        group_id    = uuid()

        shift1 = await dataset.courier_shift(
            group_id=group_id,
            cluster=cluster,
            store=store,
            status='request',
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=started_at,
            closes_at=closes_at,
        )
        shift2 = await dataset.courier_shift(
            group_id=group_id,
            cluster=cluster,
            store=store,
            status='request',
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=started_at,
            closes_at=closes_at,
        )

        courier = await dataset.courier(cluster=cluster)

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', group_id)
        t.json_is('data.opened.0.type', 'openedShift')
        t.json_is('data.opened.0.attributes.startsAt', time2iso_utc(started_at))
        t.json_is('data.opened.0.attributes.endsAt', time2iso_utc(closes_at))
        t.json_is('data.opened.0.attributes.startPoint.id', store.store_id)
        t.json_hasnt('data.opened.1')
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_experiment(tap, api, dataset, now):
    with tap.plan(8, 'Получение предложений по конкретным тегам'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=['experiment1'],
            status='request',
            schedule=[
                {'tags': ['best'], 'time': now() - timedelta(hours=1)},
                {'tags': [], 'time': now() + timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['experiment1', 'best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_tags_store_ok(tap, api, dataset, now):
    with tap.plan(8, 'Получение предложений по привязанным лавкам'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        started_at = day.replace(hour=12)
        closes_at = day.replace(hour=13)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=started_at,
            closes_at=closes_at,
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id, store2.store_id],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_tags_store_fail(tap, api, dataset, now):
    with tap.plan(8, 'Смена не найдена т.к. курьер привязан к другой лавке'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_tags_store_public(tap, api, dataset, now):
    with tap.plan(8, 'Смена найдена т.к. выставлен параметр public'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
            attr={'public': True}
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_all(tap, api, dataset, now):
    with tap.plan(8, 'Получение предложений по расписанию для всех'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_fail_all_too_early(tap, api, dataset, now):
    with tap.plan(8, 'Слишком рано для расписания для всех'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': [], 'time': now() + timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_fail_tag_too_early(tap, api, dataset, now):
    with tap.plan(8, 'Слишком рано для своего расписания'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': ['best'], 'time': now() + timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_tag_ok(tap, api, dataset, now):
    with tap.plan(8, 'Подходит по одному из тегов'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[{
                'tags': ['superman', 'best'],
                'time': now() - timedelta(hours=1)
            }],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_tag_fail(tap, api, dataset, now):
    with tap.plan(8, 'Не подходит по тегам'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': ['superman'], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_fail_delivery_type(tap, api, dataset, now):
    with tap.plan(8, 'Не свой тип доставки'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            delivery_type='car',
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_ignore_delivery_type(tap, api, dataset, now):
    with tap.plan(8, 'Игнорируем тип доставки'):
        day = (now() + timedelta(days=2)).replace(hour=0, minute=0, second=0)

        cluster = await dataset.cluster(courier_shift_setup={
            'delivery_type_check_enable': False,
        })
        shift = await dataset.courier_shift(
            cluster=cluster,
            delivery_type='car',
            tags=[],
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift.group_id)
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_fail_cluster(tap, api, dataset, now):
    with tap.plan(8, 'Не свой кластер'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            tags=[],
            status='request',
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        cluster2 = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster2,
            tags=['best'],
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 0)


async def test_closed(tap, api, dataset, now):
    with tap.plan(11, 'Получение других смен в этой же ручке'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            shift_events=[],
            status='complete',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            shift_events=[dataset.CourierShiftEvent({
                'type': 'stopped',
                'location': {
                    'lon': 123,
                    'lat': 456
                }
            })],
            status='complete',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=15),
        )

        shift_3 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            shift_events=[],
            status='released',      # не должна выдаваться курьеру
        )
        shift_4 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            shift_events=[],
            status='cancelled',      # не должна выдаваться курьеру
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened', [])
        t.json_is('data.closed.0.id', shift.courier_shift_id)
        t.json_is('data.closed.0.type', 'shift')
        t.json_is('data.closed.1.id', shift_2.courier_shift_id)
        t.json_is('data.closed.1.type', 'shift')
        t.json_has('meta')
        t.json_is('meta.opened.count', 0)
        t.json_is('meta.closed.count', 2)


async def test_filter_zones(tap, api, dataset, now, time2iso_utc):
    with tap.plan(13, 'Фильтр по лавкам'):
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        started_at = day.replace(hour=12, microsecond=0)
        closes_at  = day.replace(hour=13, microsecond=0)

        shift1 = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=started_at,
            closes_at=closes_at,
        )
        shift2 = await dataset.courier_shift(
            cluster=cluster,
            store=store2,
            status='request',
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
            started_at=started_at,
            closes_at=closes_at,
        )

        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift2.started_at.strftime('%d.%m.%Y'),
                'filters[zones][]': [store2.store_id],
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift2.group_id)
        t.json_is('data.opened.0.type', 'openedShift')
        t.json_is('data.opened.0.attributes.startsAt', time2iso_utc(started_at))
        t.json_is('data.opened.0.attributes.endsAt', time2iso_utc(closes_at))
        t.json_is('data.opened.0.attributes.startPoint.id', store2.store_id)
        t.json_hasnt('data.opened.1')
        t.json_is('data.closed', [])
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 0)


async def test_replacement(tap, api, dataset, time_mock):
    # pylint: disable=import-outside-toplevel
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(
            12,
            'Курьер проспал смену, но должен мочь взять перевыставленную из нее'
    ):
        _now = time_mock.now()

        cluster = await dataset.cluster(courier_shift_setup={
            'max_day_hours': 2,
            'max_week_hours': 2,
        })
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={'external_ids': {'eats': 12345}},
        )

        shift1 = await dataset.courier_shift(
            placement='planned',
            cluster=cluster,
            store=store,
            status='waiting',
            schedule=[
                {'tags': [], 'time': _now - timedelta(hours=1)},
            ],
            started_at=_now - timedelta(minutes=1),
            closes_at=_now + timedelta(hours=1),
            courier_id=courier.courier_id,
        )

        from scripts.cron.close_courier_shifts import close_courier_shifts
        tap.ok(
            await close_courier_shifts(cluster_id=cluster.cluster_id),
            'Скрипт отработал'
        )

        with await shift1.reload():
            tap.eq(shift1.status, 'absent', 'Смена сорвана')

        reissued = await shift1.list_reissued()
        tap.eq(len(reissued), 1, 'Есть перевысталенная смена')

        with reissued[0] as shift2:
            tap.eq(shift2.status, 'request', 'request')

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_get',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            form={
                'filters[date]': shift2.started_at.strftime('%d.%m.%Y'),
            },
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.opened.0.id', shift2.group_id)
        t.json_is('data.closed.0.id', shift1.courier_shift_id)
        t.json_has('meta')
        t.json_is('meta.opened.count', 1)
        t.json_is('meta.closed.count', 1)
