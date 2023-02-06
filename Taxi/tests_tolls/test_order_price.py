import datetime
import decimal

import pytest

ORDER_ID = '00234567890123456789abcdefGHIJKLMN'
OFFER_ID = '10234567890123456789abcdefGHIJKLMN'
CAN_SWITCH_ROAD = True
PRICE = 250.00
OLD_PRICE = 200.00
OLD_DRIVER_COST = 300.00

DATETIME = datetime.datetime(2020, 1, 2, 3, 4, 5, 1, datetime.timezone.utc)


@pytest.mark.filldb(orders='price')
@pytest.mark.experiments3(filename='conf3_toll_roads_price_limits.json')
async def test_order_price(taxi_tolls, db_toll_roads, mongodb):
    db_toll_roads.save_order(
        ORDER_ID,
        DATETIME,
        CAN_SWITCH_ROAD,
        OFFER_ID,
        True,
        price=None,
        point_a='37.0,55.0',
        point_b='37.5,55.5',
    )
    db_toll_roads.save_log(ORDER_ID, DATETIME, True)

    request = {
        'order_id': ORDER_ID,
        'price': PRICE,
        'old_price': OLD_PRICE,
        'old_driver_cost': OLD_DRIVER_COST,
        'calc_method': 'other',
        'reason': 'support',
    }

    response = await taxi_tolls.post('/tolls/v1/order/price', json=request)

    assert response.status == 200
    order = db_toll_roads.get_order_price(ORDER_ID)
    assert order['price'] == decimal.Decimal(PRICE)
    updated_doc = mongodb.orders.find_one({'_id': ORDER_ID})
    assert (
        updated_doc['driver_cost']['cost']
        == OLD_DRIVER_COST + PRICE - OLD_PRICE
    )
    assert updated_doc['driver_cost']['calc_method'] == 'other'
    assert updated_doc['driver_cost']['reason'] == 'support'
