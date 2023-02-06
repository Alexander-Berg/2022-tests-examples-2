from datetime import timedelta
import pytest


async def test_actual(tap, api, dataset, now):
    with tap.plan(36, 'Получение текущих смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster=cluster,
            currency='RUB',
        )
        courier = await dataset.courier(
            cluster=cluster,
            status='active',
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() + timedelta(hours=4)),
            closes_at=(now() + timedelta(hours=6)),
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=2)),
            closes_at=(now() + timedelta(hours=2)),
            guarantee=100.5,
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'started',
                'location': {'lon': 33, 'lat': 55},
            }],
        )
        shift3 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=(now() - timedelta(hours=1)),
            closes_at=(now() + timedelta(hours=3)),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },

                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                }
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_actual',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.0.id', shift2.courier_shift_id)
        t.json_is('data.0.attributes.status', 'In progress')
        t.json_is('data.0.attributes.courierId', courier.courier_id)
        t.json_is('data.0.attributes.courierType', 'pedestrian')
        t.json_has('data.0.attributes.eventList')
        t.json_has('data.0.attributes.eventList.0')
        t.json_is('data.0.attributes.eventList.0.type', 'shiftEvent')
        t.json_is(
            'data.0.attributes.eventList.0.attributes.eventType',
            'started'
        )
        t.json_is(
            'data.0.attributes.eventList.0.attributes.eventSource',
            'courier'
        )
        t.json_is('data.0.attributes.guarantee.value', '100.50')
        t.json_is('data.0.attributes.guarantee.currency.code', 'RUB')
        t.json_is('data.0.attributes.guarantee.currency.sign', '₽')
        t.json_is('data.1.id', shift3.courier_shift_id)
        t.json_is('data.1.attributes.status', 'Closed')
        t.json_is('data.1.attributes.courierId', courier.courier_id)
        t.json_is('data.1.attributes.courierType', 'pedestrian')
        t.json_has('data.1.attributes.eventList')
        t.json_is(
            'data.1.attributes.eventList.0.attributes.eventType',
            'started'
        )
        t.json_is(
            'data.1.attributes.eventList.0.attributes.latitude',
            55
        )
        t.json_is(
            'data.1.attributes.eventList.0.attributes.longitude',
            33
        )
        t.json_is(
            'data.1.attributes.eventList.1.attributes.eventType',
            'stopped'
        )
        t.json_hasnt('data.1.attributes.eventList.1.attributes.latitude')
        t.json_hasnt('data.1.attributes.eventList.1.attributes.longitude')
        t.json_hasnt('data.1.attributes.guarantee')
        t.json_is('data.2.id', shift1.courier_shift_id)
        t.json_is('data.2.attributes.status', 'Planned')
        t.json_is('data.2.attributes.courierId', courier.courier_id)
        t.json_is('data.2.attributes.courierType', 'pedestrian')
        t.json_has('data.2.attributes.eventList')
        t.json_hasnt('data.2.attributes.eventList.0')
        t.json_hasnt('data.2.attributes.guarantee')
        t.json_hasnt('data.3')
        t.json_is('meta.count', 3)


async def test_actual_paused(tap, api, dataset, now, time2iso_utc):
    with tap.plan(22, 'Получение текущих смен с паузой'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_duration': 300},
        )
        store = await dataset.store(
            cluster=cluster,
            currency='RUB',
        )
        courier = await dataset.courier(
            cluster=cluster,
            status='active',
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=2)),
            closes_at=(now() + timedelta(hours=2)),
            guarantee=100.5,
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'location': {'lon': 33, 'lat': 55},
                }
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_actual',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.0.id', shift.courier_shift_id)
        t.json_is('data.0.attributes.status', 'In progress')
        t.json_is('data.0.attributes.courierId', courier.courier_id)
        t.json_is('data.0.attributes.courierType', 'pedestrian')
        t.json_has('data.0.attributes.eventList')
        t.json_has('data.0.attributes.eventList.0')
        t.json_is('data.0.attributes.eventList.0.type', 'shiftEvent')
        t.json_is(
            'data.0.attributes.eventList.0.attributes.eventType',
            'started'
        )
        t.json_is(
            'data.0.attributes.eventList.0.attributes.eventSource',
            'courier'
        )
        t.json_has('data.0.attributes.eventList.1')
        t.json_is('data.0.attributes.eventList.1.type', 'shiftEvent')
        t.json_is(
            'data.0.attributes.eventList.1.attributes.eventType',
            'paused'
        )
        t.json_is(
            'data.0.attributes.eventList.1.attributes.eventSource',
            'courier'
        )
        t.json_is(
            'data.0.attributes.pauseEndsAt',
            time2iso_utc(shift.event_paused().created + timedelta(
                seconds=cluster.courier_shift_setup.pause_duration))
        )
        t.json_is('data.0.attributes.guarantee.value', '100.50')
        t.json_is('data.0.attributes.guarantee.currency.code', 'RUB')
        t.json_is('data.0.attributes.guarantee.currency.sign', '₽')
        t.json_hasnt('data.1')
        t.json_is('meta.count', 1)


async def test_actual_other(tap, api, dataset):
    with tap.plan(5, 'Не своя смена'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Не своя смена
        await dataset.courier_shift(
            store=store,
            courier=await dataset.courier(),
            status='processing',
        )

        # своя, но не выдается, т.к. статус для аналитиков, который ПРО не знает
        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            shift_events=[],
            status='released',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_actual',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_hasnt('data.0')
        t.json_is('meta.count', 0)


async def test_yesterday(tap, api, dataset, now):
    with tap.plan(5, 'Вчерашние смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
            started_at=(now() - timedelta(days=1, hours=2)),
            closes_at=(now() - timedelta(days=1, hours=1)),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_actual',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_hasnt('data.0')
        t.json_is('meta.count', 0)


@pytest.mark.parametrize(
    'status', ('released', 'cancelled')
)
async def test_actual_cancel(tap, api, dataset, status):
    with tap.plan(5, 'Не выводим отмененные смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        await dataset.courier_shift(
            store=store,
            courier=await dataset.courier(),
            status=status,
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_actual',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_hasnt('data.0')
        t.json_is('meta.count', 0)
