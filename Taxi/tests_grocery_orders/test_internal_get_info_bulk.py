import datetime

import pytest

from . import consts
from . import models

NOW = datetime.datetime.now(tz=consts.UTC_TZ)
TIMESLOT_START = '2020-03-13T09:50:00+00:00'
TIMESLOT_END = '2020-03-13T17:50:00+00:00'
TIMESLOT_REQUEST_KIND = 'wide_slot'


@pytest.mark.parametrize(
    'read_from_pg, skip_cache', [(True, False), (False, True)],
)
async def test_basic(
        taxi_grocery_orders,
        taxi_config,
        pgsql,
        grocery_depots,
        read_from_pg,
        skip_cache,
):
    taxi_config.set(GROCERY_ORDERS_READ_ORDERS_BULK_FROM_SLAVE=read_from_pg)
    order = models.Order(pgsql=pgsql, created=NOW, location='(10.0, 20.0)')
    grocery_depots.add_depot(
        legacy_depot_id=order.depot_id, country_iso3='RUS',
    )
    await taxi_grocery_orders.invalidate_caches()

    # add order that is not in cache
    not_in_cache_order = models.Order(
        pgsql=pgsql,
        created=NOW,
        location='(30.0, 40.0)',
        timeslot_start=TIMESLOT_START,
        timeslot_end=TIMESLOT_END,
        timeslot_request_kind=TIMESLOT_REQUEST_KIND,
        depot_id='2392',
    )
    grocery_depots.add_depot(
        legacy_depot_id=not_in_cache_order.depot_id, country_iso3='ISR',
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-info-bulk',
        json={
            'order_ids': [
                order.order_id,
                'unknown_order_id',
                not_in_cache_order.order_id,
            ],
            'skip_cache': skip_cache,
        },
    )

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 2

    actual_order = json[0]
    assert order.order_id == actual_order['order_id']
    assert {'lat': 20.0, 'lon': 10.0} == actual_order['location']
    assert order.status == actual_order['status']
    assert order.cart_id == actual_order['cart_id']
    assert order.personal_phone_id == actual_order['personal_phone_id']
    assert actual_order['country_iso3'] == 'RUS'
    assert order.depot_id == actual_order['depot_id']

    actual_order = json[1]
    assert not_in_cache_order.order_id == actual_order['order_id']
    assert {'lat': 40.0, 'lon': 30.0} == actual_order['location']
    assert not_in_cache_order.status == actual_order['status']
    assert not_in_cache_order.cart_id == actual_order['cart_id']
    assert (
        not_in_cache_order.timeslot_start == actual_order['timeslot']['start']
    )
    assert not_in_cache_order.timeslot_end == actual_order['timeslot']['end']
    assert (
        not_in_cache_order.timeslot_request_kind
        == actual_order['request_kind']
    )
    assert (
        not_in_cache_order.personal_phone_id
        == actual_order['personal_phone_id']
    )
    assert 'country_iso3' not in actual_order  # no depot because no cache
    assert not_in_cache_order.depot_id == actual_order['depot_id']
