# pylint: disable=too-many-locals,too-many-arguments,too-many-lines

from collections import Counter, defaultdict
from datetime import timedelta, time, datetime
from functools import partial
from pathlib import Path

from easytap.pytest_plugin import PytestTap
import pytest

from libstall.util import time2time, tzone
from stall import lp
from stall.model.courier_shift import CourierShift, CourierShiftSchedule
from stall.model.stash import Stash
from stall.script import csv2dicts, parse_float


# NOTE: заголовок "number of couriers" переименован в "number_of_couriers".
# т.к. он именно так парсится в import_data и передается в job_import_data
VALID_CSV = (
    "region_id;region_name;depot_id;area_name;date;weekday;start;"
    "duration;number_of_couriers;auto;guarantee;public"
    "\n"
    "1;Москва;7010;Лавка-Кооперативная;11.01.2021;1;8;4;4;пеший;;\n"
    "1;Москва;7010;Лавка-Кооперативная;11.01.2021;1;9;4;7;пеший;;\n"
    "1;Москва;7010;Лавка-Кооперативная;11.01.2021;1;14;4;1;пеший;;"
)


def _convert_time(row, store):
    start = parse_float(row.get('start', '0'))
    h, m = int(start), int(60 * (start % 1))

    return datetime.combine(
        time2time(row.get('date')),
        time(hour=h, minute=m, second=0, microsecond=0, tzinfo=tzone(store.tz))
    )


@pytest.mark.parametrize('filepath', [
    str(f) for f in Path(__file__).parent.glob('test_import_data/*.csv')
])
async def test_files(
        tap, api, dataset, filepath, job, load_file, now, time2iso_utc,
        unique_int, replace_csv_data,
):
    with tap.plan(14, f'Проверка файла: {filepath}'):
        store = await dataset.store(external_id=str(unique_int()))
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            load_file(filepath),
            ('depot_id', store.external_id),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        rows = csv2dicts(csv, fieldnames=(
            'region_id',
            'region_name',
            'depot_id',
            'area_name',
            'date',
            'weekday',
            'start',
            'duration',
            'number_of_couriers',
            'auto',
            'guarantee',
        ))

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('import_id', r'^\S+$')

        import_id = t.res['json']['import_id']

        with await dataset.CourierShiftSchedule.load(import_id) as schedule:
            tap.ok(schedule, 'Пачка загружена')
            tap.eq(schedule.status, 'complete', 'status')
            tap.eq(schedule.user_id, user.user_id, 'user_id')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await schedule.reload():
            time_till = min(_convert_time(row, store) for row in rows)
            tap.eq(schedule.time_till, time_till, 'time_till верно')

            total = sum(int(row.get('number_of_couriers')) for row in rows)
            tap.eq(schedule.vars['total'], total, 'vars.total верно')

        shifts = await CourierShift.list(
            by='look',
            conditions=(
                ('store_id', store.store_id),
                ('source', 'batch'),
            )
        )
        tap.ok(shifts.list, 'Импортированы')
        tap.eq(
            sorted([int(r['number_of_couriers']) for r in rows]),
            sorted(Counter([shift.group_id for shift in shifts.list]).values()),
            'Создано ровно столько групп смен, сколько и ожидалось'
        )

        with tap.subtest(len(shifts.list) * 3, 'проверяем записи') as taps:
            for shift in shifts.list:
                taps.eq(
                    shift.import_id,
                    schedule.courier_shift_schedule_id,
                    'import_id'
                )
                taps.eq(
                    shift.placement,
                    'planned',
                    'placement'
                )
                taps.eq(shift.user_id, user.user_id, 'user_id')


async def test_min_attr(
        tap, dataset, api, replace_csv_data, job, now, time2iso_utc, unique_int,
):
    with tap.plan(11, 'Минимум атрибутов CSV'):
        csv = (
            "depot_id;date;start;duration ;  number of couriers;auto\n"
            "7010;11.01.2021;8;4;2;пеший\n"
            "7010;11.01.2021;8;4;2;пеший\n"
            "7010;11.01.2021;8;4;2;пеший\n"
        )

        stores = [
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
        ]

        csv = replace_csv_data(
            csv,
            ('depot_id', [it.external_id for it in stores]),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        for store in stores:
            shifts = (
                await CourierShift.list(
                    by='look',
                    conditions=(
                        ('store_id', store.store_id),
                        ('source', 'batch'),
                    )
                )
            ).list

            tap.ok(True, shifts)
            tap.eq(len(shifts), 2, f'2 смены на склад №{store.store_id}')


async def test_extra_attr(
        tap, dataset, api, replace_csv_data, job, now, time2iso_utc, unique_int,
):
    with tap.plan(11, 'Нарушенный порядок атрибутов CSV'):
        csv = (
            "depot_id;date;start;duration;  number_of_couriers  ;auto;public \n"
            "7010;11.01.2021;8;4;1;пеший;\n"
            "\n"
            "7010;11.01.2021;8;4;1;пеший;    \n"
            "7010;11.01.2021;8;4;1;пеший;\n\n\n\n\n"
        )

        stores = [
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
        ]

        public_attrs = ['', '1', '0']

        csv = replace_csv_data(
            csv,
            ('depot_id', [it.external_id for it in stores]),
            ('public ', public_attrs),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        for store, public_attr in zip(stores, public_attrs):
            public_attr = {'': False, '1': True, '0': False}[public_attr]

            shifts = (
                await CourierShift.list(
                    by='look',
                    conditions=(
                        ('store_id', store.store_id),
                        ('source', 'batch'),
                    )
                )
            ).list

            tap.eq(len(shifts), 1, f'1 смена на склад №{store.store_id}')
            with shifts[0] as shift:
                tap.eq(
                    shift.attr.get('public', False),
                    public_attr,
                    'public_attr'
                )


@pytest.mark.parametrize(
    'placement,counter_sec',
    [
        ('planned', 19 * 3600),     # в файле norm.csv 19 смен
        ('planned-extra', 0)        # такой replacement не считается
    ]
)
async def test_placement(
        tap, api, dataset, job, load_file, now, time2iso_utc,
        replace_csv_data, placement, counter_sec, unique_int,
):
    with tap.plan(8, 'Проверка файла'):
        str_date = time2iso_utc((now() + timedelta(days=1)).date())
        store = await dataset.store(
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
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            load_file('test_import_data/norm.csv'),
            ('depot_id', store.external_id),
            ('date', str_date),
            ('duration', '1'),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={
                'csv': csv,
                'placement': placement,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shifts = await CourierShift.list(
            by='look',
            conditions=(
                ('store_id', store.store_id),
                ('source', 'batch'),
            )
        )

        tap.ok(shifts.list, 'Импортированы')
        with tap.subtest(len(shifts.list) * 2, 'проверяем записи') as taps:
            for shift in shifts.list:
                taps.eq(shift.placement, placement, 'placement')
                taps.eq(shift.user_id, user.user_id, 'user_id')

        with await store.reload() as store:
            tap.eq(
                store.vars['courier_shift_counters'][str_date]['planned_sec'],
                counter_sec,
                'кол-во добавленных плановых секунд'
            )


async def test_double_planned_placement(
        tap, api, dataset, job, load_file, now, time2iso_utc, unique_int,
        replace_csv_data,
):
    with tap.plan(7, 'Проверка добавления и увеличения planned_sec'):
        str_date = time2iso_utc((now() + timedelta(days=1)).date())
        store = await dataset.store(external_id=str(unique_int()))
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            load_file('test_import_data/norm.csv'),
            ('depot_id', store.external_id),
            ('date', str_date),
            ('duration', '1'),      # чтобы легче считать
        )

        # это раз
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={
                'csv': csv,
                'placement': 'planned',
            },
        )
        t.status_is(200, diag=True)
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # это два
        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={
                'csv': csv,
                'placement': 'planned',
            },
        )
        t.status_is(200, diag=True)
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await store.reload() as store:
            tap.eq(
                store.vars['courier_shift_counters'][str_date]['planned_sec'],
                38 * 3600,
                'кол-во добавленных плановых секунд'
            )


async def test_public_attr(
        tap, dataset, api, replace_csv_data, job, now, time2iso_utc, unique_int,
):
    with tap.plan(11, 'Проверка публичного аттрибута'):
        csv = '\n'.join(VALID_CSV.split('\n')[:4])

        public_attrs = ['', '1', '0']
        stores = [
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
            await dataset.store(external_id=str(unique_int())),
        ]

        csv = replace_csv_data(
            csv,
            ('public', public_attrs),
            ('number_of_couriers', '1'),
            ('depot_id', [it.external_id for it in stores]),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        for store, public_attr in zip(stores, public_attrs):
            public_attr = {'': False, '1': True, '0': False}[public_attr]

            shifts = (await CourierShift.list(
                by='look',
                conditions=(
                    ('store_id', store.store_id),
                    ('source', 'batch'),
                )
            )).list
            tap.eq(len(shifts), 1, f'one shift for store #{store.store_id}')

            with shifts[0] as shift:
                tap.eq(shift.attr.get('public', False),
                       public_attr, 'public_attr ok')


async def test_csv_validator_bad_depot_id(
        tap, api, dataset, now, time2iso_utc, unique_int, replace_csv_data,
):
    with tap.plan(10, 'Проверка отсутствия depot_id/кластера'):
        depot_id_1 = str(unique_int())
        depot_id_2 = str(unique_int())
        depot_id_3 = str(unique_int())
        store = await dataset.store(external_id=depot_id_1,
                                    cluster='bad_cluster',
                                    cluster_id='100500')
        await dataset.store(external_id=depot_id_2, status='closed')
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', (
                depot_id_1,   # неизвестный кластер
                depot_id_2,   # неактивная лавка
                depot_id_3,   # неизвестный depot_id и неизвестный кластер
            )),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_import_data',
                        json={'csv': csv})

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_FILE_PARSE', 'код')
        t.json_has('details.list', 'ошибки есть')

        rows_errors = t.res['json']['details']['list']
        er_bad_cluster = er_inactive_store = 0
        for e in rows_errors:
            tap.ok(e['field'] == 'depot_id', 'ошибка на поле depot_id')
            if e['code'] == 'ER_CLUSTER_SETUP':
                er_bad_cluster += 1
            elif e['code'] == 'ER_STORE_IS_INACTIVE':
                er_inactive_store += 1
            else:
                tap.failed(f'неизвестная ошибка: {e["code"]}')

        tap.eq(er_bad_cluster, 2, 'все 3 строки с неизвестными кластерами')
        tap.eq(er_inactive_store, 1, '1 строка с выключенной лавкой')
        tap.eq(len(rows_errors), 3, 'кол-во ошибок')

        cluster = await dataset.cluster()
        store.cluster = cluster.title
        store.cluster_id = cluster.cluster_id
        await store.save()


async def test_csv_decimal_separator(
        tap, api, dataset, now, time2iso_utc, replace_csv_data, job, unique_int,
):
    with tap.plan(8, 'Проверка различных десятичных разделителей'):
        store = await dataset.store(external_id=str(unique_int()))
        user = await dataset.user(store=store)

        started_at = now() + timedelta(days=1)

        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', store.external_id),
            ('date', time2iso_utc(started_at.date())),
            ('start', '12.5'),
            ('duration', '2,25'),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shifts = (
            await CourierShift.list(
                by='look',
                conditions=(
                    ('store_id', store.store_id),
                    ('source', 'batch'),
                )
            )
        ).list

        tap.eq(len(shifts), 12, 'все смены на складе')

        started_at = started_at.replace(
            hour=12,
            minute=30,
            second=0,
            microsecond=0,
            tzinfo=tzone('Europe/Moscow'),
        )
        tap.eq(shifts[0].started_at, started_at, 'start')

        closes_at = started_at + timedelta(hours=2, minutes=15)
        tap.eq(shifts[0].closes_at, closes_at, 'duration')


@pytest.mark.parametrize('col_name,col_value,courier_shift_setup', (
    ('date', '', {}),
    ('date', 'abcdefg1234', {}),
    ('start', 'abcdefg1234', {}),
    ('start', '-1', {}),
    ('start', '25', {}),
    ('duration', '', {}),
    ('duration', '0', {'slot_min_size': 2 * 3600}),
    ('duration', '9', {'slot_max_size': 8 * 3600}),
    ('number_of_couriers', '', {}),
    ('number_of_couriers', 'abcdefg1234', {}),
    ('number_of_couriers', '-1', {}),
    ('auto', '', {}),
    ('auto', 'abcdefg1234', {}),
    ('guarantee', '-1', {}),
    ('guarantee', 'abcdefg1234', {}),
))
async def test_csv_validator_bad(
        tap, api, dataset, replace_csv_data, unique_int,
        col_name, col_value, courier_shift_setup
):
    with tap.plan(5, f'Проверка ошибки "{col_name}={col_value}"'):
        cluster = await dataset.cluster(courier_shift_setup=courier_shift_setup)
        store = await dataset.store(
            external_id=str(unique_int()),
            cluster=cluster,
        )
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', store.external_id),
            # повреждаем нужный столбец
            (col_name, col_value),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_FILE_PARSE', 'код')
        t.json_has('details.list', 'ошибки есть')

        rows_errors = t.res['json']['details']['list']
        rows_number = len(VALID_CSV.strip().split('\n')) - 1
        tap.eq(len(rows_errors), rows_number, 'кол-во строк с ошибками')


async def test_csv_validator_headers(tap, api):
    with tap.plan(5, 'Проверка файла с кривыми заголовками'):
        csv = ("region_id;region_name;depot_id;area_name;date;weekday;start;"
               "duration;number of couriers;auto;public;;\n"
               "1562;Тель-Авив;12173;Deli;24.10.2021;2;6.5;8;3;foot;;;")

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_FILE_PARSE', 'код')
        t.json_has('details.list', 'ошибки есть')

        tap.eq(t.res['json']['details']['list'],
               [{
                   'code': 'ER_INVALID_HEADER_FORMAT',
                   'row_id': 0,
                   'field': '',
               }],
               'ошибка в заголовке')


@pytest.mark.parametrize('col_name,col_value,courier_shift_setup', (
    ('start', '', {}),
    ('start', '         ', {}),
    ('start', '13', {}),
    ('start', '13.5', {}),
    ('start', '13,5', {}),
    ('start', '13:30', {}),
    ('start', ' 13:30 ', {}),
    ('duration', '0', {'slot_min_size': 0}),
    ('duration', '4.5', {}),
    ('duration', '9', {'slot_max_size': 9 * 3600}),
    ('auto', 'пеший', {}),
    ('auto', ' пеший    ', {}),
    ('auto', 'ПеШий', {}),
    ('auto', 'auto', {}),
    ('auto', 'FooT', {}),
    ('auto', 'pedestrian', {}),
    ('auto', 'car', {}),
    ('guarantee', '', {}),
    ('guarantee', '     ', {}),
    ('guarantee', '123', {}),
    ('guarantee', '0', {}),
))
async def test_csv_validator_good(
        tap, api, dataset, replace_csv_data, unique_int,
        col_name, col_value, courier_shift_setup
):
    with tap.plan(6, f'Проверка отсутствие ошибки "{col_name}={col_value}"'):
        cluster = await dataset.cluster(courier_shift_setup=courier_shift_setup)
        store = await dataset.store(
            external_id=str(unique_int()),
            cluster=cluster,
        )
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', store.external_id),
            # модифицируем нужный столбец
            (col_name, col_value),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('import_id', r'^\S+$')
        t.json_hasnt('details', 'ошибок нет')


@pytest.mark.parametrize('store_status', ('active', 'disabled'))
async def test_csv_validator_good_status(
        tap, api, dataset, unique_int, replace_csv_column, store_status,
):
    with tap.plan(6, 'Проверка статуса лавки'):
        store = await dataset.store(
            external_id=str(unique_int()),
            status=store_status,
        )
        user = await dataset.user(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={
                'csv': replace_csv_column(
                    VALID_CSV, column='depot_id', value=store.external_id,
                )
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('import_id', r'^\S+$')
        t.json_hasnt('details', 'ошибок нет')


async def test_job_errors_to_stash(
        tap: PytestTap, api, dataset, job, load_file, now, unique_int,
        time2iso_utc, replace_csv_data,
):
    with tap.plan(9, 'Проверка получения ошибок из джобы через ивенты'):
        store = await dataset.store(external_id=str(unique_int()))
        user = await dataset.user(store=store)

        # Сделаем одну дату в файле невалидной
        valid_date = partial(time2iso_utc, (now() + timedelta(days=1)).date())
        new_dates = defaultdict(valid_date)
        new_dates[1] = time2iso_utc((now() - timedelta(days=1)).date())

        csv = replace_csv_data(
            load_file('test_import_data/norm.csv'),
            ('depot_id', store.external_id),

            # модифицируем нужный столбец
            ('date', new_dates),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('import_id', r'^\S+$')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # Найдём Event отправленный на фронт
        import_id = t.res['json']['import_id']
        import_event = None
        for event in lp.dump():
            if (
                    event.data.get('type') == 'courier_shifts_import_data'
                    and event.data.get('import_id') == import_id
            ):
                import_event = event
                break

        tap.ok(import_event, 'Ивент об окончании работ отправлен')
        stash_group_error = import_event.data['stash_group_error']
        tap.ok(stash_group_error, 'Ивент содержит группу для получения ошибок')

        # Получим ошибки по импорту
        cursor = await Stash.list(
            by='full',
            conditions=[
                ('group', stash_group_error),
            ],
            sort=(),
        )
        tap.eq_ok(len(cursor.list), 1, 'Список ошибок сохранён')
        tap.eq_ok(
            cursor.list[0].value.get('code'),
            'IMPORT_DATA_IN_PAST',
            'Сохранена ошибка с верным сообщением'
        )


async def test_alien_store_company(
        tap, api, dataset, time2iso_utc, now, job, unique_int, replace_csv_data,
):
    with tap.plan(15, 'Импортирование смен в чужие лавки/компании'):
        # своя лавка, своя компания
        depot_id1 = str(unique_int())
        company1 = await dataset.company()
        store1 = await dataset.store(external_id=depot_id1, company=company1)
        user1 = await dataset.user(store=store1, role='admin')

        # чужая лавка, своя компания
        depot_id2 = str(unique_int())
        store2 = await dataset.store(external_id=depot_id2, company=company1)

        # чужая лавка, чужая компания
        depot_id3 = str(unique_int())
        store3 = await dataset.store(external_id=depot_id3)

        # правим CSV
        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', (depot_id1, depot_id2, depot_id3)),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        stores = {store1.store_id, store2.store_id, store3.store_id}
        shifts = (
            await CourierShift.list(
                by='look',
                conditions=('store_id', stores)
            )
        ).list
        tap.ok(shifts, 'Импортированы')
        tap.eq({x.store_id for x in shifts}, stores, 'лавки у смен правильные')

        schedule_id = t.res['json']['import_id']
        schedule = await CourierShiftSchedule.load(schedule_id)
        tap.ok(schedule, 'Расписание')
        tap.eq(schedule.store_id, user1.store_id, 'store_id совпал')
        tap.eq(schedule.company_id, user1.company_id, 'company_id совпал')

        store2shift = {s.store_id: s.courier_shift_id for s in shifts}

        # доступность из чужой лавки, но из этой же компании
        shift_id = store2shift[store2.store_id]
        t = await api(user=await dataset.user(store=store2))
        await t.post_ok('api_admin_courier_shifts_load',
                        json={'courier_shift_id': shift_id})
        t.status_is(200, diag=True)
        t.json_is('courier_shift.courier_shift_id', shift_id, 'идентификатор')

        # доступность из чужой лавки и из чужой компании
        shift_id = store2shift[store3.store_id]
        t = await api(user=await dataset.user(store=store3))
        await t.post_ok('api_admin_courier_shifts_load',
                        json={'courier_shift_id': shift_id})
        t.status_is(200, diag=True)
        t.json_is('courier_shift.courier_shift_id', shift_id, 'идентификатор')


async def test_store_is_none(
        tap, api, dataset, time2iso_utc, now, job, unique_int, replace_csv_data,
):
    with tap.plan(8, 'Импортирование смен без собственной лавки'):
        company1 = await dataset.company()
        user1 = await dataset.user(store_id=None,
                                   company_id=company1.company_id,
                                   role='admin')

        # чужая лавка, своя компания
        depot_id2 = str(unique_int())
        store2 = await dataset.store(external_id=depot_id2, company=company1)

        # чужая лавка, чужая компания
        depot_id3 = str(unique_int())
        store3 = await dataset.store(external_id=depot_id3)

        # правим CSV
        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', (depot_id2, depot_id2, depot_id3)),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        stores = {store2.store_id, store3.store_id}
        shifts = (
            await CourierShift.list(
                by='look',
                conditions=('store_id', stores)
            )
        ).list
        tap.ok(len(shifts), 3, 'Импортированы')

        schedule_id = t.res['json']['import_id']
        schedule = await CourierShiftSchedule.load(schedule_id)
        tap.ok(schedule, 'Расписание')
        tap.eq(schedule.store_id, None, 'store_id совпал, None')
        tap.eq(schedule.company_id, user1.company_id, 'company_id совпал')


@pytest.mark.parametrize(
    'out_of_store,out_of_company,imported_shifts',
    (
        (False, False, 1),  # только своя лавка
        (True,  False, 2),  # все лавки внутри своей компании
        (True,  True,  3),  # все лавки всех компаний
    )
)
async def test_prohibit_alien_stores(
        tap, api, dataset, time2iso_utc, now, job, replace_csv_data, unique_int,
        out_of_store, out_of_company, imported_shifts
):
    with tap.plan(6, 'Проверка прав на импорт в чужие лавки/компании'):
        # своя лавка, своя компания
        area_id1 = str(unique_int())
        company1 = await dataset.company()
        store1 = await dataset.store(external_id=area_id1, company=company1)

        # чужая лавка, своя компания
        area_id2 = str(unique_int())
        store2 = await dataset.store(external_id=area_id2, company=company1)

        # чужая лавка, чужая компания
        area_id3 = str(unique_int())
        store3 = await dataset.store(external_id=area_id3)

        # модифицируем CSV
        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', (area_id1, area_id2, area_id3)),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
            ('number_of_couriers', '1'),
        )

        user = await dataset.user(store=store1, role='admin')
        with user.role as role:
            role.add_permit('out_of_store', out_of_store)
            role.add_permit('out_of_company', out_of_company)

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shifts_import_data',
                json={'csv': csv},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.ok(await job.call(await job.take()), 'Задание выполнено')

            stores = [store1.store_id, store2.store_id, store3.store_id]
            shifts = (
                await CourierShift.list(
                    by='look',
                    conditions=('store_id', stores)
                )
            ).list
            tap.ok(shifts, 'Импортированы')
            tap.eq(sorted([x.store_id for x in shifts]),
                   sorted(stores[:imported_shifts]),
                   'импортированы смены, только из доступных area_id')


async def test_dst(tap, api, dataset, replace_csv_data, job, unique_int):
    with tap.plan(7, 'Проверяем переход на летнее время'):
        store = await dataset.store(
            external_id=str(unique_int()),
            tz='Europe/Paris',
        )
        user = await dataset.user(store=store)

        csv = replace_csv_data(
            VALID_CSV,
            ('depot_id', store.external_id),
            ('date', ['30.10.2021', '31.10.2021', '01.11.2021']),
            ('start', '18'),
            ('duration', ['1', '2', '3']),
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        import_id = t.res['json']['import_id']

        task = await job.take()
        task.data.update({'now_': '2021-10-29 12:00:00 +0200'})
        tap.ok(await job.call(task), 'Задание выполнено')

        shifts = await dataset.CourierShift.list(
            by='full',
            conditions=[('import_id', import_id)],
            sort=(),
        )
        shifts = {x.duration: x for x in shifts.list}

        with shifts[1 * 60 * 60] as shift:
            tap.eq(
                shift.started_at,
                datetime(
                    2021, 10, 30, 18, 0, 0,
                    tzinfo=tzone(timedelta(hours=2))
                ),
                'начало в летнее время'
            )

        with shifts[2 * 60 * 60] as shift:
            tap.eq(
                shift.started_at,
                datetime(
                    2021, 10, 31, 18, 0, 0,
                    tzinfo=tzone(timedelta(hours=1))
                ),
                'начало в зимнее время'
            )

        with shifts[3 * 60 * 60] as shift:
            tap.eq(
                shift.started_at,
                datetime(
                    2021, 11, 1, 18, 0, 0,
                    tzinfo=tzone(timedelta(hours=1))
                ),
                'начало в зимнее время'
            )


async def test_create_permit_revoked(
        tap, dataset, api, replace_csv_data, job, now, time2iso_utc, unique_int,
):
    with tap.plan(6, 'Создание не выполняется, если пермит отключен'
                     'в настройках кластера'):
        csv = '\n'.join(VALID_CSV.split('\n')[:3])

        # ограничений нет
        cluster_1 = await dataset.cluster()
        store_1 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster_1,
            external_id=str(unique_int()),
        )

        # у админа отключена возможность создания
        cluster_2 = await dataset.cluster(disabled_role_permits={
            'admin': ['courier_shifts_create']
        })
        store_2 = await dataset.store(
            tz='Europe/Moscow',
            cluster=cluster_2,
            external_id=str(unique_int()),
        )

        csv = replace_csv_data(
            csv,
            ('number_of_couriers', '1'),
            ('depot_id', [store_1.external_id, store_2.external_id,]),
            ('date', time2iso_utc((now() + timedelta(days=1)).date())),
        )

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_import_data',
            json={'csv': csv},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shifts = (await CourierShift.list(
            by='full',
            conditions=('store_id', store_1.store_id)
        )).list
        tap.eq(len(shifts), 1, 'смена на первом складе создана')

        shifts = (await CourierShift.list(
            by='full',
            conditions=('store_id', store_2.store_id)
        )).list
        tap.eq(len(shifts), 0, 'а на втором - нет')
