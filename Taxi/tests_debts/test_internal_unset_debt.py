import bson
import pytest


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'order_id,ans_count_order', [('order_id_5', 0), ('order_id_6', 1)],
)
@pytest.mark.filldb
async def test_debts(order_id, ans_count_order, pgsql, debts_client):
    code = await debts_client.unset_debt_light(order_id=order_id)
    assert code == 200

    cursor = pgsql['debts'].cursor()
    cursor.execute(
        'SELECT * from debts.taxi_order_debts where order_id = \'{}\''.format(
            order_id,
        ),
    )
    result = list(row[0] for row in cursor)
    assert len(result) == ans_count_order


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'order_id,ans_lock_orders',
    [
        ('order_id_5', ['order_id_6', 'order_id_7']),
        ('order_id_6', ['order_id_5', 'order_id_6', 'order_id_7']),
    ],
)
@pytest.mark.filldb
async def test_cardlocks(order_id, ans_lock_orders, mongodb, debts_client):
    code = await debts_client.unset_debt_light(order_id=order_id)
    assert code == 200

    assert (
        mongodb.cardlocks.find_one({'i': '89898989898989898989898989898989'})[
            'x'
        ]
        == ans_lock_orders
    )


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'order_id,ans_lock_orders',
    [('order_id_5', []), ('order_id_6', ['order_id_5', 'order_id_5'])],
)
@pytest.mark.filldb
async def test_phonelocks(order_id, ans_lock_orders, mongodb, debts_client):
    code = await debts_client.unset_debt_light(order_id=order_id)
    assert code == 200

    assert (
        mongodb.phonelocks.find_one(
            {'i': bson.ObjectId('787878787878787878787878')},
        )['x']
        == ans_lock_orders
    )


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'order_id,ans_lock_orders',
    [
        ('order_id_5', ['order_id_6', 'order_id_7']),
        ('order_id_6', ['order_id_5', 'order_id_6', 'order_id_7']),
    ],
)
@pytest.mark.filldb
async def test_devicelocks(order_id, ans_lock_orders, mongodb, debts_client):
    code = await debts_client.unset_debt_light(order_id=order_id)
    assert code == 200

    assert (
        mongodb.devicelocks.find_one(
            {'i': '89898989898989898989898989898989'},
        )['x']
        == ans_lock_orders
    )
