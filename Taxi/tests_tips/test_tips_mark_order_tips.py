import datetime

import pytest


@pytest.mark.pgsql(
    'tips',
    queries=[
        'INSERT INTO tips.tips (id, updated_at) '
        'VALUES (\'existing_order_id\', \'2020-11-24T12:00:00\')',
    ],
)
@pytest.mark.parametrize(
    ['order_id'],
    [
        pytest.param('existing_order_id'),
        pytest.param('existing_order_id_2', id='Order not in tips db'),
    ],
)
@pytest.mark.now('2020-11-24T12:00:00Z')
async def test_tips_db(stq_runner, tips_postgres_db, order_id: str):

    await stq_runner.tips_mark_order_tips.call(
        task_id=order_id, args=[order_id],
    )

    tips_postgres_db.execute(
        'SELECT id, updated_at '
        'FROM tips.tips '
        f'WHERE id = \'{order_id}\'',
    )
    orders = list(row for row in tips_postgres_db)
    assert len(orders) == 1
    db_order_id, db_updated_at = orders[0]
    assert db_order_id == order_id
    # checking against old row in db, since mock.now doesnt work for postgres
    assert db_updated_at > datetime.datetime.fromisoformat(
        '2020-11-24T12:00:00',
    )
