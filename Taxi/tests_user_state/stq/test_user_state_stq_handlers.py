import pytest

DB_NAME = 'user_state'

GET_UPGRADED_CLASS_ORDER_BY_ID_SQL = """
SELECT
  order_id,
  upgraded_to,
  yandex_uid,
  zone_name,
  brand,
  is_completed
FROM user_state.upgraded_class_orders
WHERE order_id = '{order_id}'
;
"""

DEFAULT_TASK_KWARGS = {
    'order_id': 'some_order_id',
    'upgraded_to': 'vip',
    'yandex_uid': 'test_yandex_uid',
    'zone_name': 'moscow',
    'brand': 'yataxi',
}


def get_order(pgsql, order_id):
    db = pgsql[DB_NAME].cursor()
    query = GET_UPGRADED_CLASS_ORDER_BY_ID_SQL.format(order_id=order_id)
    db.execute(query)
    rows = [row for row in db]

    if rows:
        fields = [column.name for column in db.description]
        return dict(zip(fields, rows[0]))

    return None


@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_ok(stq_runner, pgsql):
    task_kwargs = DEFAULT_TASK_KWARGS

    await stq_runner.user_state_handle_class_upgraded.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    row = get_order(pgsql, task_kwargs['order_id'])
    expected_row = task_kwargs
    expected_row['is_completed'] = False
    assert row == expected_row


@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_already_exists(stq_runner, pgsql):
    order_id = 'already_existing_order_id'

    task_kwargs = {**DEFAULT_TASK_KWARGS, **{'order_id': order_id}}

    order_before = get_order(pgsql, order_id)

    await stq_runner.user_state_handle_class_upgraded.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    order_after = get_order(pgsql, order_id)

    assert order_after == order_before


@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_order_status_completed(stq_runner, pgsql):
    order_id = 'already_existing_order_id'
    task_kwargs = {**DEFAULT_TASK_KWARGS, **{'order_id': order_id}}

    await stq_runner.user_state_handle_order_completed.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    order_after = get_order(pgsql, order_id)

    assert order_after['is_completed']
