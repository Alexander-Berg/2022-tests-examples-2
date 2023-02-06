# pylint: disable=too-many-locals,too-many-arguments
# pylint: disable=redefined-outer-name,too-many-lines
from datetime import timedelta
from pathlib import Path

import pytest


@pytest.fixture
def get_csv_template(load_file):
    def _wrapper(count: int = 2) -> str:
        filepath = 'test_import_shifts/norm.csv'
        return '\n'.join(load_file(filepath).strip().split('\n')[:count + 1])
    return _wrapper


@pytest.mark.parametrize('filepath', [
    str(f) for f in Path(__file__).parent.glob('test_import_shifts/*.csv')
])
async def test_simple(
        tap, api, dataset, job, load_file, now,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
        filepath,
):
    with tap.plan(7, f'Проверка файла-редактирования: {filepath}'):
        csv = load_file(filepath)
        count = len([i for i in csv.split('\n') if i.strip()]) - 1

        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        store2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )

        shifts = [
            await dataset.courier_shift(
                cluster=cluster,
                store=store1,
                started_at=_now + timedelta(hours=10),
                closes_at=_now + timedelta(hours=11),
                schedule=[{"tags": [], "time": _now + timedelta(hours=1)}],
            ) for _ in range(count)
        ]
        tap.ok(len(shifts), f'Создано {len(shifts)} смен для проверки')

        csv = replace_csv_data(
            csv,
            ('courier_shift_id', [shift.courier_shift_id for shift in shifts]),
            ('depot_id', store2.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', f'{tag1.title},{tag2.title}'),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with tap.subtest(9 * len(shifts), 'Проверяем смены') as _tap:
            for shift in shifts:
                _tap.note(f'Смена {shift.courier_shift_id}')
                with await shift.reload() as shift:
                    _tap.eq(shift.store_id, store2.store_id, 'store_id')
                    _tap.eq(shift.cluster_id, cluster.cluster_id, 'cluster_id')
                    _tap.eq(shift.courier_id, None, 'courier_id')
                    _tap.eq(shift.started_at, started_at, 'started_at')
                    _tap.eq(shift.closes_at, closes_at, 'closes_at')
                    _tap.eq(shift.delivery_type, 'foot', 'delivery_type')
                    _tap.eq(shift.status, 'request', 'status')
                    _tap.eq(sorted(shift.tags),
                            sorted([tag1.title, tag2.title]),
                            'tags')
                    _tap.eq(shift.vars.get('public', False), False,
                            'public attr')


async def test_set_courier(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(11, 'Проверка назначения курьеров'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        store2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
            tags=[tag1.title, tag2.title],
        )

        # свободная
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            tags=[tag1.title, tag2.title],
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', shift.courier_shift_id),
            ('depot_id', store2.external_id),
            ('courier_id', courier.eda_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', f'{tag1.title},{tag2.title}'),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload() as shift:
            tap.eq(shift.cluster_id, cluster.cluster_id, 'cluster_id')
            tap.eq(shift.store_id, store2.store_id, 'store_id')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(shift.delivery_type, 'foot', 'delivery_type')
            tap.eq(shift.status, 'waiting', 'status')
            tap.eq(sorted(shift.tags),
                   sorted([tag1.title, tag2.title]),
                   'tags')


async def test_replace_courier(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(11, 'Проверка переназначения курьеров'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        store2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
            tags=[tag1.title, tag2.title],
        )

        # занята другим курьером
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='waiting',
            tags=[tag1.title, tag2.title],
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', shift.courier_shift_id),
            ('depot_id', store2.external_id),
            ('courier_id', courier.eda_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', f'{tag1.title},{tag2.title}'),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload() as shift:
            tap.eq(shift.cluster_id, cluster.cluster_id, 'cluster_id')
            tap.eq(shift.store_id, store2.store_id, 'store_id')
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(shift.delivery_type, 'foot', 'delivery_type')
            tap.eq(shift.status, 'waiting', 'status')
            tap.eq(sorted(shift.tags),
                   sorted([tag1.title, tag2.title]),
                   'tags')


async def test_free_courier(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(7, 'Освобождение курьеров со смены'):
        count = 2
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        store2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )

        shifts = [
            await dataset.courier_shift(
                cluster=cluster,
                store=store1,
                status='waiting',
                started_at=_now + timedelta(hours=10),
                closes_at=_now + timedelta(hours=11),
                schedule=[{"tags": [], "time": _now + timedelta(hours=1)}],
            ) for _ in range(count)
        ]
        tap.ok(len(shifts), f'Создано {len(shifts)} смен для проверки')

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', [shift.courier_shift_id for shift in shifts]),
            ('depot_id', store2.external_id),

            # Снимаем курьеров
            ('courier_id', ''),

            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', f'{tag1.title},{tag2.title}'),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with tap.subtest(2 * len(shifts), 'Проверяем смены') as _tap:
            for shift in shifts:
                _tap.note(f'Смена {shift.courier_shift_id}')
                with await shift.reload() as shift:
                    _tap.eq(shift.courier_id, None, 'courier_id')
                    _tap.eq(shift.status, 'request', 'status')


async def test_status_cancel_error(
        tap, api, dataset, job, now, get_csv_template,
        tzone, unique_int, time2iso, replace_csv_data,
):
    with tap.plan(5, 'Попытка отменить смену без прав на это'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier_shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(hours=10),
            closes_at=_now + timedelta(hours=11),
            status='request',
        )

        csv = replace_csv_data(
            get_csv_template(count=1),
            ('courier_shift_id', courier_shift.courier_shift_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('depot_id', store.external_id),
            ('tags', ''),

            # отменяем
            ('status', 'cancelled'),
        )
        user = await dataset.user(store=store)
        with user.role as role:
            role.remove_permit('courier_shifts_cancel')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_import_shifts', json={
                    'csv': csv
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

            with await courier_shift.reload() as shift:
                tap.eq(shift.status, 'request', 'смена не отменилась')


async def test_status_cancel(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(9, 'Проверка отмена смен'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
            tags=[tag.title],
        )

        # свободная
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='request',
            tags=[tag.title],
        )
        # занята курьером
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='waiting',       # курьер создастся автоматически
            tags=[tag.title],
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', [
                shift_1.courier_shift_id,
                shift_2.courier_shift_id
            ]),
            ('depot_id', store.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', tag.title),

            # назначение курьера
            ('courier_id', [
                # смена остается свободной
                '',
                # переназначением курьера
                courier.eda_id
            ]),

            # попытка изменения статуса смены
            ('status', [
                # провальная попытка изменить статус. Можно только отменять.
                # Поэтому статус останется request.
                'template',
                # отмена смены, на которой поменяется курьер.
                'cancelled'
            ])
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shifts = [shift_1, shift_2]
        with tap.subtest(2 * len(shifts), 'Проверяем смены') as _tap:
            for shift in shifts:
                _tap.note(f'Смена {shift.courier_shift_id}')
                with await shift.reload() as shift:
                    _tap.eq(shift.cluster_id, cluster.cluster_id, 'cluster_id')
                    _tap.eq(shift.delivery_type, 'foot', 'delivery_type')

        # свободная смена осталась нетронутой и ее статус не стал template
        tap.eq(shift_1.status, 'request', 'смена назначена')
        # курьер назначен, но смена отменена, т.к. отмена смен имеет приоритет
        tap.eq(shift_2.status, 'cancelled', 'смена отменилась')
        tap.eq(shift_2.courier_id, courier.courier_id, 'курьер назначен')


async def test_set_tags(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(7, 'Проверка редактирования тегов'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag3 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        store2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            tags=[],
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='request',
            tags=[tag2.title],
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', [
                shift_1.courier_shift_id,
                shift_2.courier_shift_id
            ]),
            ('depot_id', store2.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', [
                f'{tag1.title},{tag2.title}',
                f'{tag2.title},{tag3.title}'
            ]),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(sorted(shift.tags),
                   sorted([tag1.title, tag2.title]),
                   'tags первой смены')

        with await shift_2.reload() as shift:
            tap.eq(sorted(shift.tags),
                   sorted([tag2.title, tag3.title]),
                   'tags второй смены')


async def test_system_tags(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, uuid, unique_int, replace_csv_data,
):
    with tap.plan(9, 'Проверка редактирования системных тегов'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        tag_1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag_2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag_sys = await dataset.courier_shift_tag(title=f'tag-system-{uuid()}',
                                                  group='system')

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )

        shift_1 = await dataset.courier_shift(
            store=store,
            status='request',
            tags=[tag_1.title],                   # системного тега не было
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            status='request',
            tags=[tag_sys.title],                 # был только системный тег
        )
        shift_3 = await dataset.courier_shift(
            store=store,
            status='request',
            tags=[tag_sys.title, tag_1.title],    # был системный и простой
        )
        shift_4 = await dataset.courier_shift(
            store=store,
            status='request',
            tags=[tag_sys.title, tag_1.title],    # был системный и простой
        )

        csv = replace_csv_data(
            get_csv_template(count=4),
            ('courier_shift_id', [
                shift_1.courier_shift_id,
                shift_2.courier_shift_id,
                shift_3.courier_shift_id,
                shift_4.courier_shift_id,
            ]),
            ('depot_id', store.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', [
                f'{tag_1.title},{tag_sys.title}',   # попытка выдать системный
                f'{tag_1.title}',                   # а тут попытка подменить
                f'{tag_sys.title},{tag_2.title}',   # выдаем выданный + замена
                '',                                 # пробуем все снять
            ]),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.tags, [tag_1.title], 'системный тег не назначен')

        with await shift_2.reload() as shift:
            tap.eq(sorted(shift.tags),
                   sorted([tag_1.title, tag_sys.title]),
                   'системный тег остался на месте и добавился новый')

        with await shift_3.reload() as shift:
            tap.eq(sorted(shift.tags),
                   sorted([tag_sys.title, tag_2.title]),
                   'системный тег остался на месте, а второй заменился новый')

        with await shift_4.reload() as shift:
            tap.eq(shift.tags,
                   [tag_sys.title],
                   'системный тег на месте, а обычный снят')


@pytest.mark.parametrize('init,fixes,er_code,er_value,er_message', [
    (  # Ошибка получения смены
        {'status': 'request'},
        {'courier_shift_id': 'unknown'},
        'ER_NOT_FOUND', None, 'Courier shift not found',
    ),
    (  # Ошибка в pre_check: попытка отредактировать завершенную смену
        {'status': 'complete'},
        {'status': 'request'},
        'ER_GONE', 'complete', 'Courier shift in incorrect status for editing'
    ),
    (  # Ошибка в pre_check: попытка задать время начала смены в прошлом
        {'status': 'request'},
        {'started_at': '2021-01-01'},
        'ER_BAD_REQUEST',
        {'started_at': '2021-01-01T00:00:00+00:00'},
        'Courier shift started in past'
    ),
    (  # Ошибка в проверке параметра
        {'status': 'request'},
        {'tags': 'unknown'},
        'ER_NOT_FOUND', ['unknown'], 'Tag not found',
    ),
])
async def test_job_errors(
        tap, api, dataset, job, now, get_csv_template,
        tzone, unique_int, time2iso, replace_csv_data,
        init, fixes, er_code, er_value, er_message,
):
    with tap.plan(12, 'Ошибки при массовом редактировании смен'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier_shift = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            started_at=_now + timedelta(hours=10),
            closes_at=_now + timedelta(hours=11),
            **init,
        )

        csv = replace_csv_data(
            get_csv_template(count=1),
            ('courier_shift_id', courier_shift.courier_shift_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('depot_id', store.external_id),
            ('tags', ''),

            # Здесь пишем ошибочные поля
            *fixes.items()
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('errors', r'^error:\w+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        errors_group = t.res['json']['errors']

        with await courier_shift.reload() as shift:
            for column, value in fixes.items():
                tap.ne(getattr(shift, column), value, f'{column} не изменилось')

        errors = (await dataset.Stash.list(
            by='full',
            conditions=[('group', errors_group)],
            sorted='name',
        )).list

        tap.eq(len(errors), 1, 'Ошибки получены')
        tap.eq(errors[0].value['code'], er_code, 'код ошибки совпадает')
        tap.eq(errors[0].value['value'], er_value, f'value={er_value}')
        tap.eq(errors[0].value['message'], er_message, f'message={er_message}')
        tap.ok(errors[0].value['line'], 'line')


async def test_set_courier_fail_exceeding(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, unique_int, replace_csv_data,
):
    with tap.plan(15, 'Не даем назначать курьера если не прошел проверку'):
        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone('Europe/Moscow')) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster(
            tz='Europe/Moscow',
            courier_shift_setup={
                # Проверяем что смены не вылезут за 2 часа в день
                'max_day_hours': 2,
                'max_week_hours': 24 * 7,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            tz='Europe/Moscow',
            external_id=str(unique_int()),
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
        )

        # свободная, на больше часов чем разрешено
        shift1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='request',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=15),
        )
        # занята другим курьером, на больше часов чем разрешено
        shift2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=15),
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', [
                shift1.courier_shift_id,
                shift2.courier_shift_id
            ]),
            ('depot_id', store.external_id),
            ('courier_id', courier.eda_id),
            ('started_at', time2iso(day.replace(hour=12))),
            ('closes_at', time2iso(day.replace(hour=15))),
            ('tags', ''),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('errors', r'^error:\w+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        errors_group = t.res['json']['errors']

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'courier_id')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'request')
            tap.ne(shift.courier_id, courier.courier_id, 'courier_id')

        errors = (await dataset.Stash.list(
            by='full',
            conditions=[('group', errors_group)],
            sorted='name',
        )).list
        tap.eq(len(errors), 2, 'Ошибки получены')

        errors.sort(key=lambda x: x.value['line'])
        with errors[0] as error:
            tap.eq(
                error.value['code'],
                'ER_EXCEEDING_DURATION',
                'ER_EXCEEDING_DURATION'
            )
            tap.eq(error.value['line'], 1, 'line')
        with errors[1] as error:
            tap.eq(
                error.value['code'],
                'ER_EXCEEDING_DURATION',
                'ER_EXCEEDING_DURATION'
            )
            tap.eq(error.value['line'], 2, 'line')


async def test_fail_intersection(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, unique_int, replace_csv_data,
):
    with tap.plan(15, 'Не даем назначать курьера если смены пересекаются'):
        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone('Europe/Moscow')) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        cluster = await dataset.cluster(tz='Europe/Moscow')
        store = await dataset.store(
            cluster=cluster,
            tz='Europe/Moscow',
            external_id=str(unique_int()),
        )
        user = await dataset.user(store=store, role='admin')
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
        )

        await dataset.courier_shift(
            cluster=cluster,
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=11),
            closes_at=day.replace(hour=13),
        )

        # свободная, на больше часов чем разрешено
        shift1 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='request',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=14),
        )
        # занята другим курьером, на больше часов чем разрешено
        shift2 = await dataset.courier_shift(
            cluster=cluster,
            store=store,
            status='waiting',
            started_at=day.replace(hour=12),
            closes_at=day.replace(hour=14),
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', [
                shift1.courier_shift_id,
                shift2.courier_shift_id
            ]),
            ('depot_id', store.external_id),
            ('courier_id', courier.eda_id),
            ('started_at', time2iso(day.replace(hour=12))),
            ('closes_at', time2iso(day.replace(hour=15))),
            ('tags', ''),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('errors', r'^error:\w+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        errors_group = t.res['json']['errors']

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'request', 'request')
            tap.eq(shift.courier_id, None, 'courier_id')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'request')
            tap.ne(shift.courier_id, courier.courier_id, 'courier_id')

        errors = (await dataset.Stash.list(
            by='full',
            conditions=[('group', errors_group)],
            sorted='name',
        )).list
        tap.eq(len(errors), 2, 'Ошибки получены')

        errors.sort(key=lambda x: x.value['line'])
        with errors[0] as error:
            tap.eq(
                error.value['code'],
                'ER_INTERSECTION',
                'ER_INTERSECTION'
            )
            tap.eq(error.value['line'], 1, 'line')
        with errors[1] as error:
            tap.eq(
                error.value['code'],
                'ER_INTERSECTION',
                'ER_INTERSECTION'
            )
            tap.eq(error.value['line'], 2, 'line')


async def test_set_public_attr(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, unique_int, replace_csv_data,
):
    with tap.plan(8, 'Проверка смены параметра public'):
        count = 3
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        shifts = [
            await dataset.courier_shift(
                cluster=cluster,
                store=store,
                started_at=_now + timedelta(hours=10),
                closes_at=_now + timedelta(hours=11),
                schedule=[{"tags": [], "time": _now + timedelta(hours=1)}],
            ) for _ in range(count)
        ]

        csv = replace_csv_data(
            get_csv_template(count=count),
            ('courier_shift_id', [it.courier_shift_id for it in shifts]),
            ('depot_id', store.external_id),
            ('public', ['1', '0', '']),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', ''),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        await shifts[0].reload()
        tap.is_ok(shifts[0].attr.get('public', False), True,
                  'параметр выставлен в True')

        await shifts[1].reload()
        tap.is_ok(shifts[1].attr.get('public', False), False,
                  'параметр выставлен в False')

        await shifts[2].reload()
        tap.is_ok(shifts[1].attr.get('public', None), False,
                  'параметр выставлен в False')


@pytest.mark.parametrize('col_name,col_value', [
    ['courier_shift_id', ''],
    ['delivery_type', ''],
    ['delivery_type', 'abcdefg1234'],
    ['status', ''],
    ['started_at', ''],
    ['started_at', 'abcdefg1234'],
    ['closes_at', ''],
    ['closes_at', 'abcdefg1234'],
    ['guarantee', '-1'],
    ['guarantee', 'abcdefg1234'],
    ['status', 'abcdefg1234'],
])
async def test_csv_validator_bad(
        tap, api, dataset, replace_csv_data, time2iso, now,
        tzone, get_csv_template, col_name, col_value
):
    with tap.plan(5, f'Проверка ошибки "{col_name}={col_value}"'):
        count = 2
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)
        courier_shift = await dataset.courier_shift(store=store)
        tags = [await dataset.courier_shift_tag(title=t) for t in ('t1', 't2')]
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        # назначаем существующий courier_shift_id
        csv = replace_csv_data(
            get_csv_template(count=count),
            ('courier_shift_id', courier_shift.courier_shift_id),
            ('depot_id', store.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', ','.join(t.title for t in tags)),

            # повреждаем нужный столбец
            (col_name, col_value)
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts',
            json={'csv': csv},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_FILE_PARSE', 'код')
        t.json_has('details.list', 'ошибки в строках')

        invalid_rows = t.res['json']['details']['list']
        tap.eq(len(invalid_rows), count, 'кол-во строк с ошибками')


@pytest.mark.parametrize('col_name,col_value', [
    ['tags', ''],           # убрать все теги
    ['tags', '  '],
    ['guarantee', ''],      # убрать гарантированную плату
    ['guarantee', ' '],
])
async def test_csv_validator_good(
        tap, api, dataset, job, time2iso, now, tzone, unique_int,
        replace_csv_data, get_csv_template, col_name, col_value
):
    with tap.plan(6, f'Проверка отсутствия ошибки "{col_name}={col_value}"'):
        count = 2
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster,
                                    external_id=str(unique_int()))
        user = await dataset.user(store=store)
        courier_shifts = [
            await dataset.courier_shift(store=store) for _ in range(count)
        ]
        tags = [await dataset.courier_shift_tag(title=t) for t in ('t1', 't2')]
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        # назначаем существующий courier_shift_id, теги и др.
        csv = replace_csv_data(
            get_csv_template(count=count),
            ('courier_shift_id', [c.courier_shift_id for c in courier_shifts]),
            ('depot_id', store.external_id),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', ','.join(t.title for t in tags)),

            # модифицируем нужный столбец
            (col_name, col_value),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        errors_group = t.res['json']['errors']
        errors = (await dataset.Stash.list(
            by='full',
            conditions=[('group', errors_group)],
            sorted='name',
        )).list
        tap.eq(len(errors), 0, 'Ошибок нет')


@pytest.mark.parametrize(
    'out_of_store,out_of_company,imported_shifts',
    (
        (False, False, 1),  # только своя лавка
        (True, False, 2),   # все лавки внутри своей компании
        (True, True, 3),    # все лавки всех компаний
    )
)
async def test_prohibit_alien_stores(
        tap, api, dataset, job, now, tzone, unique_int, time2iso,
        replace_csv_data, get_csv_template,
        out_of_store, out_of_company, imported_shifts
):
    with tap.plan(5, 'Проверка прав на изменение смен чужих лавок/компании'):
        tags = [await dataset.courier_shift_tag(title=t) for t in
                ('t1', 't2')]

        # своя лавка, своя компания
        company1 = await dataset.company()
        store1 = await dataset.store(company=company1,
                                     external_id=str(unique_int()))
        shift1 = await dataset.courier_shift(store=store1, guarantee=None)

        # чужая лавка, своя компания
        store2 = await dataset.store(company=company1,
                                     external_id=str(unique_int()))
        shift2 = await dataset.courier_shift(store=store2, guarantee=0)

        # чужая лавка, чужая компания
        store3 = await dataset.store(external_id=str(unique_int()))
        shift3 = await dataset.courier_shift(store=store3, guarantee=10)

        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)
        depot_ids = (store1.external_id, store2.external_id, store3.external_id)
        shift_ids = (shift1.courier_shift_id, shift2.courier_shift_id,
                     shift3.courier_shift_id)

        # назначаем существующий courier_shift_id, теги и др.
        csv = replace_csv_data(
            get_csv_template(count=3),
            ('courier_shift_id', shift_ids),
            ('depot_id', depot_ids),
            ('started_at', time2iso(started_at)),
            ('closes_at', time2iso(closes_at)),
            ('tags', ','.join(t.title for t in tags)),

            # признак, что смену отредактировали
            ('guarantee', '123'),
        )

        user = await dataset.user(store=store1, role='admin')
        with user.role as role:
            role.add_permit('out_of_store', out_of_store)
            role.add_permit('out_of_company', out_of_company)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_import_shifts',
                json={'csv': csv},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')

        cursor = await dataset.CourierShift.list(
            by='full',
            conditions=('courier_shift_id', shift_ids)
        )

        tap.eq(
            sorted(
                [x.courier_shift_id for x in cursor.list if x.guarantee == 123]
            ),
            sorted(shift_ids[:imported_shifts]),
            'отредактированы смены, только из доступных лавок'
        )


async def test_change_timezone(
        tap, api, dataset, job, now, get_csv_template,
        time2iso, tzone, unique_int, replace_csv_data,
):
    with tap.plan(7, 'Проверка предложения изменений при изменении tz'):
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)

        cluster = await dataset.cluster()
        store1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
        )
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': unique_int(),
                },
            },
        )
        shift = await dataset.courier_shift(
            cluster=cluster,
            store=store1,
            status='waiting',
            courier_id=courier.courier_id,
            started_at=started_at,
            closes_at=closes_at,
        )

        csv = replace_csv_data(
            get_csv_template(),
            ('courier_shift_id', shift.courier_shift_id),
            ('depot_id', store1.external_id),
            ('courier_id', courier.eda_id),
            ('started_at', time2iso(started_at, tz=0)),
            ('closes_at', time2iso(closes_at, tz=3)),
            ('tags', ''),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'courier_id')
            tap.eq(shift.shift_events, [], 'Изменения не предложены')


async def test_counters_planned(
        tap, api, dataset, job, now, time2iso_utc, replace_csv_data, unique_int,
        tzone, time2iso, get_csv_template,
):
    with tap.plan(19, 'Изменение счетчиков длительности смен'):
        count = 4
        _now = now(tz=tzone('Europe/Moscow')).replace(hour=0, microsecond=0)

        # параметры 4-ч часовой смены
        duration = 4 * 3600
        started_at = _now + timedelta(days=1, hours=1)
        closes_at = _now + timedelta(days=1, hours=1 + duration // 3600)
        str_date = time2iso_utc(started_at.date())

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': duration * count,
                        'extra_sec': 0,   # смены только создали и еще не меняли
                    }
                }
            }
        )
        # все смены по 4 часа
        shifts = [
            await dataset.courier_shift(
                store=store,
                status='request',
                started_at=started_at,
                closes_at=closes_at,
                placement='planned',
            ) for _ in range(count)
        ]

        csv = replace_csv_data(
            get_csv_template(count=count),
            ('courier_shift_id', [s.courier_shift_id for s in shifts]),
            ('depot_id', store.external_id),
            ('courier_id', ''),
            ('started_at', [
                time2iso(started_at - timedelta(hours=1)),  # раньше на час
                time2iso(started_at),                       # не изменилось
                time2iso(started_at + timedelta(hours=1)),  # позже на час
                time2iso(started_at + timedelta(days=1)),   # позже на 1 сутки
            ]),
            ('closes_at', [
                time2iso(closes_at),                        # не изменилось
                time2iso(closes_at - timedelta(hours=2)),   # раньше на 2 часа
                time2iso(closes_at + timedelta(hours=1)),   # позже на час
                time2iso(closes_at + timedelta(days=1)),    # позже на 1 сутки
            ]),
            ('tags', ''),
        )
        # +1h, -2h, 0h

        user = await dataset.user(store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # +1 час
        with await shifts[0].reload() as shift:
            tap.eq(shift.duration, duration + 3600, 'duration #0')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #0 is None')

        # -2 часа
        with await shifts[1].reload() as shift:
            tap.eq(shift.duration, duration - 7200, 'duration #1')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #1 is None')

        # без изменений
        with await shifts[2].reload() as shift:
            tap.eq(shift.duration, duration, 'duration #2')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #2 is None')
            tap.eq(shift.started_at, started_at + timedelta(hours=1), 'начало')
            tap.eq(shift.closes_at, closes_at + timedelta(hours=1), 'конец')

        # без изменений, но теперь на другой дате
        with await shifts[3].reload() as shift:
            tap.eq(shift.duration, duration, 'duration #3')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #3 is None')
            tap.eq(shift.started_at, started_at + timedelta(days=1), 'начало')
            tap.eq(shift.closes_at, closes_at + timedelta(days=1), 'конец')

        with await store.reload() as store:
            tap.eq(
                store.vars['courier_shift_counters'][str_date]['planned_sec'],
                sum(s.duration for s in shifts[:3]),
                'кол-во плановых секунд совпадает'
            )
            date2 = time2iso_utc((started_at + timedelta(days=1)).date())
            tap.eq(
                store.vars['courier_shift_counters'][str(date2)]['planned_sec'],
                shifts[3].duration,
                'перенесено на другую дату'
            )


async def test_counters_planned_extra(
        tap, api, dataset, job, now, time2iso_utc, replace_csv_data, unique_int,
        tzone, time2iso, get_csv_template,
):
    with tap.plan(14, 'Счетчики не работают для planned_extra смен'):
        _count = 3
        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        _duration = 4 * 3600   # 4 часа
        started_at = _now + timedelta(days=1, hours=1)
        closes_at = _now + timedelta(days=1, hours=1 + _duration // 3600)
        str_date = time2iso_utc(started_at.date())

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
            vars={
                'courier_shift_counters': {
                    str_date: {
                        'planned_sec': 0,
                        'extra_sec': 0,
                    }
                }
            }
        )
        # все смены по 4 часа
        shifts = [
            await dataset.courier_shift(
                store=store,
                status='request',
                started_at=started_at,
                closes_at=closes_at,
                placement='planned-extra',
            ) for _ in range(_count)
        ]

        csv = replace_csv_data(
            get_csv_template(count=_count),
            ('courier_shift_id', [s.courier_shift_id for s in shifts]),
            ('depot_id', store.external_id),
            ('courier_id', ''),
            ('started_at', [
                time2iso(started_at - timedelta(hours=1)),  # раньше на час
                time2iso(started_at),                       # не изменилось
                time2iso(started_at + timedelta(hours=1)),  # позже на час
            ]),
            ('closes_at', [
                time2iso(closes_at),                        # не изменилось
                time2iso(closes_at - timedelta(hours=2)),   # раньше на 2 часа
                time2iso(closes_at + timedelta(hours=1)),   # позже на час
            ]),
            ('tags', ''),
        )

        user = await dataset.user(store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shifts[0].reload() as shift:
            tap.eq(shift.duration, _duration + 3600, 'duration #0')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #0 is None')

        with await shifts[1].reload() as shift:
            tap.eq(shift.duration, _duration - 7200, 'duration #1')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #1 is None')

        with await shifts[2].reload() as shift:
            tap.eq(shift.duration, _duration, 'duration #2')
            tap.eq(shift.vars.get('extra_sec'), None, 'extra_sec #2 is None')
            tap.eq(shift.started_at, started_at + timedelta(hours=1), 'начало')
            tap.eq(shift.closes_at, closes_at + timedelta(hours=1), 'конец')

        old_sec = store.vars['courier_shift_counters'][str_date]['planned_sec']
        with await store.reload() as store:
            tap.eq(
                store.vars['courier_shift_counters'][str_date]['planned_sec'],
                old_sec,
                'кол-во не изменилось'
            )


async def test_counters_planned_repeat(
        tap, api, dataset, job, now, time2iso_utc, replace_csv_data, unique_int,
        tzone, time2iso, get_csv_template,
):
    with tap.plan(21, 'Повторное изменение счетчиков длительности смен'):
        count = 4
        _now = now(tz=tzone('Europe/Moscow')).replace(hour=0, microsecond=0)

        # параметры 4-ч часовой смены
        default = 1800
        duration = 4 * 3600
        started_at = _now + timedelta(days=1, hours=1)
        closes_at = _now + timedelta(days=1, hours=1 + duration // 3600)
        date_1 = time2iso_utc(started_at.date())

        cluster = await dataset.cluster()
        store = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster,
            external_id=str(unique_int()),
            vars={
                'courier_shift_counters': {
                    date_1: {
                        'planned_sec': duration * count,
                        'extra_sec': default * count,  # каждая увеличена
                    }
                }
            }
        )
        # все смены по 4 часа
        shifts = [
            await dataset.courier_shift(
                store=store,
                status='request',
                started_at=started_at,
                closes_at=closes_at,
                placement='planned',
                vars={
                    'extra_sec': default,  # X минут уже докинули
                }
            ) for _ in range(count)
        ]

        csv = replace_csv_data(
            get_csv_template(count=count),
            ('courier_shift_id', [s.courier_shift_id for s in shifts]),
            ('depot_id', store.external_id),
            ('courier_id', ''),
            ('started_at', [
                time2iso(started_at - timedelta(hours=1)),  # раньше на час
                time2iso(started_at),                       # не изменилось
                time2iso(started_at + timedelta(hours=1)),  # позже на час
                time2iso(started_at + timedelta(days=1)),   # позже на 1 сутки
            ]),
            ('closes_at', [
                time2iso(closes_at),                        # не изменилось
                time2iso(closes_at - timedelta(hours=2)),   # раньше на 2 часа
                time2iso(closes_at + timedelta(hours=1)),   # позже на час
                time2iso(closes_at + timedelta(days=1)),    # позже на 1 сутки
            ]),
            ('tags', ''),
        )
        # +1h, -2h, 0h

        user = await dataset.user(store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # +1 час
        _extra_sec_0 = 3600
        with await shifts[0].reload() as shift:
            tap.eq(shift.duration, duration + _extra_sec_0, 'duration #0')
            tap.eq(shift.vars['extra_sec'], default, 'extra_sec #0 (default)')

        # -2 часа
        _extra_sec_1 = -7200
        with await shifts[1].reload() as shift:
            tap.eq(shift.duration, duration + _extra_sec_1, 'duration #1')
            tap.eq(shift.vars['extra_sec'], default, 'extra_sec #1 (default)')

        # без изменений
        _extra_sec_2 = 0
        with await shifts[2].reload() as shift:
            tap.eq(shift.duration, duration + _extra_sec_2, 'duration #2')
            tap.eq(shift.vars['extra_sec'], default, 'extra_sec #2 (default)')
            tap.eq(shift.started_at, started_at + timedelta(hours=1), 'начало')
            tap.eq(shift.closes_at, closes_at + timedelta(hours=1), 'конец')

        # без изменений, но теперь на другой дате
        _extra_sec_3 = 0
        with await shifts[3].reload() as shift:
            tap.eq(shift.duration, duration + _extra_sec_3, 'duration #3')
            tap.eq(shift.vars['extra_sec'], default, 'extra_sec #3 (default)')
            tap.eq(shift.started_at, started_at + timedelta(days=1), 'начало')
            tap.eq(shift.closes_at, closes_at + timedelta(days=1), 'конец')

        with await store.reload() as store:
            tap.eq(
                store.vars['courier_shift_counters'][date_1]['planned_sec'],
                sum(s.duration for s in shifts[:3]),
                'кол-во плановых секунд совпадает'
            )
            tap.eq(
                store.vars['courier_shift_counters'][date_1]['extra_sec'],
                default * count - shifts[3].vars['extra_sec'],
                'кол-во доп. секунд стало меньше из-за последне смены'
            )

            date_2 = str(time2iso_utc((started_at + timedelta(days=1)).date()))
            tap.eq(
                store.vars['courier_shift_counters'][date_2]['planned_sec'],
                shifts[3].duration,
                'planned_sec перенесено на другую дату'
            )
            tap.eq(
                store.vars['courier_shift_counters'][date_2]['extra_sec'],
                shifts[3].vars['extra_sec'],
                'extra_sec перенесено на другую дату'
            )


async def test_save_permit_revoked(
        tap, api, dataset, job, time2iso, tzone, unique_int, replace_csv_data,
        now, get_csv_template,
):
    with tap.plan(11, 'Редактирование не выполняется, если пермит отключен'
                      'в настройках кластера'):
        _now = now(tz=tzone('Europe/Moscow')).replace(hour=0, microsecond=0)
        started_at = _now + timedelta(days=1, hours=1)
        closes_at = _now + timedelta(days=1, hours=4)

        # ограничений нет
        cluster_1 = await dataset.cluster()
        store_1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster_1,
            external_id=str(unique_int()),
        )
        shift_1 = await dataset.courier_shift(
            cluster=cluster_1,
            store=store_1,
            status='request',
            started_at=started_at,
            closes_at=closes_at,
        )

        # у админа отключена возможность редактирования
        cluster_2 = await dataset.cluster(disabled_role_permits={
            'admin': ['courier_shifts_save']
        })
        store_2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster_2,
            external_id=str(unique_int()),
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster_2,
            store=store_2,
            status='request',
            started_at=started_at,
            closes_at=closes_at,
        )

        csv = replace_csv_data(
            get_csv_template(count=2),
            ('courier_shift_id', [
                shift_1.courier_shift_id, shift_2.courier_shift_id,
            ]),
            ('depot_id', [store_1.external_id, store_2.external_id]),
            # увеличиваем на 1ч обе
            ('started_at', time2iso(started_at + timedelta(hours=1))),
            ('closes_at', time2iso(closes_at + timedelta(hours=1))),
            ('tags', ''),
        )

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_shifts', json={
                'csv': csv
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload():
            tap.eq(shift_1.cluster_id, cluster_1.cluster_id, 'cluster_id')
            tap.eq(shift_1.store_id, store_1.store_id, 'store_id')
            tap.eq(
                shift_1.closes_at,
                closes_at + timedelta(hours=1),
                'редактирование прошло, закроется на 1 час позже'
            )

        with await shift_2.reload():
            tap.eq(shift_2.cluster_id, cluster_2.cluster_id, 'cluster_id')
            tap.eq(shift_2.store_id, store_2.store_id, 'store_id')
            tap.eq(shift_2.closes_at, closes_at, 'осталась без изменений')
