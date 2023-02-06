import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

DEPOT_ID = '0'


@pytest.mark.now(keys.TS_NOW)
@common.GROCERY_ORDER_CYCLE_ENABLED
async def test_basic(
        taxi_grocery_cart, cart, overlord_catalog, tristero_parcels,
):
    item_id = 'item_id_1'
    parcel_id = 'parcel_id:st-pa'
    price = '123.12'

    overlord_catalog.add_product(product_id=item_id, price=price)
    tristero_parcels.add_parcel(parcel_id=parcel_id)

    await cart.modify(
        {item_id: {'q': '1', 'p': price}, parcel_id: {'q': '1', 'p': '0'}},
        currency='RUB',
    )
    cart.update_db(
        timeslot_start='2020-03-13T09:50:00+00:00',
        timeslot_end='2020-03-13T17:50:00+00:00',
        timeslot_request_kind='wide_slot',
    )
    await cart.checkout()
    await taxi_grocery_cart.invalidate_caches()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/retrieve/by-depot',
        json={'depot_id': DEPOT_ID},
        headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert items[0]['cart_id'] == cart.cart_id
    assert items[0]['cart_version'] == 1
    assert items[0]['items'][1]['id'] == parcel_id
    assert items[0]['timeslot'] == {
        'end': '2020-03-13T17:50:00+00:00',
        'start': '2020-03-13T09:50:00+00:00',
    }
    assert items[0]['request_kind'] == 'wide_slot'
