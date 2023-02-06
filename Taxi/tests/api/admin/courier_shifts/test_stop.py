import pytest

from stall.model.courier_shift import COURIER_SHIFT_STATUSES, CourierShiftEvent


@pytest.mark.parametrize('target_status', ['complete', 'leave'])
async def test_stop_processing(tap, api, dataset, uuid, target_status):
    with tap.plan(10, f'Попытка закрыть смену в статус "{target_status}"'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        event_started_id = uuid()
        courier_shift = await dataset.courier_shift(
            store=store,
            status='processing',
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': target_status,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, target_status, 'смена закрыта')
            tap.eq(len(shift.shift_events), 3, '+два новых события')

            with shift.shift_events[-2] as event:
                tap.eq(
                    event.shift_event_id,
                    f'{event_started_id}:stopped',
                    'started shift_event_id'
                )
                tap.eq(event.type, 'stopped', 'событие stopped')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, target_status, 'событие изменения статуса')
                tap.eq(event.user_id, user.user_id, 'user_id')


@pytest.mark.parametrize('reason', ['drunk', 'alien'])
@pytest.mark.parametrize('comment', ['кириллица это', 'english word', None])
async def test_stop_reason(tap, api, dataset, reason, comment):
    with tap.plan(9, f'Стоп с конкретной причиной "{reason}"/"{comment}"'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'status': 'complete',
                'reason': reason,
                'comment': comment,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'complete', 'complete')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'stopped', 'stopped')
                tap.eq(event.user_id, user.user_id, 'user_id')
                tap.eq(event.courier_id, None, 'courier_id none')
                tap.eq(event.detail['reason'], reason, 'причина')
                tap.eq(event.detail.get('comment'), comment, 'комментарий')


@pytest.mark.parametrize(
    'status',
    set(COURIER_SHIFT_STATUSES) - {'processing', 'complete', 'leave'}
)
async def test_stop_forbidden_status(tap, api, dataset, status):
    with tap.plan(4, f'Попытка завершить смену в статусе "{status}"'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        courier_shift = await dataset.courier_shift(store=store, status=status)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_COURIER_SHIFT_INVALID_STATUS')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, status, 'смена не изменилась')


@pytest.mark.parametrize('comment', [
    'x' * 201,  # слишком много
    '',         # слишком мало
])
async def test_stop_bad_comment(tap, api, dataset, comment):
    with tap.plan(3, f'Стоп с кривым комментарием - {comment}"'):
        user = await dataset.user(role='admin')

        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            status='processing',
            courier=courier,
            courier_id=courier.cluster_id,
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'status': 'complete',
                'comment': comment,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


async def test_stop_forbidden_reason(tap, api, dataset):
    with tap.plan(4, 'Попытка завершить смену c неверной причиной'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        courier_shift = await dataset.courier_shift(
            store=store,
            status='processing',
            shift_events=[
                CourierShiftEvent({
                    'type': 'started',
                }),
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
                'reason': 'close_time',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, 'processing', 'смена не изменилась')


async def test_stop_paused_shift(tap, api, dataset, uuid):
    with tap.plan(12, 'Завершение смены на паузе'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        event_started_id = uuid()
        courier_shift = await dataset.courier_shift(
            store=store,
            status='processing',
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
                CourierShiftEvent({'type': 'paused'})
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, 'complete', 'смена закрыта')
            tap.eq(len(shift.shift_events), 5, '+3 новых события')

            with shift.shift_events[-3] as event:
                tap.eq(event.type, 'unpaused', 'событие unpaused')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'stopped', 'событие stopped')
                tap.eq(
                    event.shift_event_id,
                    f'{event_started_id}:stopped',
                    'started shift_event_id'
                )
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'complete',
                       'событие изменения статуса')
                tap.eq(event.user_id, user.user_id, 'user_id')


async def test_stop_shift_with_changes(tap, api, dataset, uuid):
    with tap.plan(11, 'Завершение смены с предложенными изменениями'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        event_started_id = uuid()
        courier_shift = await dataset.courier_shift(
            store=store,
            status='processing',
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
                CourierShiftEvent({'type': 'change'})
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, 'complete', 'смена закрыта')
            tap.eq(len(shift.shift_events), 5, '+3 новых события')

            with shift.shift_events[-3] as event:
                tap.eq(event.type, 'rejected', 'событие rejected')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'stopped', 'событие stopped')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'complete',
                       'событие изменения статуса')
                tap.eq(event.user_id, user.user_id, 'user_id')


async def test_stop_shift_with_order(tap, api, dataset, uuid):
    with tap.plan(12, 'Завершение смены с актуальным заказом'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)
        courier = await dataset.courier(cluster=cluster)

        event_started_id = uuid()
        courier_shift = await dataset.courier_shift(
            status='processing',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
            ],
        )
        await dataset.order(
            courier_id=courier.courier_id,
            status='processing',
            estatus='waiting',
        )

        # пробуем завершить смену с заказом
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_HAS_PROCESSING')

        # жесткое завершение
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'leave',
                'force_stop': True,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, 'leave', 'смена закрыта')
            tap.eq(len(shift.shift_events), 3, '+2 новых события')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'stopped', 'событие stopped')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'leave', 'событие изменения статуса')
                tap.eq(event.user_id, user.user_id, 'user_id')


async def test_stop_shift_returning(tap, api, dataset, uuid, now):
    with tap.plan(12, 'Завершение смены с возвращающимся курьером'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)
        courier = await dataset.courier(cluster=cluster)

        event_started_id = uuid()
        courier_shift = await dataset.courier_shift(
            status='processing',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
            ],
        )
        await dataset.order(
            courier_shift=courier_shift,
            courier_id=courier.courier_id,
            status='complete',
            estatus='done',
        )
        courier.last_order_time = now()
        await courier.save()

        # пробуем завершить смену с заказом
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_COURIER_RETURNING')

        # курьер вернулся на лавку
        courier.checkin_time = now()
        await courier.save()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_stop',
            json={
                'courier_shift_id': courier_shift.courier_shift_id,
                'status': 'complete',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await courier_shift.reload() as shift:
            tap.eq(shift.status, 'complete', 'смена закрыта')
            tap.eq(len(shift.shift_events), 3, '+2 новых события')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'stopped', 'событие stopped')
                tap.eq(event.user_id, user.user_id, 'user_id')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'complete', 'событие изменения статуса')
                tap.eq(event.user_id, user.user_id, 'user_id')
