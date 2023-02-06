import datetime
import uuid

import pytest

from tests_grocery_discounts import common


def _check_db(expected: list, schema_name: str, pgsql):
    pg_cursor = pgsql[schema_name].cursor()
    columns = [
        'order_id',
        'yandex_uid',
        'series_id',
        'created_at',
        'cancelled_at',
    ]
    str_columns = ','.join(columns)
    pg_cursor.execute(
        f'SELECT {str_columns} FROM {schema_name}.discount_usages',
    )
    result = [dict(zip(columns, item)) for item in pg_cursor.fetchall()]
    assert sorted(result, key=lambda x: x['series_id']) == sorted(
        expected, key=lambda x: x['series_id'],
    )


def _shift_time(time: str) -> str:
    return (
        datetime.datetime.strptime(time, common.DATETIME_FORMAT)
        + datetime.timedelta(days=1)
    ).strftime(common.DATETIME_FORMAT)


@pytest.mark.pgsql('grocery_discounts', files=['init_discounts_db.sql'])
async def test_stq_discounts_usages(
        stq_runner, pgsql, service_name, mocked_time,
):
    number_of_calls = 2
    order_id = 'test_order_id'
    yandex_uid = 100500
    discount_ids = {'1', '2', '3', '4'}
    add_time_str = '2020-02-01T09:00:01+00:00'
    kwargs = {
        'order_id': order_id,
        'discount_ids': discount_ids,
        'yandex_uid': yandex_uid,
        'add_time': add_time_str,
    }

    for _ in range(number_of_calls):
        await stq_runner.grocery_discounts_discount_usage_add.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
        kwargs['add_time'] = _shift_time(kwargs['add_time'])

    add_time = datetime.datetime.strptime(add_time_str, common.DATETIME_FORMAT)
    expected = [
        {
            'created_at': add_time,
            'cancelled_at': None,
            'series_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'order_id': order_id,
            'yandex_uid': yandex_uid,
        },
        {
            'created_at': add_time,
            'cancelled_at': None,
            'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'order_id': order_id,
            'yandex_uid': yandex_uid,
        },
    ]
    _check_db(expected, service_name, pgsql)

    cancel_time_str = kwargs['add_time']

    kwargs = {
        'order_id': order_id,
        'yandex_uid': yandex_uid,
        'cancel_time': cancel_time_str,
    }

    for _ in range(number_of_calls):
        await stq_runner.grocery_discounts_discount_usage_cancel.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
        kwargs['cancel_time'] = _shift_time(kwargs['cancel_time'])

    cancel_time = datetime.datetime.strptime(
        cancel_time_str, common.DATETIME_FORMAT,
    )
    expected = [
        {
            'created_at': add_time,
            'cancelled_at': cancel_time,
            'series_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'order_id': order_id,
            'yandex_uid': yandex_uid,
        },
        {
            'created_at': add_time,
            'cancelled_at': cancel_time,
            'series_id': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'order_id': order_id,
            'yandex_uid': yandex_uid,
        },
    ]

    _check_db(expected, service_name, pgsql)

    kwargs = {
        'order_id': order_id,
        'discount_ids': discount_ids,
        'yandex_uid': yandex_uid,
        'add_time': kwargs['cancel_time'],
    }

    for _ in range(number_of_calls):
        await stq_runner.grocery_discounts_discount_usage_add.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )
        kwargs['add_time'] = _shift_time(kwargs['add_time'])

    _check_db(expected, service_name, pgsql)
