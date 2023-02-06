from datetime import timedelta, time

import pytest

from libstall.util import time2time, tzone
from libstall.model import coerces
from stall.model.courier_shift import COURIER_SHIFT_STATUSES


async def test_refuse(tap, api, dataset, now):
    with tap.plan(14, 'Отказ от смены'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() - timedelta(minutes=1)),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'released', 'status')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')

            with shift.shift_events[0] as event:
                tap.ok(event.shift_event_id, 'shift_event_id')
                tap.eq(event.type, 'refuse', 'событие отказа')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')
            with shift.shift_events[1] as event:
                tap.ok(event.shift_event_id, 'shift_event_id')
                tap.eq(event.type, 'released', 'событие закрытия смены')

        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.not_refusable',
        )


async def test_wrong_shift(tap, api, dataset, uuid):
    with tap.plan(3, 'Отказ от смены'):
        courier = await dataset.courier()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': uuid(),
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.shift_does_not_exist',
        )


@pytest.mark.parametrize(
    'status', [x for x in COURIER_SHIFT_STATUSES if x not in {'waiting'}]
)
async def test_processing(tap, api, dataset, now, status):
    with tap.plan(5, 'Отказ только если не исполнялся'):
        store = await dataset.store()
        courier = await dataset.courier()

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=(now() - timedelta(minutes=1)),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)

        if status == 'processing':
            t.json_is(
                'errors.0.attributes.code',
                'core.courier_shift.shift_flow_manager.validator.'
                'refuse.has_events',
            )
        else:
            t.json_is(
                'errors.0.attributes.code',
                'core.courier_shift.shift_flow_manager.validator.'
                'refuse.not_refusable',
            )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, status, 'Статус не менялся')


async def test_refuse_disabled(tap, api, dataset, now):
    with tap.plan(6, 'запрещено отказываться от смен'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'shift_close_disable': True,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() + timedelta(minutes=1)),
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.temporary_unavailable',
        )

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')


# время начала смены 2020-01-05T18:00:00
@pytest.mark.parametrize(
    ['shift_setup', 'max_close_time'],
    [
        ({'shift_close_time': time(14, 30, 0)}, '2020-01-04T14:30:00+03'),
        ({'shift_close_before_days': 2}, '2020-01-03T18:00:00'),
        (
            {'shift_close_time': time(14, 30, 0), 'shift_close_before_days': 3},
            '2020-01-02T14:30:00+03',
        ),
    ],
)
async def test_refuse_too_late(
    tap, api, dataset, time_mock, shift_setup, max_close_time
):
    with tap.plan(11, 'закрывать можно только до определенного часа'):
        cluster = await dataset.cluster(courier_shift_setup=shift_setup)
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=coerces.date_time('2020-01-05T18:00:00'),
        )

        # опоздали с отменой на одну минуту
        time_mock.set(coerces.date_time(max_close_time) + timedelta(minutes=1))

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.not_refusable',
        )

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')

        # есть ещё минута, чтобы успеть отказаться
        time_mock.set(time_mock.now() - timedelta(minutes=2))

        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'released', 'статус изменился')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')


@pytest.mark.parametrize(
    'tz',
    [
        'America/Caracas',
        'UTC',
        'Europe/Moscow',
        'Asia/Hong_Kong',
    ],
)
@pytest.mark.parametrize(
    'local_started_at',
    [
        '2020-01-05T00:00:00',
        '2020-01-05T23:59:59',
    ],
)
async def test_refuse_timezone_ok(
    tap, api, dataset, time_mock, tz, local_started_at
):
    with tap.plan(5, 'закрывать можно только до определенного часа'):
        local_max_close_time = '2020-01-04T14:30:00'

        cluster = await dataset.cluster(
            courier_shift_setup={'shift_close_time': time(14, 30, 0)}
        )
        store = await dataset.store(cluster=cluster, tz=tz)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=time2time(local_started_at).replace(
                tzinfo=tzone(tz)
            ),
        )

        # есть ещё минута, чтобы успеть отказаться
        time_mock.set(
            time2time(local_max_close_time).replace(tzinfo=tzone(tz))
            - timedelta(minutes=1)
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        with await shift.reload() as shift:
            tap.eq(shift.status, 'released', 'статус изменился')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 2, 'события добавлены')


@pytest.mark.parametrize(
    'tz',
    [
        'America/Caracas',
        'UTC',
        'Europe/Moscow',
        'Asia/Hong_Kong',
    ],
)
@pytest.mark.parametrize(
    'local_started_at',
    [
        '2020-01-05T00:00:00',
        '2020-01-05T23:59:59',
    ],
)
async def test_refuse_timezone_fail(
    tap, api, dataset, time_mock, tz, local_started_at
):
    with tap.plan(6, 'закрывать можно только до определенного часа'):
        local_max_close_time = '2020-01-04T14:30:00'

        cluster = await dataset.cluster(
            courier_shift_setup={'shift_close_time': time(14, 30, 0)}
        )
        store = await dataset.store(cluster=cluster, tz=tz)
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=time2time(local_started_at).replace(
                tzinfo=tzone(tz)
            ),
        )

        # опоздали с отменой на одну минуту
        time_mock.set(
            time2time(local_max_close_time).replace(tzinfo=tzone(tz))
            + timedelta(minutes=1)
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_refuse',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.not_refusable',
        )

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')
