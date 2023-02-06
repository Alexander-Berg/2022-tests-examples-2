import json

from . import headers
from . import models


async def test_basic(taxi_grocery_orders, pgsql):
    order = models.Order(
        pgsql=pgsql,
        entrance='entrance',
        postal_code='postal_code',
        delivery_common_comment='delivery_common_comment',
    )

    auth_context_headers = {**headers.DEFAULT_HEADERS}
    auth_context_headers.pop('X-Idempotency-Token')
    auth_context_raw = {'headers': auth_context_headers}
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps(auth_context_raw),
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/takeout/load', json={'order_id': order.order_id},
    )

    expected_data = {
        'short_order_id': order.short_order_id,
        'cart_id': order.cart_id,
        'location': order.location_as_point(),
        'country': order.country,
        'city': order.city,
        'street': order.street,
        'house': order.house,
        'flat': order.flat,
        'floor': order.floor,
        'place_id': order.place_id,
        'doorcode': order.doorcode,
        'doorcode_extra': order.doorcode_extra,
        'building_name': order.building_name,
        'doorbell_name': order.doorbell_name,
        'left_at_door': order.left_at_door,
        'meet_outside': order.meet_outside,
        'no_door_call': order.no_door_call,
        'postal_code': order.postal_code,
        'delivery_common_comment': order.delivery_common_comment,
        'entrance': order.entrance,
        'user_ip': order.user_ip,
        'user_agent': order.user_agent,
    }
    expected_sensitive_data = {
        'yandex_uid': order.yandex_uid,
        'personal_phone_id': order.personal_phone_id,
        'phone_id': order.phone_id,
        'taxi_user_id': order.taxi_user_id,
        'eater_id': order.eats_user_id,
        'appmetrica_device_id': order.appmetrica_device_id,
        'user_ip': order.user_ip,
        'taxi_session': order.session,
        'bound_taxi_sessions': order.bound_sessions,
        'extra_data': {
            'user_info': order.user_info,
            'auth_context': auth_context_raw,
        },
    }

    assert response.status_code == 200
    assert response.json() == {
        'objects': [
            {
                'id': order.order_id,
                'data': expected_data,
                'sensitive_data': expected_sensitive_data,
            },
        ],
    }


async def test_404(taxi_grocery_orders):
    response = await taxi_grocery_orders.post(
        '/internal/v1/takeout/load', json={'order_id': 'unknown'},
    )

    assert response.status_code == 404
