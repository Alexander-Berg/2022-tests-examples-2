import datetime

import pytest

ORDER_ID = '00234567890123456789abcdefGHIJKLMN'
OFFER_ID = '10234567890123456789abcdefGHIJKLMN'
DATETIME = datetime.datetime(2020, 1, 2, 3, 4, 5, 1, datetime.timezone.utc)


@pytest.mark.parametrize('order_exists', [False, True])
@pytest.mark.parametrize('log_exists', [False, True])
@pytest.mark.parametrize('can_switch_road', [False, True])
@pytest.mark.parametrize('has_toll_road', [False, True])
@pytest.mark.parametrize('auto_payment', [False, True])
@pytest.mark.parametrize('price', ['250', None])
async def test_order_retrieve(
        taxi_tolls,
        db_toll_roads,
        order_exists,
        log_exists,
        can_switch_road,
        has_toll_road,
        auto_payment,
        price,
):
    if order_exists:
        db_toll_roads.save_order(
            ORDER_ID,
            DATETIME,
            can_switch_road,
            OFFER_ID,
            auto_payment,
            price=price,
            point_a=None,
            point_b=None,
        )
    if order_exists and log_exists:
        db_toll_roads.save_log(ORDER_ID, DATETIME, not has_toll_road)
        db_toll_roads.save_log(
            ORDER_ID,
            DATETIME + datetime.timedelta(microseconds=1),
            has_toll_road,
        )

    response = await taxi_tolls.post(
        '/tolls/v1/order/retrieve', json={'order_id': ORDER_ID},
    )

    assert response.status == 200
    json = response.json()
    has_all_db_records = order_exists and log_exists
    expected_json = {
        'visible': has_all_db_records,
        'can_switch_road': has_all_db_records and can_switch_road,
        'has_toll_road': has_all_db_records and has_toll_road,
        'auto_payment': has_all_db_records and auto_payment,
    }
    if has_all_db_records:
        expected_json['cost'] = {}
        if price:
            expected_json['cost']['price'] = price
    assert json == expected_json


@pytest.mark.experiments3(filename='conf3_toll_roads_price_limits.json')
@pytest.mark.parametrize(
    'point_a, point_b, falls_inside',
    [
        pytest.param(
            ['39.0', '58.0'], ['35.0', '53.0'], False, id='both_points_out',
        ),
        pytest.param(
            ['37.0', '55.0'], ['37.5', '55.5'], True, id='both_points_in',
        ),
        pytest.param(
            ['35.0', '53.0'], ['37.0', '55.0'], False, id='point_a_out',
        ),
        pytest.param(
            ['37.0', '55.0'], ['39.0', '57.0'], False, id='point_b_out',
        ),
    ],
)
async def test_order_retrieve_limits(
        taxi_tolls, db_toll_roads, point_a, point_b, falls_inside,
):
    can_switch_road = True
    has_toll_road = True
    auto_payment = True
    db_toll_roads.save_order(
        ORDER_ID,
        DATETIME,
        can_switch_road,
        OFFER_ID,
        auto_payment,
        price=None,
        point_a=','.join(point_a),
        point_b=','.join(point_b),
    )
    db_toll_roads.save_log(ORDER_ID, DATETIME, not has_toll_road)

    response = await taxi_tolls.post(
        '/tolls/v1/order/retrieve', json={'order_id': ORDER_ID},
    )
    assert response.status == 200
    json = response.json()
    if falls_inside:
        assert json['cost'] == {'limits': {'min': '100', 'max': '900'}}
    else:
        assert json['cost'] == {}
