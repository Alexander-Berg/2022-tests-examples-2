import random

from scripts.cron.couriers_tags_in_shifts import process_courier_tags
from stall.client.grocery_tags import client as client_gt
from stall.model.courier import Courier, EXPORTED_FIELDS
from stall.script import csv2dicts, objects2csv


# pylint: disable=too-many-locals
async def test_simple(tap, api, dataset, job, load_file, replace_csv_column):
    with tap.plan(13, 'Обновление курьеров из файла CSV'):
        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        rows = csv2dicts(csv, fieldnames=EXPORTED_FIELDS)

        couriers = [
            await dataset.courier(
                vars={
                    'external_ids': {
                        'eats': str(random.randint(1000000, 9999999)),
                    },
                },
            )
            for _ in range(len(rows))
        ]

        courier_ids = [courier.courier_id for courier in couriers]

        tag1 = await dataset.courier_shift_tag(type='courier')
        tag2 = await dataset.courier_shift_tag(type='courier')
        tags = [tag1.title, tag2.title]
        tags_data = ','.join(tags)

        csv = replace_csv_column(csv, 'courier_id', value=courier_ids)
        csv = replace_csv_column(csv, 'tags', value=tags_data)

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        couriers = await Courier.list(
            by='look',
            conditions=(
                ('courier_id', courier_ids),
            ),
        )

        tap.ok(couriers.list, 'Импортированы')

        received = couriers.list
        tap.eq(len(received), len(rows), 'Получены все курьеры')
        tap.ok(received[0].courier_id in courier_ids, 'Курьер 1 обновлён')
        tap.ok(received[1].courier_id in courier_ids, 'Курьер 2 обновлён')
        tap.ok(received[2].courier_id in courier_ids, 'Курьер 3 обновлён')


async def test_ids(tap, api, dataset, job, load_file, replace_csv_column):
    with tap.plan(7, 'Обновление курьеров c ID Лавки, Еды и Такси'):
        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        rows = csv2dicts(csv, fieldnames=EXPORTED_FIELDS)

        couriers = [
            await dataset.courier(
                vars={
                    'external_ids': {
                        'eats': str(random.randint(1000000, 9999999)),
                    },
                },
            )
            for _ in range(len(rows))
        ]

        courier_real_ids = [courier.courier_id for courier in couriers]

        courier_ids = [
            couriers[0].courier_id,
            couriers[1].external_id,
            couriers[2].vars['external_ids']['eats'],
            couriers[3].vars['external_ids']['eats'],  # заглушка, т.к. 4 строки
        ]

        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()
        tags = [tag1.title, tag2.title]
        tags_data = ','.join(tags)

        csv = replace_csv_column(csv, 'courier_id', value=courier_ids)
        csv = replace_csv_column(csv, 'tags', value=tags_data)

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        couriers = await Courier.list(
            by='look',
            conditions=(
                ('tags', '&&', tags),
            ),
        )

        tap.ok(couriers.list, 'Импортированы')

        csv = replace_csv_column(csv, 'courier_id', value=courier_real_ids)
        rows = csv2dicts(csv, fieldnames=EXPORTED_FIELDS)

        expected = [{
            'courier_id': row['courier_id'],
            'tags': row['tags'].split(','),
        } for row in rows].sort(key=lambda x: x['courier_id'])

        received = [{
            'courier_id': courier.courier_id,
            'tags': courier.tags,
        } for courier in couriers].sort(key=lambda x: x['courier_id'])

        tap.eq(received, expected, 'Все курьеры обновлены')


async def test_simple_2(tap, api, dataset, job):
    with tap.plan(11, 'Проверка импорта'):
        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()
        tag3 = await dataset.courier_shift_tag()

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        store3 = await dataset.store(cluster=cluster)

        courier_edit    = await dataset.courier(
            cluster=cluster,
            tags=[tag1.title],
            tags_store=[store1.store_id],
        )
        courier_remove  = await dataset.courier(
            cluster=cluster,
            tags=[tag1.title],
            tags_store=[store1.store_id],
        )
        courier_add     = await dataset.courier(cluster=cluster)

        csv = objects2csv(
            objects=[{
                'courier_id': courier_edit.courier_id,
                'tags': tag2.title,
                'depot_id': store2.external_id,
                'region': 'Кластер уничтожающий шушун',
                'courier_eda_id': '1234567',
                'name': '',
                'delivery': 'foot',
                'status': 'active',
            }, {
                'courier_id': courier_remove.courier_id,
                'tags': '',
                'depot_id': '',
                'region': 'Кластер уничтожающий шушун',
                'courier_eda_id': '1234567',
                'name': '',
                'delivery': 'foot',
                'status': 'active',
            }, {
                'courier_id': courier_add.courier_id,
                'tags': ', '.join([
                    tag2.title,
                    tag3.title,
                    tag2.title,  # тестируем отсутствие повторений
                ]),
                'depot_id': ' , '.join([
                    store2.external_id,
                    store3.external_id,
                    store2.external_id,  # тестируем отсутствие повторений
                ]),
                'region': 'Кластер уничтожающий шушун',
                'courier_eda_id': '1234567',
                'name': '',
                'delivery': 'foot',
                'status': 'active',
            }],
            fieldnames=EXPORTED_FIELDS,
        )

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={'csv': csv})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await courier_edit.reload() as courier:
            tap.eq(courier.tags, [tag2.title], 'Теги изменены')
            tap.eq(courier.tags_store, [store2.store_id], 'Привязка изменена')

        with await courier_remove.reload() as courier:
            tap.eq(courier.tags, [], 'Теги удалены')
            tap.eq(courier.tags_store, [], 'Привязка удалена')

        with await courier_add.reload() as courier:
            tap.eq(
                sorted(courier.tags),
                sorted([tag2.title, tag3.title]),
                'Теги добавлены'
            )
            tap.eq(
                sorted(courier.tags_store),
                sorted([store2.store_id, store3.store_id]),
                'Привязка добавлена'
            )


async def test_only_id(tap, api, dataset, job):
    with tap.plan(8, 'Можно указывать не все поля а только нужные'):
        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()

        courier_edit    = await dataset.courier(tags=[tag1.title])
        courier_remove  = await dataset.courier(tags=[tag1.title])
        courier_add     = await dataset.courier()

        csv = objects2csv(
            objects=[{
                'courier_id': courier_edit.courier_id,
                'tags': tag2.title,
            }, {
                'courier_id': courier_remove.courier_id,
                'tags': '',
            }, {
                'courier_id': courier_add.courier_id,
                'tags': tag2.title,
            }],
            fieldnames=['courier_id', 'tags'],
        )

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={'csv': csv})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await courier_edit.reload() as courier:
            tap.eq(courier.tags, [tag2.title], 'Теги изменены')

        with await courier_remove.reload() as courier:
            tap.eq(courier.tags, [], 'Теги удалены')

        with await courier_add.reload() as courier:
            tap.eq(courier.tags, [tag2.title], 'Теги добавлены')


async def test_only_id_any(tap, api, dataset, job):
    with tap.plan(8, 'Можно указывать не все поля с любым id'):
        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()

        courier_edit    = await dataset.courier(tags=[tag1.title])
        courier_remove  = await dataset.courier(tags=[tag1.title])
        courier_add     = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(random.randint(1000000, 9999999)),
                },
            },
        )

        csv = objects2csv(
            objects=[{
                'courier_eda_id': courier_edit.courier_id,
                'tags': tag2.title,
            }, {
                'courier_eda_id': courier_remove.external_id,
                'tags': '',
            }, {
                'courier_eda_id': courier_add.vars['external_ids']['eats'],
                'tags': tag2.title,
            }],
            fieldnames=['courier_eda_id', 'tags'],
        )

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={'csv': csv})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await courier_edit.reload() as courier:
            tap.eq(courier.tags, [tag2.title], 'Теги изменены')

        with await courier_remove.reload() as courier:
            tap.eq(courier.tags, [], 'Теги удалены')

        with await courier_add.reload() as courier:
            tap.eq(courier.tags, [tag2.title], 'Теги добавлены')


async def test_wrong_tags(
        tap, api, dataset, job, load_file, uuid, replace_csv_column
):
    with tap.plan(7, 'Неправильные теги'):
        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        courier = await dataset.courier()
        tag = await dataset.courier_shift_tag()
        tags = [tag.title, uuid()]
        tags_data = ','.join(tags)

        csv = replace_csv_column(csv, 'courier_id', value=courier.courier_id)
        csv = replace_csv_column(csv, 'tags', value=tags_data)

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('errors', r'^error:\w+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        couriers = await Courier.list(
            by='look',
            conditions=(
                ('tags', '&&', tags),
            ),
        )

        tap.eq(couriers.list, [], 'Теги не изменены')


async def test_system_tags(
        tap, api, dataset, job, load_file, uuid, replace_csv_data,
):
    with tap.plan(10, 'Проверка редактирования системных тегов'):
        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        tag_1 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag_2 = await dataset.courier_shift_tag(title=f'tag-{uuid()}')
        tag_sys = await dataset.courier_shift_tag(title=f'tag-system-{uuid()}',
                                                  group='system')

        courier_1 = await dataset.courier(
            tags=[tag_1.title],                   # системного тега не было
        )
        courier_2 = await dataset.courier(
            tags=[tag_sys.title],                 # был только системный тег
        )
        courier_3 = await dataset.courier(
            tags=[tag_sys.title, tag_1.title],    # был системный и простой
        )
        courier_4 = await dataset.courier(
            tags=[tag_sys.title, tag_1.title],    # был системный и простой
        )

        csv = replace_csv_data(
            csv,
            ('courier_id', [
                courier_1.courier_id,
                courier_2.courier_id,
                courier_3.courier_id,
                courier_4.courier_id,
            ]),
            ('tags', [
                f'{tag_1.title},{tag_sys.title}',   # попытка выдать системный
                f'{tag_1.title}',                   # а тут попытка подменить
                f'{tag_sys.title},{tag_2.title}',   # выдаем выданный + замена
                '',                                 # пробуем все снять
            ]),
        )

        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')
        t.json_like('errors', r'^error:\w+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await courier_1.reload() as courier:
            tap.eq(courier.tags, [tag_1.title], 'системный тег не назначен')

        with await courier_2.reload() as courier:
            tap.eq(sorted(courier.tags),
                   sorted([tag_1.title, tag_sys.title]),
                   'системный тег остался на месте и добавился новый')

        with await courier_3.reload() as courier:
            tap.eq(sorted(courier.tags),
                   sorted([tag_sys.title, tag_2.title]),
                   'системный тег остался на месте, а второй заменился новый')

        with await courier_4.reload() as courier:
            tap.eq(courier.tags,
                   [tag_sys.title],
                   'системный тег на месте, а обычный снят')


async def test_external(tap, api, dataset, job, load_file, replace_csv_column):
    with tap.plan(10, 'Проверка файлов'):
        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        rows = csv2dicts(csv, fieldnames=EXPORTED_FIELDS)

        count = len(rows)
        couriers = [await dataset.courier() for _ in range(count)]
        courier_ids = [courier.courier_id for courier in couriers[:count//2]] \
            + [courier.external_id for courier in couriers[count//2:]]

        tag1 = await dataset.courier_shift_tag()
        tag2 = await dataset.courier_shift_tag()
        tags = [tag1.title, tag2.title]
        tags_data = ','.join(tags)

        csv = replace_csv_column(csv, 'courier_id', value=courier_ids)
        csv = replace_csv_column(csv, 'tags', value=tags_data)

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })

        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        couriers_loaded = await Courier.list(
            by='look',
            conditions=(
                ('tags', '&&', tags),
            ),
        )

        tap.ok(couriers_loaded.list, 'Импортированы')

        expected = {courier.courier_id for courier in couriers}
        received = {courier.courier_id for courier in couriers_loaded}

        tap.eq(received, expected, 'Все курьеры обновлены')


async def test_only_depot_id(tap, api, dataset, job):
    with tap.plan(8, 'Можно указывать не все поля а только нужные: depot_id'):

        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)

        courier_edit    = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.external_id]
        )
        courier_remove  = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.external_id],
        )
        courier_add     = await dataset.courier(cluster=cluster,)

        csv = objects2csv(
            objects=[{
                'courier_id': courier_edit.courier_id,
                'depot_id': store2.external_id,
            }, {
                'courier_id': courier_remove.courier_id,
                'depot_id': '',
            }, {
                'courier_id': courier_add.courier_id,
                'depot_id': store2.external_id,
            }],
            fieldnames=['courier_id', 'depot_id'],
        )

        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={'csv': csv})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await courier_edit.reload() as courier:
            tap.eq(courier.tags_store, [store2.store_id], 'Теги изменены')

        with await courier_remove.reload() as courier:
            tap.eq(courier.tags_store, [], 'Теги удалены')

        with await courier_add.reload() as courier:
            tap.eq(courier.tags_store, [store2.store_id], 'Теги добавлены')


async def test_update_tags_in_shift(
    tap, api, dataset, job, ext_api, load_file, replace_csv_data,
):
    with tap.plan(7, 'Обновляем теги курьера + и у всех его смен'):
        async def handler(request):  # pylint: disable=unused-argument
            return 200, 'OK'

        filepath = 'data/test_update_couriers.csv'
        csv = load_file(filepath)

        rows = csv2dicts(csv, fieldnames=EXPORTED_FIELDS)

        # без тегов
        cluster = await dataset.cluster()
        couriers = [
            await dataset.courier(cluster=cluster, tags=[])
            for _ in range(len(rows))
        ]
        shifts = [
            await dataset.courier_shift(
                cluster=cluster,
                status='waiting',
                courier=courier,
                courier_tags=None,  # тегов тоже нет
            )
            for courier in couriers
        ]

        tags = sorted([
            (await dataset.courier_shift_tag(type='courier')).title,
            (await dataset.courier_shift_tag(type='courier')).title,
        ])

        csv = replace_csv_data(
            csv,
            ('courier_id', [courier.courier_id for courier in couriers]),
            ('tags', ','.join(tags)),
        )

        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok('api_admin_couriers_import_data', json={
            'csv': csv,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with tap.subtest(2 * len(couriers), 'Теги курьеров обновились') as _tap:
            for courier in couriers:
                with await courier.reload():
                    _tap.eq(courier.tags, tags, 'теги обновлены')
                    _tap.ok(courier.tags_updated is not None, 'время обновлено')

        # крон-скрипт перемалывает смены и обновляет в них теги
        async with await ext_api(client_gt, handler):
            await process_courier_tags(cluster_id=cluster.cluster_id)

        with tap.subtest(len(shifts), 'Теги курьеров в сменах тоже') as _tap:
            for shift in shifts:
                with await shift.reload():
                    _tap.eq(shift.courier_tags, tags, 'теги обновлены')
