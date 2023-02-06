# pylint: disable=too-many-lines

from datetime import timedelta

import pytest

from stall.client.grocery_checkins import GroceryCheckinsError
from stall.client.grocery_checkins import client as gc_client


async def test_simple(tap, api, dataset, uuid, time2iso_utc, time2time):
    with tap.plan(18, 'Пауза смены'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.pauseEndsAt', time2iso_utc(shift.closes_at))

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 1, 'события добавлены')

            with shift.shift_events[0] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )
                tap.eq(
                    event.detail['pro_event_id'],
                    event_id,
                    'pro_event_id'
                )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'processing', 'processing')
        tap.eq(len(shift.shift_events), 1, 'события не дублированы')


async def test_wrong_status(tap, api, dataset, uuid):
    with tap.plan(3, 'Пауза смены не в processing'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.invalid_previous_status'
        )


async def test_max_count(tap, api, dataset, uuid):
    with tap.plan(12, 'Слишком много пауз'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_max_count': 2},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        tap.eq(cluster.cluster_id, shift.cluster_id, 'cluster_id')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )


async def test_max_count_system(tap, api, dataset, uuid):
    with tap.plan(3, 'Слишком много пауз, хотя и сняты все системой'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_max_count': 1},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                },
                {
                    'type': 'unpaused',
                },
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )


async def test_only_courier(tap, api, dataset, uuid):
    with tap.plan(8, 'Учитываются только паузы курьера'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_max_count': 1},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        user = await dataset.user(store=store)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[
                {
                    'user_id': user.user_id,
                    'type': 'paused',
                },
                {
                    'user_id': user.user_id,
                    'type': 'unpaused',
                },
            ],
        )

        tap.eq(cluster.cluster_id, shift.cluster_id, 'cluster_id')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unpause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )


async def test_too_late(tap, api, dataset, uuid, now):
    with tap.plan(7, 'Взятие паузы смены слишком поздно'):
        cluster = await dataset.cluster(
            courier_shift_setup={'shift_end_restriction': 3600},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()

        shift_well = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            closes_at=now()+timedelta(hours=2),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift_well.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        shift_bad = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            closes_at=now()+timedelta(minutes=30),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift_bad.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.start_time_unavailable'
        )
        t.json_has('errors.0.attributes.arguments.threshold')
        t.json_like(
            'errors.0.attributes.title',
            t.res['json']['errors'][0]['attributes']['arguments']['threshold']
        )


async def test_not_found(tap, api, dataset, uuid):
    with tap.plan(3, 'Пауза смены не в processing'):
        courier = await dataset.courier()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': uuid(),
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.shift_does_not_exist'
        )


async def test_schedule_pause(tap, api, dataset, uuid):
    with tap.plan(14, 'Отложенная пауза смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 1, 'события добавлены')

            with shift.shift_events[-1] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 1, 'повторное событие не добавлено')


async def test_schedule_pause_force(tap, api, dataset, uuid):
    with tap.plan(22, 'Форсируем паузу после выполнения заказа'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        order = await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 1, 'события добавлены')

            with shift.shift_events[-1] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')

        # Закрываем заказ
        order.status = 'complete'
        tap.ok(await order.save(), 'закрыли заказ')

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')

            with shift.shift_events[-1] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'paused', 'форсирована paused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')


async def test_after_schedule_pause(tap, api, dataset, uuid, now):
    with tap.plan(15, 'Пауза после отложенной паузы'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_max_count': 1},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster, checkin_time=now())

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )
        order = await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        # отложенная пауза
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 1, 'события добавлены')
            tap.eq(shift.shift_events[-1].type, 'schedule_pause', 'scheduled')

        # запуск паузы
        order.status = 'complete'
        await order.save()
        tap.ok(await dataset.CourierShift.job_start_schedule_pause(
            courier_id=courier.courier_id
        ), 'отложенная пауза запущена')

        with await shift.reload():
            tap.eq(len(shift.shift_events), 2, 'Событие смены добавлено')

            with shift.shift_events[0] as event:
                tap.eq(event.type, 'schedule_pause', 'schedule_pause')

            with shift.shift_events[1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.courier_id, None, 'courier_id=None')
                tap.eq(event.detail.get('courier_id'),
                       courier.courier_id,
                       'courier_id')
                tap.eq(event.detail.get('user_id'),
                       courier.user_id,
                       'user_id=None')

        # снимаем с паузы
        shift.shift_events = [{
            'type': 'unpaused',
            'courier_id': None,
            'shift_event_id': f'{shift.shift_events[1].shift_event_id}:unpaused'
        }]
        await shift.save()

        # повторная постановка паузы после отложенной не срабатывает
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )


async def test_pause_ends(tap, api, dataset, uuid, time2iso_utc):
    with tap.plan(3, 'Время закрытия паузы'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_duration': 7200},
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )

        t.status_is(200, diag=True)

        with await shift.reload() as shift:
            t.json_is(
                'data.pauseEndsAt',
                time2iso_utc(
                    shift.shift_events[-1].created + timedelta(hours=2)
                ),
            )


async def test_grocery_checkins_sync(
        tap, dataset, ext_api, api, uuid, time2iso
):
    with tap.plan(4, 'оповещаем grocery-checkins о паузе'):
        _calls = []

        async def handle(request):
            data = await request.json()
            _calls.append(data)
            return {}

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        async with await ext_api('grocery_checkins', handle):
            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_pause',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                    'X-App-Version': '1.2.3',
                },
                json={
                    'id': uuid(),
                    'location': {
                        'latitude': 55.0,
                        'longitude': 33.0,
                    },
                }
            )
            t.status_is(200, diag=True)

        with await shift.reload() as shift:
            event = shift.event_paused()
            tap.ok(event, 'shift is on pause')
            tap.eq(_calls, [{
                'performer_id': courier.external_id,
                'shift_id': shift.courier_shift_id,
                'paused_at': time2iso(event.created)
            }], 'grocery_checkins called once')


async def test_grocery_checkins_schedule(
        tap, dataset, ext_api, api, uuid
):
    with tap.plan(5, 'не оповещаем grocery-checkins о плановой паузе'):
        _calls = []

        async def handle(request):
            data = await request.json()
            _calls.append(data)
            return {}

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        async with await ext_api('grocery_checkins', handle):
            t = await api(role='token:web.external.tokens.0')
            await t.post_ok(
                'api_external_pro_courier_shifts_pause',
                params_path={
                    'courier_shift_id': shift.courier_shift_id,
                },
                headers={
                    'X-YaTaxi-Park-Id': courier.park_id,
                    'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                    'X-App-Version': '1.2.3',
                },
                json={
                    'id': uuid(),
                    'location': {
                        'latitude': 55.0,
                        'longitude': 33.0,
                    },
                }
            )
            t.status_is(204, diag=True)

        with await shift.reload() as shift:
            event = shift.event_paused()
            tap.ok(not event, 'shift is not on pause')
            event = shift.event_schedule_pause()
            tap.ok(event, 'shift is not on schedule_pause')
            tap.eq(_calls, [], 'grocery_checkins not called')


@pytest.mark.parametrize('exc_cls', [GroceryCheckinsError, Exception])
async def test_grocery_checkins_sync_fail(
        tap, dataset, api, uuid, monkeypatch, exc_cls
):
    with tap.plan(3, 'при ошибках обращения к grocery-checkins не падаем'):
        # pylint: disable=unused-argument
        async def raiser(self, *args, **kwargs):
            raise exc_cls

        monkeypatch.setattr(gc_client, gc_client.shift_pause.__name__, raiser)

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)

        with await shift.reload() as shift:
            event = shift.event_paused()
            tap.ok(event, 'shift is on pause')


async def test_restart_pause(
    tap, api, dataset, uuid, time2iso_utc, time2time, now,
):
    with tap.plan(18, 'Доиспользование паузы смены'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_max_count': 1,
                'restart_pause': True,
                'pause_duration': 1200,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        _now = now().replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'created':  _now - timedelta(hours=3, minutes=50),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'created':  _now - timedelta(hours=3, minutes=45),
                },
            ],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.pauseEndsAt', time2iso_utc(shift.closes_at))

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 3, 'события добавлены')

            with shift.shift_events[-1] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )
                tap.eq(
                    event.detail['pro_event_id'],
                    event_id,
                    'pro_event_id'
                )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'processing', 'processing')
        tap.eq(len(shift.shift_events), 3, 'события не дублированы')


async def test_restart_pause_expire_time(tap, api, dataset, uuid, now):
    with tap.plan(6, 'Доиспользование паузы смены не сработает'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_max_count': 1,
                'restart_pause': True,
                'pause_duration': 1200,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        _now = now().replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'created':  _now - timedelta(hours=3, minutes=50),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'created':  _now - timedelta(hours=3, minutes=25),
                },
            ],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'processing', 'processing')
        tap.eq(len(shift.shift_events), 2, 'события не дублированы')


async def test_restart_extra_pause(
    tap, api, dataset, uuid, time2iso_utc, time2time, now,
):
    with tap.plan(18, 'Доиспользование расширенной паузы смены'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_max_count': 1,
                'restart_pause': True,
                'pause_duration': 1200,  # 20 минут
                'long_slot_duration': 14400,  # 4 часа
                'extra_pause': 1200,  # 20 минут
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        _now = now().replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(hours=1),
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'paused',
                    'created':  _now - timedelta(hours=5, minutes=50),
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'unpaused',
                    'created':  _now - timedelta(hours=5, minutes=25),
                },
            ],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.pauseEndsAt', time2iso_utc(shift.closes_at))

        with await shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 3, 'события добавлены')

            with shift.shift_events[-1] as event:
                tap.eq(event.shift_event_id, event_id, 'shift_event_id')
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.location.lat, 55.0, 'lat')
                tap.eq(event.location.lon, 33.0, 'lon')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )
                tap.eq(
                    event.detail['pro_event_id'],
                    event_id,
                    'pro_event_id'
                )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(204, diag=True)

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'processing', 'processing')
        tap.eq(len(shift.shift_events), 3, 'события не дублированы')


async def test_full_minute(tap, api, dataset, uuid, now):
    with tap.plan(3, 'Пауза смены не берётся тк считаем по минутам'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_max_count': 1,
                'restart_pause': True,
                'pause_duration': 125,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()

        _now = now().replace(microsecond=0)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[{
                'courier_id': courier.courier_id,
                'type': 'paused',
                'created':  _now - timedelta(hours=3, minutes=50, seconds=50),
            }, {
                'courier_id': courier.courier_id,
                'type': 'unpaused',
                'created':  _now - timedelta(hours=3, minutes=50, seconds=40),
            }, {
                'courier_id': courier.courier_id,
                'type': 'paused',
                'created':  _now - timedelta(hours=3, minutes=30, seconds=1),
            }, {
                'courier_id': courier.courier_id,
                'type': 'unpaused',
                'created':  _now - timedelta(hours=3, minutes=30),
            }],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_pause',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.0,
                    'longitude': 33.0,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'pause.pause_max_count_reached'
        )
