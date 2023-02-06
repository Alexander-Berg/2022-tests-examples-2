# pylint: disable=too-many-locals,too-many-arguments,too-many-lines

from datetime import timedelta
import pytest

from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_simple(tap, api, dataset, time2iso_utc, now, tzone, uuid):
    with tap.plan(16, 'Поменять нескольких смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=['best'],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
        )
        shift_new1 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=4),
            schedule=[{
                'tags': ['best'],
                'time': now() - timedelta(hours=1),
            }, {
                'tags': [],
                'time': now() + timedelta(hours=1),
            }],
        )
        shift_new2 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=6),
            closes_at=day.replace(hour=8),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new1.group_id,
                    'startsAt': time2iso_utc(shift_new1.started_at),
                    'endsAt': time2iso_utc(shift_new1.closes_at),
                    'startPointId': store.store_id,
                }, {
                    'id': shift_new2.group_id,
                    'startsAt': time2iso_utc(shift_new2.started_at),
                    'endsAt': time2iso_utc(shift_new2.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(204, diag=True)

        with await shift_new1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.shift_events[0].detail.get('swap'), True, 'swapped')

        with await shift_new2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.shift_events[0].detail.get('swap'), True, 'swapped')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'released', 'статус изменился')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 4, '4 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished', 'refuse', 'released'],
                   'обмен сменами прошел ожидаемо')


async def test_last_wrong(tap, api, dataset, time2iso_utc, now, tzone, uuid):
    with tap.plan(18, 'Назначенные смены откатываются после ошибки'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])
        courier = await dataset.courier(
            cluster=cluster,
            tags=tags,
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
            courier_tags=tags,
        )
        shift_new1 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=4),
            schedule=[{
                'tags': ['best'],
                'time': now() - timedelta(hours=2),
            }, {
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        shift_new2 = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=6),
            closes_at=day.replace(hour=8),
            schedule=[{
                'tags': ['best'],
                'time': now() - timedelta(hours=1),
            }, {
                'tags': [],
                'time': now() + timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new1.group_id,
                    'startsAt': time2iso_utc(shift_new1.started_at),
                    'endsAt': time2iso_utc(shift_new1.closes_at),
                    'startPointId': store.store_id,
                }, {
                    'id': shift_new2.group_id,
                    'startsAt': time2iso_utc(shift_new2.started_at),
                    'endsAt': time2iso_utc(shift_new2.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)

        with await shift_new1.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 2, 'событие добавлено и отменено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.shift_events[0].detail.get('swap'), True, 'swapped')
            tap.eq(shift.shift_events[1].type, 'request', 'request')
            tap.eq(shift.courier_tags, None, 'курьерских теги убраны')

        with await shift_new2.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')
            tap.eq(shift.courier_tags, None, 'курьерских теги не появились')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 2, '2 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished'],
                   'обмен сменами прошел неудачно')
            tap.eq(shift.courier_tags, tags, 'курьерских теги на месте')


async def test_wrong_shift(tap, api, dataset, time2iso_utc, now, tzone, uuid):
    with tap.plan(6, 'Пытаемся сменить неправильную смену'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': uuid(),
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')


async def test_wrong_status(tap, api, dataset, time2iso_utc, now, tzone, uuid):
    with tap.plan(9, 'Пытаемся сменить смену с неправильным статусом'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='request',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
        )

        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=4),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.lock.not_acquired'
        )

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')


async def test_wrong_courier(tap, api, dataset, time2iso_utc, now, tzone, uuid):
    with tap.plan(8, 'Пытаемся сменить смену другого курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
        )

        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=5),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')


async def test_ignore_swapped_shift(
        tap, api, dataset, time2iso_utc, now, tzone, uuid
):
    with tap.plan(11, 'Поменять смену на другую, с учетом ограничений на день'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 2,
                'max_week_hours': 2,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=['best'],
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=5),
        )
        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=5),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(204, diag=True)

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.shift_events[0].detail.get('swap'), True, 'swapped')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'released', 'статус изменился')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 4, '4 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished', 'refuse', 'released'],
                   'обмен сменами прошел ожидаемо')


@pytest.mark.parametrize(
    'start,close,between_stores',
    [
        # [10, 14, 0],     # пересечение СТЫК В СТЫК слева (НЕ СЧИТАЕТСЯ)
        [10, 14, 600],     # пересечение СТЫК В СТЫК слева + 10м на дорогу
        [11, 15, 0],       # пересечение на 1 час слева
        [11, 19, 0],       # охватывает целиком
        [15, 17, 0],       # лежит внутри
        [17, 20, 0],       # пересечение на 2 часа справа
        [18, 20, 0],       # пересечение СТЫК В СТЫК справа годится для обмена
    ]
)
async def test_swap_intersection(       # pylint: disable=too-many-locals
        tap, api, dataset, time2iso_utc, start, close, between_stores,
        now, tzone, uuid
):
    with tap.plan(11, 'Обмен сменами, которые как-то пересекаются'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'duration_between_stores': between_stores,
            },
        )
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        shift_old = await dataset.courier_shift(
            store=store1,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=18),
        )
        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store2,
            tags=[],
            started_at=day.replace(hour=start),
            closes_at=day.replace(hour=close),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store2.store_id,
                }],
            }
        )

        t.status_is(204, diag=True)

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(len(shift.shift_events), 1, 'событие добавлено')
            tap.eq(shift.shift_events[0].type, 'waiting', 'waiting')
            tap.eq(shift.shift_events[0].detail.get('swap'), True, 'swapped')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'released', 'статус изменился')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер остался')
            tap.eq(len(shift.shift_events), 4, '4 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished', 'refuse', 'released'],
                   'обмен сменами прошел ожидаемо')


@pytest.mark.parametrize(
    'start,close,between_stores',
    [
        [10, 14, 0],       # пересечение СТЫК В СТЫК слева НЕ СЧИТАЕТСЯ
        [10, 13, 3600],    # пересечение СТЫК В СТЫК слева за счет 1ч на дорогу
        [11, 13, 0],       # пересечение нет (слева)
        [19, 21, 0],       # пересечение нет (справа)
        [19, 21, None],    # пересечение нет (справа), задержка не задана
        # [18, 20, 0],     # пересечение СТЫК В СТЫК справа годится для обмена
    ]
)
async def test_swap_no_intersection(    # pylint: disable=too-many-locals
        tap, api, dataset, time2iso_utc, start, close, between_stores,
        now, tzone, uuid
):
    with tap.plan(9, 'Обмен сменами, которые почти никак не пересекаются'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'duration_between_stores': between_stores,
            },
        )
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[],
            delivery_type='foot',
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        shift_old = await dataset.courier_shift(
            store=store1,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=18),
        )
        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store2,
            tags=[],
            started_at=day.replace(hour=start),
            closes_at=day.replace(hour=close),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store2.store_id,
                }],
            }
        )
        t.status_is(400, diag=True)

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 2, '2 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished'],
                   'обмен сменами прошел неудачно')


async def test_refuse_disabled(
        tap, api, dataset, time2iso_utc, now, tzone, uuid
):
    with tap.plan(9, 'запрещено обмениваться сменами'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'shift_close_disable': True,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=5),
        )
        shift_new = await dataset.courier_shift(
            status='request',
            delivery_type='foot',
            store=store,
            tags=[],
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=5),
            schedule=[{
                'tags': [],
                'time': now() - timedelta(hours=1),
            }],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'refuse.temporary_unavailable',
        )

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 0, 'события не добавлены')

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')


async def test_blocks(tap, api, dataset, now, uuid, time2iso_utc):
    with tap.plan(5, 'Курьер имеет блокировку'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            blocks=[{'source': 'wms', 'reason': 'blocked'}],
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=7),
        )
        shift_new = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=4),
            schedule=[
                {'tags': [], 'time': now() - timedelta(hours=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [
                    {
                        'id': shift_new.group_id,
                        'startsAt': time2iso_utc(shift_new.started_at),
                        'endsAt': time2iso_utc(shift_new.closes_at),
                        'startPointId': store.store_id,
                    },
                ],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift_new.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.remote_services.'
            'invalid_work_status'
        )


async def test_no_intersection_with_any(
        tap, api, dataset, time2iso_utc, now, tzone, uuid
):
    with tap.plan(12, 'Обмен невозможен если пересекает имеющуюся смену'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=['best'],
        )

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

        # эта смена помешает
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=1),
            closes_at=day.replace(hour=3),
        )
        shift_old = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=3),
            closes_at=day.replace(hour=5),
        )

        # новая смена на час раньше, она пересекается с предыдущей
        shift_new = await dataset.courier_shift(
            status='request',
            store=store,
            tags=[],
            started_at=day.replace(hour=2),
            closes_at=day.replace(hour=5),
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_old.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_new.group_id,
                    'startsAt': time2iso_utc(shift_new.started_at),
                    'endsAt': time2iso_utc(shift_new.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(400, diag=True)
        t.json_is('errors.0.id', shift_new.group_id)
        t.json_is('errors.0.type', 'error')
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.intersection',
            'пересечение с одной из имеющихся смен'
        )

        with await shift_new.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'курьер не назначен')
            tap.eq(len(shift.shift_events), 0, 'событие не добавлено')

        with await shift_old.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting')
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не снят')
            tap.eq(len(shift.shift_events), 2, '2 события добавлены')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished'],
                   'обмен сменами прошел неудачно')


async def test_tag_beginner(
    tap, api, dataset, uuid, now, time2iso_utc, push_events_cache, job
):
    with tap.plan(13, 'Новичок обменивается на более позднюю смену'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)

        # две смены курьера
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[TAG_BEGINNER],
            schedule=[
                {'tags': [], 'time': now() - timedelta(days=1)},
            ],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=5),
            closes_at=_now + timedelta(hours=8),
            tags=[TAG_BEGINNER],
            schedule=[
                {'tags': [], 'time': now() - timedelta(days=1)},
            ],
        )

        # смену_1 обменяем на смену_3
        shift_3 = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=4),
            closes_at=_now + timedelta(hours=5),
            tags=[],
            schedule=[
                {'tags': [], 'time': now() - timedelta(days=1)},
            ],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_swap',
            params_path={
                'courier_shift_id': shift_1.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            },
            json={
                'id': uuid(),
                'items': [{
                    'id': shift_3.group_id,
                    'startsAt': time2iso_utc(shift_3.started_at),
                    'endsAt': time2iso_utc(shift_3.closes_at),
                    'startPointId': store.store_id,
                }],
            }
        )

        t.status_is(204, diag=True)

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'released', 'смену сдали #1')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #1')
            tap.eq(shift.tags, [TAG_BEGINNER], 'смена - новичок в отставке #1')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена все еще назначена #2')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен #2')
            tap.eq(shift.tags, [], 'тегов нет #2')

        with await shift_3.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена назначена #3')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен #3')
            tap.eq(shift.tags, [TAG_BEGINNER], 'смена теперь Новичок #3')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'курьер все еще новичок')
