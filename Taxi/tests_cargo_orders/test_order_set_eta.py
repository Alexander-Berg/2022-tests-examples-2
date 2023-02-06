import datetime

import psycopg2


def build_request(order_id):
    return {
        'cargo_order_id': order_id,
        'performer_info': {
            'park_id': 'park_id1',
            'driver_id': 'driver_id1',
            'tariff_class': 'cargo',
        },
        'first_point_eta': {
            'arrive_time': '2020-07-20T11:08:00+00:00',
            'route_distance': 888.88,
        },
    }


async def test_basic(taxi_cargo_orders, default_order_id, fetch_performer):
    response = await taxi_cargo_orders.post(
        'v1/order/set-eta', json=build_request(default_order_id),
    )
    assert response.status_code == 200

    performer = fetch_performer(default_order_id)

    assert performer.dist_from_point_a == 889
    assert performer.eta_to_point_a == datetime.datetime(
        2020,
        7,
        20,
        14,
        8,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    )
