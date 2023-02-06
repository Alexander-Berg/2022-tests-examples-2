import json

from . import consts
from . import headers
from . import models

CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
LOCATION_IN_RUSSIA = [37, 55]
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
DOORCODE = '42'
DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'
LEFT_AT_DOOR = False
COMMENT = 'comment'
DEPOT_ID = '2809'
ENTRANCE = '3333'
PROCESSING_FLOW_VERSION = 'grocery_flow_v1'

SUBMIT_BODY = {
    'cart_id': CART_ID,
    'cart_version': CART_VERSION,
    'offer_id': OFFER_ID,
    'position': {
        'location': LOCATION_IN_RUSSIA,
        'place_id': PLACE_ID,
        'floor': FLOOR,
        'flat': FLAT,
        'doorcode': DOORCODE,
        'doorcode_extra': DOORCODE_EXTRA,
        'building_name': BUILDING_NAME,
        'doorbell_name': DOORBELL_NAME,
        'left_at_door': LEFT_AT_DOOR,
        'comment': COMMENT,
        'entrance': ENTRANCE,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
}


async def test_raw_auth_context(
        taxi_grocery_orders, grocery_cart, grocery_depots, pgsql,
):
    grocery_cart.set_payment_method({'type': 'card', 'id': 'id'})
    grocery_depots.add_depot(
        legacy_depot_id=DEPOT_ID,
        country_iso3=models.Country.Russia.country_iso3,
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v2/submit',
        json=SUBMIT_BODY,
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    auth_context = models.OrderAuthContext(
        pgsql, order_id=response.json()['order_id'], insert_in_pg=False,
    )
    auth_context.update()

    assert json.loads(auth_context.raw_auth_context) == consts.AUTH_CONTEXT
