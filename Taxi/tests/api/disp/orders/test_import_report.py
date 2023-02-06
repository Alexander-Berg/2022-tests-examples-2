import random
import pytest

from stall.model.stash import Stash


@pytest.mark.parametrize('rows, expected_rows', [
    (
        'product,count,shelf\n'
        '\n,,\n,,\n'
        '1234,9,cool shelf\n,,\n\n',
        [
            {'count': 9, 'shelf': 'cool shelf', 'product': '1234'},
        ]
    ),
    (
        'external_id\tproduct\tcount\tshelf\n'
        'abcdef\t1234\t11\tmy shelf',
        [
            {'count': 11, 'shelf': 'my shelf', 'product': '1234'},
        ]
    ),
    (
        'product,count,shelf\n'
        '1234,10,cool shelf\n'
        '42,12,mango',
        [
            {'count': 10, 'shelf': 'cool shelf', 'product': '1234'},
            {'count': 12, 'shelf': 'mango', 'product': '42'}
        ]
    ),
    (
        'product,count,shelf\n'
        '1234,10,cool shelf\n'
        ',,\n'
        '42,12,mango',
        [
            {'count': 10, 'shelf': 'cool shelf', 'product': '1234'},
            {'count': 12, 'shelf': 'mango', 'product': '42'}
        ]
    ),
    (
        'count;product;shelf\n'
        '123;10,4;cool shelf\n'
        '333;11;успешная',
        [
            {'count': 123, 'shelf': 'cool shelf', 'product': '10,4'},
            {'count': 333, 'shelf': 'успешная', 'product': '11'}
        ]
    ),
    (
        'shelf;product;count',
        []
    ),
    (
        '',
        []
    )
])
async def test_order_signal(tap, api, dataset, rows, expected_rows):
    with tap.plan(7, 'Успешная загрузка'):
        order = await dataset.order(
            type='inventory_check_more',
            vars={'third_party_assistance': True}
        )
        user = await dataset.user(role='admin', store_id=order.store_id)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_import_report',
            json={
                'csv': rows,
                'order_id': order.order_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await order.reload(), 'перезабрали')
        signal = order.signals[0]
        tap.eq(signal.type, 'inventory_report_imported', 'тип сигнала верен')

        stash = await Stash.load(
            f'inventory_report-{order.order_id}',
            by='name'
        )
        tap.ok(stash, 'сохранили')
        tap.eq(
            stash.value('rows'),
            expected_rows,
            'строки правильные'
        )


@pytest.mark.parametrize('csv, expected_message', [
    ('shelf,product\n1,2', 'Required fields are not found:count'),
    ('shelf,product,count\n1,2,a', 'CSV has invalid rows #:1'),
    (
        'count,product,shelf,field\n1,0,0,0\n1,0,,0\n',
        'CSV has invalid rows #:2'
    ),
    (
        'count,product,shelf,field\n1,,0,0\n1,,,0\n',
        'CSV has invalid rows #:1,2'
    ),
])
async def test_invalid_csv(tap, api, dataset, csv, expected_message):
    with tap.plan(4, 'Некорректный CSV'):
        order = await dataset.order(
            type='inventory_check_product_on_shelf',
            vars={'third_party_assistance': True}
        )
        user = await dataset.user(role='admin', store_id=order.store_id)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_import_report',
            json={
                'csv': csv,
                'order_id': order.order_id,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', expected_message)


async def test_report_processed(tap, api, uuid, make_csv_str, dataset):
    with tap.plan(7, 'Повторная отправка'):
        order = await dataset.order(
            type='inventory_check_more',
            vars={'third_party_assistance': True}
        )
        user = await dataset.user(role='admin', store_id=order.store_id)

        t = await api(user=user)

        rows = [
            {
                'shelf': uuid(),
                'product': uuid(),
                'count': random.randint(0, 15),
            }
        ]
        csv_str = make_csv_str(
            ['shelf', 'product', 'count'],
            rows,
        )
        await t.post_ok(
            'api_disp_orders_import_report',
            json={
                'csv': csv_str,
                'order_id': order.order_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_disp_orders_import_report',
            json={
                'csv': csv_str,
                'order_id': order.order_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Unprocessed report remains')


@pytest.mark.parametrize('order_params', [
    {
        'type': 'inventory_check_more',
        'vars': {'third_party_assistance': False},
    },
    {
        'type': 'inventory',
        'vars': {'third_party_assistance': True},
    },
    {
        'type': 'order',
        'vars': {},
    },
    {
        'type': 'inventory_check_more',
        'vars': {'third_party_assistance': True},
        'status': 'failed',
    },
])
async def test_invalid_order(
        tap, api, uuid, make_csv_str, dataset, order_params):
    with tap.plan(4, 'Некорректный ордер'):
        order = await dataset.order(**order_params)
        user = await dataset.user(role='admin', store_id=order.store_id)

        t = await api(user=user)

        rows = [
            {
                'shelf': uuid(),
                'product': uuid(),
                'count': random.randint(0, 15),
            }
        ]
        csv_str = make_csv_str(
            ['shelf', 'product', 'count'],
            rows,
        )
        await t.post_ok(
            'api_disp_orders_import_report',
            json={
                'csv': csv_str,
                'order_id': order.order_id,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Unsupported order')
