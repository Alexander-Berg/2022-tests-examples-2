import random
import pytest

from stall.api.admin.shelves.import_data import CSV_REQUIRED_FIELDS
from stall.model.shelf import (
    SHELF_STATUSES,
    SHELF_TYPES,
    Shelf,
    SHELF_WH_GROUPS,
)
from stall.model.stash import Stash


async def test_job_created(tap, api, dataset, uuid, make_csv_str):
    with tap.plan(10, 'Импортируем, джоба создается'):
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)

        t = await api()
        t.set_user(admin)

        rows = [
            {
                'rack':              'стеллаж с сосисками',
                'shelf':             uuid(),
                'status':            SHELF_STATUSES[0],
                'shelf_external_id': uuid(),
            }
            for _ in range(5)
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'status', 'shelf_external_id'],
            rows,
        )
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'shelves_import-{store.store_id}'
        stash = await Stash.unstash(name=stash_name)

        tap.ok(stash, 'Shelves in stash')
        tap.eq_ok(stash.value('user_id'), admin.user_id, 'user_id')
        tap.eq_ok(stash.value('store_id'), store.store_id, 'store_id')
        tap.ok(stash.value('rows'), rows)
        first_row = stash.value('rows.0')
        tap.eq(
            set(first_row),
            {'rack', 'shelf', 'status', 'external_id', 'shelf_external_id'},
            'Все поля попали в стэш'
        )
        tap.eq(
            first_row['external_id'],
            first_row['shelf_external_id'],
            'Значения external перемапили'
        )


async def test_er_no_store(tap, api, dataset):
    with tap.plan(4):
        admin = await dataset.user(role='admin')
        admin.store_id = None
        await admin.save()

        t = await api()
        t.set_user(admin)

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': ''},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', "User don't have assigned store")


async def test_er_no_rows(tap, api):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': 'a,b,c'},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'There is 0 rows')


async def test_er_too_many_rows(tap, api, uuid, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')

        rows = [
            {
                'rack':  'стеллаж с сосисками',
                'shelf': uuid(),
            }
            for _ in range(2001)
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'order', 'type', 'tag', 'barcode', 'status'],
            rows,
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'Request has more than')


async def test_er_bad_columns(tap, api, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')

        csv_str = make_csv_str(
            ['a', 'b'],
            [{'a': i, 'b': i} for i in range(10)],
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'CSV required fields not found:'
        )


async def test_er_no_required_cols(tap, api, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')
        rows_count = 10

        _, *some_req = CSV_REQUIRED_FIELDS
        # fill every required field except of one
        csv_str = make_csv_str(
            CSV_REQUIRED_FIELDS,
            [{key: i * 10 + j for j, key in enumerate(list(some_req), start=1)}
             for i in range(1, rows_count + 1)],
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'Field required'
        )


async def test_er_status_is_correct(tap, api, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')
        rows_count = 10

        # "status" field is wrong here
        field_mixin = {'status': 'WRONG_STATUS'}
        keys_no_mixin = list(set(CSV_REQUIRED_FIELDS) - set(field_mixin.keys()))
        csv_str = make_csv_str(
            list(field_mixin.keys()) + list(keys_no_mixin),
            [
                {**field_mixin, **{
                    key: i * 10 + j
                    for j, key in enumerate(list(keys_no_mixin), start=1)
                }} for i in range(1, rows_count + 1)
            ],
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'has wrong "status" field.'
        )


async def test_er_type_is_correct(tap, api, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')
        rows_count = 10

        # 'type' field is wrong here
        field_mixin = {'type': 'WRONG_TYPE', 'status': SHELF_STATUSES[0]}
        keys_no_mixin = list(set(CSV_REQUIRED_FIELDS) - set(field_mixin.keys()))
        csv_str = make_csv_str(
            list(field_mixin.keys()) + list(keys_no_mixin),
            [
                {**field_mixin, **{
                    key: i * 10 + j
                    for j, key in enumerate(list(keys_no_mixin), start=1)
                }} for i in range(1, rows_count + 1)
            ],
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'has wrong "type" field.'
        )


async def test_er_tag_is_correct(tap, api, make_csv_str):
    with tap.plan(4):
        t = await api(role='admin')
        rows_count = 10

        # 'tag' field is wrong here
        field_mixin = {
            'tag':    'WRONG_TAG',
            'type':   SHELF_TYPES[0],
            'status': SHELF_STATUSES[0]
        }
        keys_no_mixin = list(set(CSV_REQUIRED_FIELDS) - set(field_mixin.keys()))
        csv_str = make_csv_str(
            list(field_mixin.keys()) + list(keys_no_mixin),
            [
                {**field_mixin, **{
                    key: i * 10 + j
                    for j, key in enumerate(list(keys_no_mixin), start=1)
                }} for i in range(1, rows_count + 1)
            ],
        )

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like(
            'message',
            'has wrong "tag" field.'
        )


async def test_er_import_started(tap, api, uuid, make_csv_str):
    with tap.plan(8):
        t = await api(role='admin')

        rows = [
            {
                'rack':   'стеллаж с сосисками',
                'shelf':  uuid(),
                'status': SHELF_STATUSES[0],
                'type':   SHELF_TYPES[0],
            }
            for _ in range(5)
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'order', 'type', 'tag', 'barcode', 'status'],
            rows,
        )
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'Import already started by user:')


async def test_shelf_in_order(tap, api, dataset, make_csv_str, job):
    with tap.plan(14, 'На полку есть созданный документ в работе'):
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)
        product = await dataset.product()
        shelves = [await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title=f'полка_{i}',
            status='active'
        ) for i in range(2)]

        t = await api()
        t.set_user(admin)

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={
                'csv': make_csv_str(
                    ['rack', 'shelf', 'width', 'status', 'type'],
                    [
                        {
                            'rack':   shelf.rack,
                            'shelf':  shelf.title,
                            'width':  random.randint(10, 1000),
                            'status': 'disabled',
                            'type':   'parcel',
                        } for shelf in shelves
                    ],
                )},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash = await Stash.load(
            f'shelves_import-{admin.store_id}', by='name')

        await dataset.order(
            store=store,
            type='check_product_on_shelf',
            products=[product.product_id],
            shelves=[shelves[0].shelf_id],
            status='reserving',
            estatus='begin',
        )

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        err_stash_0 = await Stash.load(
            f'error:{stash.stash_id}:0', by='name')

        tap.eq(err_stash_0.value['code'], 'ER_ORDERS_CONFLICT', 'error')
        tap.eq_ok(
            sorted(err_stash_0.value['value'], key=lambda x: x['field']),
            [
                {
                    'field':     'status',
                    'new_value': 'disabled',
                    'old_value': 'active'
                },
                {
                    'field':     'type',
                    'new_value': 'parcel',
                    'old_value': 'store'
                }
            ],
            'ошибки из-за изменения статуса и типа активной полки'
        )

        err_stash_1 = await Stash.load(
            f'error:{stash.stash_id}:1', by='name')
        tap.eq_ok(err_stash_1, None, 'больше ошибок нет')

        await shelves[0].reload()
        tap.eq(shelves[0].status, 'active',
               'status занятой полки не меняется')
        tap.eq(shelves[0].type, 'store',
               'type занятой полки не меняется')
        tap.eq(shelves[0].width, None,
               'width занятой полки не меняется')

        await shelves[1].reload()
        tap.eq(shelves[1].status, 'active',
               'status свободной полки не меняется')
        tap.eq(shelves[1].type, 'store',
               'type свободной полки не меняется')
        tap.is_ok(shelves[1].width, None,
                'width свободной полки не меняется')


async def test_data(tap, dataset, api, uuid, make_csv_str, job):
    with tap.plan(6, 'Новые полки'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')

        t = await api(user=user)

        rows = [
            {
                'rack':            'стеллаж с сосисками',
                'shelf':           uuid(),
                'height':          random.randint(10, 1000),
                'width':           random.randint(10, 1000),
                'depth':           random.randint(10, 1000),
                'status':          SHELF_STATUSES[1],
                'type':            SHELF_TYPES[0],
                'warehouse_group': SHELF_WH_GROUPS[0]
            }
            for _ in range(5)
        ]
        csv_str = make_csv_str(
            [
                'rack', 'shelf', 'order', 'type', 'tag',
                'barcode', 'status', 'height', 'width', 'depth',
                'warehouse_group'
            ],
            rows,
        )
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        with tap.subtest(None, 'Проверяем полки') as taps:
            for row in rows:
                shelfs = await Shelf.list(
                    by='full',
                    conditions=(
                        ('title', row['shelf']),
                        ('store_id', store.store_id),
                    ),
                    sort=(),
                )
                shelfs = shelfs.list

                taps.eq(len(shelfs), 1, 'Полка создана')
                taps.eq(shelfs[0]['height'], row['height'], 'Высота')
                taps.eq(shelfs[0]['width'], row['width'], 'Ширина')
                taps.eq(shelfs[0]['depth'], row['depth'], 'Глубина')
                taps.eq(
                    shelfs[0]['warehouse_group'],
                    row['warehouse_group'],
                    'Группа товаров',
                )


async def test_renew_data(tap, dataset, api, uuid, make_csv_str, job):
    with tap.plan(13, 'Обновление параметров полки без стоков'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        barcode = uuid()

        shelf = await dataset.shelf(
            store_id=store.store_id,
            title='0',
            barcode=barcode,
            height=200,
            width=350,
            depth=0,
        )
        tap.ok(shelf, 'Первичные значения полок')

        t = await api(user=user)

        rows = [
            {
                'rack':    'стеллаж с сосисками',
                'shelf':   '0',
                'barcode': barcode,
                'height':  0,
                'width':   0,
                'depth':   0,
                'status':  'disabled',
                'type':    'incoming',
                'tag':     'freezer'
            }
        ]
        csv_str = make_csv_str(
            [
                'rack', 'shelf', 'order', 'type', 'tag',
                'barcode', 'status', 'height', 'width', 'depth',
            ],
            rows,
        )
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        shelfs = await Shelf.list(
            by='full',
            conditions=(
                ('title', '0'),
                ('store_id', store.store_id),
            ),
            sort=(),
        )

        tap.ok(shelfs, 'Перезаписанные полки')

        shelf = list(shelfs)[0]

        tap.eq(shelf['height'], None, 'Высота')
        tap.eq(shelf['width'], None, 'Ширина')
        tap.eq(shelf['depth'], None, 'Глубина')
        tap.eq(shelf['type'], 'incoming', 'тип')
        tap.eq(shelf['status'], 'disabled', 'статус')
        tap.eq(shelf['tags'], ['freezer'], 'tags')


async def test_required_only(tap, dataset, api, uuid, job):
    with tap.plan(13, 'Параметры не обновляются, если их не передать'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        barcode = uuid()

        shelf = await dataset.shelf(
            store_id=store.store_id,
            status='active',
            title='0',
            barcode=barcode,
            height=200,
            width=350,
            depth=10,
            type='incoming',
            tags=['freezer']
        )
        tap.ok(shelf, 'Первичные значения полок')

        t = await api(user=user)

        rows = [
            {
                'rack':   'стеллаж с сосисками',
                'shelf':  '0',
                'status': 'disabled',
            }
        ]
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'json': rows},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        shelfs = await Shelf.list(
            by='full',
            conditions=(
                ('title', '0'),
                ('store_id', store.store_id),
            ),
            sort=(),
        )

        tap.eq_ok(len(shelfs.list), 1, 'Перезаписанные полки')

        shelf = list(shelfs)[0]

        tap.eq(shelf['height'], 200, 'Высота')
        tap.eq(shelf['width'], 350, 'Ширина')
        tap.eq(shelf['depth'], 10, 'Глубина')
        tap.eq(shelf['type'], 'incoming', 'тип')
        tap.eq(shelf['tags'], ['freezer'], 'tags')

        tap.eq(shelf['status'], 'disabled', 'статус')


# pylint: disable=too-many-locals
async def test_stock(tap, dataset, api, make_csv_str, job):
    with tap.plan(13, 'Обновление параметров полок со стоками'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        product = await dataset.product()

        shelf_1 = await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title='0'
        )
        shelf_2 = await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title='1',
        )
        for shelf in [shelf_1, shelf_2]:
            await dataset.stock(
                store=store, shelf=shelf, product=product, count=10,
            )

        shelf_2.status = 'disabled'
        await shelf_2.save()
        tap.eq(shelf_2['status'], 'disabled',
            'отключили полку со стоками')

        t = await api(user=user)

        rows = [
            {
                'rack':   shelf_1.rack,
                'shelf':  shelf_1.title,
                'status': 'disabled',
                'type':   'incoming',
                'tag':    'freezer'
            },
            {
                'rack':   shelf_2.rack,
                'shelf':  shelf_2.title,
                'status': 'active',
                'type':   shelf.type
            }
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'status', 'type', 'tag'], rows)
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash = await Stash.load(
            f'shelves_import-{user.store_id}', by='name')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        await shelf_1.reload()
        tap.eq(shelf_1['type'], 'store', 'тип полки со стоком не меняется')
        tap.eq(shelf_1['status'], 'active',
               'статус полки со стоком не меняется на disabled')
        tap.eq(shelf_1['tags'], [], 'tags')

        await shelf_2.reload()
        tap.eq(shelf_2['status'], 'disabled',
               'статус не менятся на active из-за первой полки')

        err_stash_0 = await Stash.load(
            f'error:{stash.stash_id}:0', by='name')

        tap.eq(err_stash_0.value['code'], 'ER_SHELF_WITH_STOCKS', 'error')
        tap.eq_ok(
            sorted(err_stash_0.value['value'], key=lambda x: x['field']),
            [
                {'field':     'status',
                 'new_value': 'disabled',
                 'old_value': 'active'},
                {'field':     'tags',
                 'new_value': ['freezer'],
                 'old_value': []},
                {'field':     'type',
                 'new_value': 'incoming',
                 'old_value': 'store'}
            ],
            'ошибки из-за изменения статуса и типа активной полки'
        )

        err_stash_1 = await Stash.load(
            f'error:{stash.stash_id}:1', by='name')
        tap.eq_ok(err_stash_1, None, 'больше ошибок нет')


async def test_empty_stock(tap, dataset, api, uuid, make_csv_str, job):
    with tap.plan(11, 'Обновление параметров полки с пустым стоком/ '
                      'активация полок со стоком'
    ):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        product = await dataset.product()
        barcode = uuid()

        shelf_1 = await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title='полка с пустым стоком',
            barcode=barcode,
            height=200,
            width=350,
            depth=0,
        )
        await dataset.stock(
            store=store, shelf=shelf_1, product=product, count=0,
        )

        shelf_2 = await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title='отключенная полка со стоком',
        )
        await dataset.stock(
            store=store, shelf=shelf_2, product=product, count=10,
        )
        shelf_2.status = 'disabled'
        await shelf_2.save()
        tap.eq(shelf_2['status'], 'disabled',
            'отключили полку со стоками')

        t = await api(user=user)

        rows = [
            {
                'rack':   shelf_1.rack,
                'shelf':  shelf_1.title,
                'status': 'disabled',
                'type':   'incoming',
                'tag':    'freezer'
            },
            {
                'rack':   shelf_2.rack,
                'shelf':  shelf_2.title,
                'status': 'active',
                'type':   shelf_2.type,
                'tag':    None
            }
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'status', 'type', 'tag'], rows)
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash = await Stash.load(
            f'shelves_import-{user.store_id}', by='name')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        await shelf_1.reload()
        tap.eq(shelf_1['type'], 'incoming', 'тип')
        tap.eq(shelf_1['status'], 'disabled', 'статус')
        tap.eq(shelf_1['tags'], ['freezer'], 'tags')

        await shelf_2.reload()
        tap.eq(
            shelf_2['status'], 'active', 'полка со стоком активировалась')

        err_stash = await Stash.load(
            f'error:{stash.stash_id}:0', by='name')

        tap.eq(err_stash, None, 'ошибок нет')


@pytest.mark.parametrize('csv_str, expected_message', [
    (
        (
            'rack,shelf,order,type,tag,status,height,width,depth\n'
            f'булочки,0,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},0,0,0\n'
            f'сосиски,0,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},0,0\n'
        ),
        'There is invalid row #2',
    ),
    (
        (
            'rack,shelf,order,type,tag,status,external_id\n'
            f'булочки,title,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},123\n'
            f'сосиски,title,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},124\n'
        ),
        'Row #2 has duplicate title',
    ),
    (
        (
            'rack,shelf,order,type,tag,status,external_id\n'
            f'булочки,1,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},123\n'
            f'сосиски,2,,{SHELF_TYPES[0]},,{SHELF_STATUSES[0]},123\n'
        ),
        'Row #2 has duplicate external id'
    ),
])
async def test_invalid_csv(tap, dataset, api, csv_str, expected_message):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', expected_message)


async def test_json(tap, dataset, api, uuid, job):
    with tap.plan(5):
        store = await dataset.store()
        user = await dataset.user(store=store)
        t = await api(user=user)
        rows = [
            {
                'rack':   'Стеллаж',
                'shelf':  uuid(),
                'height': 10,
                'status': SHELF_STATUSES[0],
                'type':   SHELF_TYPES[0],
                'order':  1,
            }
            for _ in range(2)
        ]
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'json': rows},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        job_id = t.res['json']['job_id']
        task = await job.take()
        tap.eq(task.id, job_id, 'Достали нужную таску')
        await job.call(task)
        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(shelves), 2, 'Создано 2 инстанса')


async def test_without_status(tap, dataset, api, make_csv_str, job):
    with tap.plan(9, 'Меняем незащищенные поля по время раскладок'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        await dataset.order(store=store, type='stowage')

        shelf_1 = await dataset.shelf(
            store_id=store.store_id,
            rack='стеллаж с сосисками',
            title='отключенная полка',
            status='disabled'
        )

        t = await api(user=user)
        rows = [
            {
                'rack':   shelf_1.rack,
                'shelf':  shelf_1.title,
                'height': random.randint(10, 1000),

            },
            {
                'rack':   shelf_1.rack,
                'shelf':  'новая полка',
                'height': random.randint(10, 1000),
            }
        ]
        csv_str = make_csv_str(
            ['rack', 'shelf', 'height'], rows)
        await t.post_ok(
            'api_admin_shelves_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash = await Stash.load(
            f'shelves_import-{user.store_id}', by='name')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Джоба из события')
        await job.call(task)

        err_stash = await Stash.load(
            f'error:{stash.stash_id}:0', by='name')

        tap.eq(err_stash, None, 'ошибок нет')

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(shelves), 2, 'Создано 2 инстанса')
        for shelf in shelves:
            if shelf.shelf_id == shelf_1.shelf_id:
                tap.eq(shelf.status, 'disabled', 'статус не изменился')
            else:
                tap.eq(shelf.status, 'active', 'новая полка активна')
