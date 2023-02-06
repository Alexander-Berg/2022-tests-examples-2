import pytest

from stall.client.grocery_checkins import GroceryCheckinsError
from stall.client.grocery_checkins import client as gc_client


async def test_pause(tap, api, dataset, time2time):
    with tap.plan(14, 'Остановка смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
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
            'api_admin_courier_shifts_pause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )

        with await shift.reload():
            pause = shift.shift_events[-2]
            tap.ok(pause, 'Пауза была')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.user_id, user.user_id, 'user_id')
                tap.eq(event.courier_id, None, 'courier_id none')
                tap.eq(event.detail.get('duration'), None, 'duration none')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )

        await t.post_ok(
            'api_admin_courier_shifts_pause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Повторная остановка успешна')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )


async def test_same_duration(tap, api, dataset):
    with tap.plan(6, 'Пауза с теми же настройками'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
            status='processing',
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
                    'detail': {'duration': 600},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_pause',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'duration': 600,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )

        with await shift.reload():
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.detail.get('duration'), 600, 'duration тот же')


async def test_another_duration(tap, api, dataset):
    with tap.plan(5, 'Пауза с другими настройками'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
            status='processing',
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
                    'detail': {'duration': 600},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_pause',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'duration': 500,
            },
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')

        with await shift.reload():
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.detail.get('duration'), 600, 'duration не менялся')


async def test_gone(tap, api, dataset):
    with tap.plan(3, 'Заказ уже завершен'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
            status='complete',
            shift_events=[
                {
                    'courier_id': courier.courier_id,
                    'type': 'started',
                    'location': {'lon': 33, 'lat': 55},
                },
                {
                    'courier_id': courier.courier_id,
                    'type': 'stopped',
                    'location': {'lon': 33, 'lat': 55},
                },
            ],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_pause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')


async def test_ignore_cluster(tap, api, dataset, time2time):
    with tap.plan(10, 'Бесконечная пауза до конца смены, игнорируя настройки'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_duration': 60},
        )
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)
        shift   = await dataset.courier_shift(
            store=store,
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
            'api_admin_courier_shifts_pause',
            json={'courier_shift_id': shift.courier_shift_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            shift.courier_shift_id,
            'идентификатор'
        )

        with await shift.reload():
            pause = shift.shift_events[-2]
            tap.ok(pause, 'Пауза была')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.user_id, user.user_id, 'user_id')
                tap.eq(event.courier_id, None, 'courier_id none')
                tap.eq(event.detail.get('duration'), None, 'duration none')
                tap.eq(
                    time2time(event.detail.get('ends_at')),
                    shift.closes_at,
                    'ends_at'
                )


async def test_grocery_checkins_sync(
        tap, dataset, ext_api, api, time2iso
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
            t = await api(role='admin')
            await t.post_ok(
                'api_admin_courier_shifts_pause',
                json={
                    'courier_shift_id': shift.courier_shift_id,
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
        tap, dataset, ext_api, api,
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
            t = await api(role='admin')
            await t.post_ok(
                'api_admin_courier_shifts_pause',
                json={
                    'courier_shift_id': shift.courier_shift_id,
                },
            )
            t.status_is(200, diag=True)

        with await shift.reload() as shift:
            event = shift.event_paused()
            tap.ok(not event, 'shift is not on pause')
            event = shift.event_schedule_pause()
            tap.ok(event, 'shift is not on schedule_pause')
            tap.eq(_calls, [], 'grocery_checkins not called')


@pytest.mark.parametrize('exc_cls', [GroceryCheckinsError, Exception])
async def test_grocery_checkins_sync_fail(
        tap, dataset, api, monkeypatch, exc_cls
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

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_pause',
            json={
                'courier_shift_id': shift.courier_shift_id,
            },
        )
        t.status_is(200, diag=True)

        with await shift.reload() as shift:
            event = shift.event_paused()
            tap.ok(event, 'shift is on pause')


@pytest.mark.parametrize('reason', ['got_wet', 'transport_breakdown'])
@pytest.mark.parametrize('comment', ['кириллица это', 'english word', None])
async def test_pause_reason(tap, api, dataset, reason, comment):
    with tap.plan(8, f'Пауза с конкретной причиной "{reason}"/"{comment}"'):
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
            'api_admin_courier_shifts_pause',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'reason': reason,
                'comment': comment,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')
                tap.eq(event.user_id, user.user_id, 'user_id')
                tap.eq(event.courier_id, None, 'courier_id none')
                tap.eq(event.detail['reason'], reason, 'причина')
                tap.eq(event.detail.get('comment'), comment, 'комментарий')


@pytest.mark.parametrize('comment', [
    'x' * 201,  # слишком много
    '',         # слишком мало
])
async def test_pause_bad_comment(tap, api, dataset, comment):
    with tap.plan(3, f'Пауза с кривым комментарием - {comment}"'):
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
            'api_admin_courier_shifts_pause',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'comment': comment,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
