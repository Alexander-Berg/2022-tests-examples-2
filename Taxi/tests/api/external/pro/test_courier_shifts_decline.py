from datetime import timedelta

import pytest

from stall.model.courier_shift import COURIER_SHIFT_STATUSES
from stall.model.courier_shift_tag import TAG_BEGINNER


@pytest.mark.parametrize('tags', (
    [],              # обычный курье
    [TAG_BEGINNER],  # новичок
))
async def test_decline(
    tap, api, dataset, now, uuid, push_events_cache, job, tags,
):
    # pylint: disable=too-many-locals
    with tap.plan(18, f'Отказ от изменений - {tags}'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster, tags=tags)

        old_started_at = (now() + timedelta(hours=1)).replace(microsecond=0)
        new_started_at = (now() + timedelta(hours=2)).replace(microsecond=0)

        change_event_id = uuid()
        shift = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='waiting',
            started_at=old_started_at,
            shift_events=[
                {'type': 'request'},
                {'type': 'waiting', 'courier_id': courier.courier_id},
                {
                    'shift_event_id': change_event_id,
                    'type': 'change',
                    'courier_id': courier.courier_id,
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                            'guarantee': None,
                        },
                        'new': {
                            'started_at': new_started_at,
                            'guarantee': '123.00',
                        },
                    },
                },
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_decline',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(204, diag=True)

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.eq(await job.take(), None, 'Задание нет')

        with await shift.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не менялся')
            tap.eq(len(shift.shift_events), 4, 'события добавлены')

            tap.eq(shift.started_at, old_started_at, 'started_at не применены')
            tap.eq(shift.guarantee, None, 'guarantee не применены')

            tap.ok(not shift.event_change(), 'изменений нет')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'change', 'change')
            with shift.shift_events[-1] as event:
                tap.eq(
                    f'{change_event_id}:rejected',
                    event.shift_event_id,
                    'id события'
                )
                tap.eq(event.type, 'rejected', 'rejected')
                tap.eq(event.courier_id, courier.courier_id, 'courier_id')
                tap.eq(event.user_id, None, 'user_id')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_decline',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
        )
        t.status_is(400, diag=True)
        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, 'waiting', 'статус не менялся')
        tap.eq(len(shift.shift_events), 4, 'события не дублированы')


@pytest.mark.parametrize(
    'status',
    [x for x in COURIER_SHIFT_STATUSES if x not in {'waiting', 'processing'}]
)
async def test_status(tap, api, dataset, now, status):
    with tap.plan(5, 'Только  доступных статусах'):
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
            'api_external_pro_courier_shifts_decline',
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
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )

        tap.ok(await shift.reload(), 'Получили смену')
        tap.eq(shift.status, status, 'Статус не менялся')
