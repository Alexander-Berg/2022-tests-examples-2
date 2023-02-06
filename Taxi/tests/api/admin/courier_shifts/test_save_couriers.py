# pylint: disable=too-many-locals,too-many-lines

from datetime import timezone, timedelta

import pytest

from stall.model.courier_shift_tag import TAG_BEGINNER


@pytest.mark.parametrize(
    'param_name,value_before,value_after', (
        ('tags', ['one', 'two'], ['new_1', 'new_2']),
        ('delivery_type', 'rover', 'car'),
    )
)
async def test_save_update_simultaneously(
        tap, api, dataset, now, param_name, value_before, value_after,
):
    with tap.plan(17, 'Обновление курьера и доставки/тегов смены одновременно'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster,
                                        **{param_name: value_before})
        user = await dataset.user(store=store, role='admin')

        # создаем смену без курьера
        shift = await dataset.courier_shift(
            store=store,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            **{param_name: value_before}
        )
        tap.ok(shift, 'смена создана')

        # редактируем теги/доставку + курьера, который с новыми уже не совместим
        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'courier_id': courier.courier_id,
                            **{param_name: value_after}
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        # отдельно редактируем теги/доставку
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            **{param_name: value_after}
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.eq(t.res['json']['courier_shift'][param_name],
               value_after,
               'параметр установлен')

        # отдельно редактируем, пробуем назначит неподходящего курьера
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'courier_id': courier.courier_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        # редактируем теги/доставку и курьера, который совместим
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'courier_id': courier.courier_id,
                            # 'status': 'processing',     # игнорируется
                            **{param_name: value_before}
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.courier_id', courier.courier_id, 'courier_id')
        t.json_is('courier_shift.status', 'waiting', 'status')
        tap.eq(t.res['json']['courier_shift'][param_name],
               value_before,
               'параметр установлен')


async def test_set_courier(tap, api, dataset):
    with tap.plan(9, 'Назначение курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])
        courier = await dataset.courier(cluster=cluster, tags=tags)

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.courier_id', courier.courier_id, 'courier_id')
        t.json_is('courier_shift.status', 'waiting', 'waiting')
        t.json_is('courier_shift.shift_events.0.type', 'waiting')
        t.json_is('courier_shift.courier_tags.0', tags[0])
        t.json_is('courier_shift.courier_tags.1', tags[1])
        t.json_hasnt('courier_shift.courier_tags.2')


async def test_set_courier_any_delivery(tap, api, dataset):
    with tap.plan(6, 'Назначение курьера с чужим типом доставки'):
        cluster = await dataset.cluster(courier_shift_setup={
            'delivery_type_check_enable': False,
        })
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster, delivery_type='foot')
        shift = await dataset.courier_shift(
            store=store,
            status='request',
            delivery_type='car',
        )

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.courier_id', courier.courier_id, 'courier_id')
        t.json_is('courier_shift.status', 'waiting', 'waiting')
        t.json_is('courier_shift.shift_events.0.type', 'waiting')


async def test_set_courier_beginner(tap, api, dataset, push_events_cache, job):
    with tap.plan(7, 'Назначение курьера-новичка на смену'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        shift = await dataset.courier_shift(
            store=store,
            status='request',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера назначен')
            tap.eq(shift.tags, [TAG_BEGINNER], 'теперь смена - новичок')


async def test_drop_courier(tap, api, dataset, uuid):
    with tap.plan(7, 'Снятие курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier,
            tags=[uuid(), uuid()]
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.courier_id', None, 'courier_id=None')
        t.json_is('courier_shift.status', 'request', 'request')
        t.json_is('courier_shift.shift_events.0.type', 'request')
        t.json_is('courier_shift.courier_tags', None, 'courier_tags=None')


async def test_drop_courier_beginner(tap, api, dataset, push_events_cache, job):
    with tap.plan(7, 'Снятие курьера-новичка'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier,
            tags=[TAG_BEGINNER],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': None,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(shift.status, 'request', 'свободна')
            tap.eq(shift.courier_id, None, 'курьера нет')
            tap.eq(shift.tags, [], 'тег новичок снят')


async def test_replace_courier(tap, api, dataset):
    with tap.plan(6, 'Замена курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        tag_1 = (await dataset.courier_shift_tag(type='courier')).title
        tag_2 = (await dataset.courier_shift_tag(type='courier')).title
        courier_1 = await dataset.courier(cluster=cluster, tags=[tag_1])
        courier_2 = await dataset.courier(cluster=cluster, tags=[tag_2])

        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier_1,
            courier_tags=[tag_1],
        )

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier_2.courier_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier_2.courier_id, 'курьер #2')
            tap.eq(shift.courier_tags, [tag_2], 'теги курьера обновились')


async def test_replace_courier_beginner(
    tap, api, dataset, push_events_cache, job,
):
    with tap.plan(11, 'Замена курьера-новичка на курьера-новичка'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier_1 = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        courier_2 = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])

        # обе смены первого курьера
        shift_1 = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier_1,
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier_1,
            tags=[],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift_1.courier_shift_id,
                'courier_id': courier_2.courier_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')
        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # осталась новичком, т.к. второй курьер тоже новичок
        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier_2.courier_id, 'курьер #2')
            tap.eq(shift.tags, [TAG_BEGINNER], 'все еще смена-новичок')

        # стала новичком, т.к. первую отобрали
        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'назначена')
            tap.eq(shift.courier_id, courier_1.courier_id, 'курьер #1')
            tap.eq(shift.tags, [TAG_BEGINNER], 'теперь смена-новичок')


async def test_assign_no_changes(tap, api, dataset, now):
    with tap.plan(4, 'Курьер не должен аппрувить параметры при назначении'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
        )

        # редактируем теги/доставку + курьера, который с новыми уже не совместим
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
                'started_at': _now + timedelta(hours=2),
                'closes_at': _now + timedelta(hours=4),
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.ok(
                not [x for x in shift.shift_events if x.type == 'change'],
                'Нет события изменений'
            )


async def test_reassign_no_changes(tap, api, dataset, now):
    with tap.plan(4, 'Курьер не должен аппрувить параметры при переназначении'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        shift = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier1,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
        )

        # редактируем теги/доставку + курьера, который с новыми уже не совместим
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier2.courier_id,
                'started_at': _now + timedelta(hours=2),
                'closes_at': _now + timedelta(hours=4),
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.ok(
                not [x for x in shift.shift_events if x.type == 'change'],
                'Нет события изменений'
            )


async def test_changes(tap, api, dataset, now, time2time):
    with tap.plan(8, 'Курьер должен аппрувить параметры при редактировании'):
        _now = now(tz=timezone.utc).replace(microsecond=0)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(store=store, role='admin')

        old_started_at = _now + timedelta(hours=1)
        old_closes_at = _now + timedelta(hours=3)
        new_started_at = _now + timedelta(hours=2)
        new_closes_at = _now + timedelta(hours=4)

        shift = await dataset.courier_shift(
            status='waiting',
            courier=courier,
            store=store,
            started_at=old_started_at,
            closes_at=old_closes_at,
        )

        # редактируем теги/доставку + курьера, который с новыми уже не совместим
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
                'started_at': new_started_at,
                'closes_at': new_closes_at,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'change', 'change')
                tap.eq(
                    time2time(event.detail.get('old', {}).get('started_at')),
                    old_started_at,
                    'old started_at'
                )
                tap.eq(
                    time2time(event.detail.get('old', {}).get('closes_at')),
                    old_closes_at,
                    'old closes_at'
                )
                tap.eq(
                    time2time(event.detail.get('new', {}).get('started_at')),
                    new_started_at,
                    'new started_at'
                )
                tap.eq(
                    time2time(event.detail.get('new', {}).get('closes_at')),
                    new_closes_at,
                    'new closes_at'
                )


async def test_set_courier_fail_time(tap, api, dataset, now):
    with tap.plan(3, 'Назначение курьера невозможно т.к. не пройдет проверку'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                # Проверяем что смены не вылезут за 2 часа в день
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 1 час которая уже есть
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        shift = await dataset.courier_shift(
            store=store,
            status='template',
            started_at=day.replace(hour=17),
            closes_at=day.replace(hour=19),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_EXCEEDING_DURATION_DAY')


async def test_set_time_fail_courier(tap, api, dataset, now):
    with tap.plan(3, 'Изменение времени на смене с курьером не подходит'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                # Проверяем что смены не вылезут за 2 часа в день
                'max_day_hours': 3,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 1 час которая уже есть
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=13),
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=15),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'closes_at': day.replace(hour=18),
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_EXCEEDING_DURATION_DAY')


async def test_intersection_fail(tap, api, dataset, now):
    with tap.plan(3, 'Изменение смены не должно повлечь пересечение с другой'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 1 час которая уже есть
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=14),
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=15),
            closes_at=day.replace(hour=16),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'started_at': day.replace(hour=13),
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_COURIER_SHIFT_INTERSECTION')


async def test_follow(tap, api, dataset, now, time2time):
    with tap.plan(7, 'Изменение смены на стык в стык разрешено'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now() + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Смена на 1 час которая уже есть
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=14),
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=15),
            closes_at=day.replace(hour=16),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'started_at': day.replace(hour=14),
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload() as shift:
            tap.eq(
                shift.started_at,
                day.replace(hour=15),
                'started_at не поменялось'
            )
            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'change', 'Предложено изменение')
                tap.eq(
                    time2time(event.detail['old']['started_at']),
                    day.replace(hour=15),
                    'old'
                )
                tap.eq(
                    time2time(event.detail['new']['started_at']),
                    day.replace(hour=14),
                    'new'
                )


async def test_set_mentor(tap, api, dataset):
    with tap.plan(8, 'Назначение наставника. Успех.'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            tags=[TAG_BEGINNER],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift.mentor_shift_id',
            mentor_shift.courier_shift_id,
            'mentor_shift_id',
        )

        # повторное назначение ничего не ломает
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift.mentor_shift_id',
            mentor_shift.courier_shift_id,
            'mentor_shift_id',
        )


async def test_drop_mentor(tap, api, dataset):
    with tap.plan(4, 'Снятие наставника'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            tags=[TAG_BEGINNER],
        )

        mentor = await dataset.courier(cluster=cluster)
        await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': None,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift.mentor_shift_id', None, 'mentor_shift_id')


async def test_replace_mentor(tap, api, dataset):
    with tap.plan(4, 'Замена наставника'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        mentor_1 = await dataset.courier(cluster=cluster)
        mentor_shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor_1,
            status='processing',
            shift_events=[{'type': 'started'}],
        )
        mentor_2 = await dataset.courier(cluster=cluster)
        mentor_shift_2 = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor_2,
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            tags=[TAG_BEGINNER],
            mentor_shift_id=mentor_shift_1.courier_shift_id,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift_2.courier_shift_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift.mentor_shift_id',
            mentor_shift_2.courier_shift_id,
            'наставник заменен'
        )


@pytest.mark.parametrize('duration', [7200, 6000])
async def test_mentor_intersections(tap, api, dataset, now, duration):
    with tap.plan(8, 'Назначение наставника. Пересечения 1ч и 2ч'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': duration,
        })
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            courier=beginner,
            cluster=cluster,
            status='processing',
            shift_events=[{'type': 'started'}],
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[TAG_BEGINNER],
        )

        # пересекаются недостаточно
        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            courier=mentor,
            cluster=cluster,
            status='processing',
            shift_events=[{'type': 'started'}],
            started_at=_now - timedelta(hours=3),
            closes_at=_now + timedelta(hours=2),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_WORKING_INTERVAL')

        with await beginner_shift.reload() as shift:
            tap.eq(shift.mentor_shift_id, None, 'наставник не назначен')

        # продляем наставнику смену
        mentor_shift.closes_at = _now + timedelta(hours=3)
        await mentor_shift.save()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift.mentor_shift_id',
            mentor_shift.courier_shift_id,
            'mentor_shift_id',
        )


async def test_mentor_ignore_absent(tap, api, dataset, now):
    with tap.plan(4, 'Игнор опозданий/отмен/отказов смен с наставником'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)

        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            started_at=_now + timedelta(hours=10),  # очень трудолюбивый ментор
            closes_at=_now + timedelta(hours=22),
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='absent',
            tags=[TAG_BEGINNER],
            started_at=_now + timedelta(hours=10),
            closes_at=_now + timedelta(hours=12),
            mentor_shift_id=mentor_shift.courier_shift_id,  # ранее был назначен
        )
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            tags=[TAG_BEGINNER],
            started_at=_now + timedelta(hours=12),
            closes_at=_now + timedelta(hours=14),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is(
            'courier_shift.mentor_shift_id',
            mentor_shift.courier_shift_id,
            'mentor_shift_id',
        )


async def test_mentor_err_not_beginner(tap, api, dataset):
    with tap.plan(4, 'Назначение наставника. Ошибка, т.к. не новичок'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_second_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
            shift_events=[{'type': 'started'}],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_second_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        with await beginner_second_shift.reload() as shift:
            tap.eq(shift.mentor_shift_id, None, 'наставник не назначен')


async def test_mentor_err_busy(tap, api, dataset):
    with tap.plan(4, 'Назначение наставника. Ошибка, наставник занят'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            tags=[TAG_BEGINNER],
        )

        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
            shift_events=[{'type': 'started'}],
        )
        await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            mentor_shift_id=mentor_shift.courier_shift_id,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        with await beginner_shift.reload() as shift:
            tap.eq(shift.mentor_shift_id, None, 'наставник не назначен')


async def test_mentor_err_no_overlap(tap, api, dataset, now):
    with tap.plan(4, 'Назначение наставника. Ошибка, т.к. нет пересечения'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)

        _now = now(tz=timezone.utc).replace(microsecond=0)
        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='processing',
            shift_events=[{'type': 'started'}],
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[TAG_BEGINNER],
        )

        # не пересекаются
        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
            shift_events=[{'type': 'started'}],
            started_at=_now + timedelta(hours=10),
            closes_at=_now + timedelta(hours=13),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_WORKING_INTERVAL')

        with await beginner_shift.reload() as shift:
            tap.eq(shift.mentor_shift_id, None, 'наставник не назначен')


async def test_mentor_err_not_processing(tap, api, dataset, now):
    with tap.plan(4, 'Попытка назначить наставника не в processing статусе'):
        cluster = await dataset.cluster(courier_shift_setup={
            'beginner_auto_pause_duration': 7200,
        })
        user = await dataset.user(role='admin')

        _now = now(tz=timezone.utc).replace(microsecond=0)
        beginner = await dataset.courier(cluster=cluster, tags=[TAG_BEGINNER])
        beginner_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=beginner,
            status='waiting',
            tags=[TAG_BEGINNER],
        )

        mentor = await dataset.courier(cluster=cluster)
        mentor_shift = await dataset.courier_shift(
            cluster=cluster,
            courier=mentor,
            status='processing',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': beginner_shift.courier_shift_id,
                'mentor_shift_id': mentor_shift.courier_shift_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        with await beginner_shift.reload() as shift:
            tap.eq(shift.mentor_shift_id, None, 'наставник не назначен')


async def test_courier_tags_err(tap, api, dataset):
    with tap.plan(5, 'Целенаправленное изменение courier_tags запрещено'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        tag_1 = (await dataset.courier_shift_tag(type='courier')).title
        tag_2 = (await dataset.courier_shift_tag(type='courier')).title
        courier = await dataset.courier(cluster=cluster, tags=[tag_1])

        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier,
            courier_tags=[tag_1],
        )

        user = await dataset.user(store=store, role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_save',
            json={
                'courier_shift_id': shift.courier_shift_id,
                'courier_id': courier.courier_id,
                # пропихиваем за счет additionalProperty=True
                'courier_tags': [tag_2],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await shift.reload():
            tap.eq(shift.courier_id, courier.courier_id, 'курьер #2')
            tap.eq(shift.courier_tags, [tag_1], 'теги курьера остались те же')
