import json

from . import headers
from . import models


async def test_basic(taxi_grocery_orders, pgsql):
    anonym_id = 'anonym_id'

    order = models.Order(
        pgsql=pgsql,
        yandex_uid='yandex_uid',
        personal_phone_id='personal_phone_id',
        phone_id='phone_id',
        taxi_user_id='taxi_user_id',
        eats_user_id='eats_user_id',
        user_ip='user_ip',
        session='session',
        bound_sessions=['session'],
        user_info='user_info',
        appmetrica_device_id='appmetrica_device_id',
    )
    order_auth_context = models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/takeout/delete',
        json={'order_id': order.order_id, 'anonym_id': anonym_id},
    )

    assert response.status_code == 200

    order.update()
    assert order.anonym_id == anonym_id
    assert order.yandex_uid is None
    assert order.personal_phone_id is None
    assert order.phone_id is None
    assert order.taxi_user_id == ''
    assert order.eats_user_id == ''
    assert order.user_ip is None
    assert order.session is None
    assert order.bound_sessions is None
    assert order.user_info == ''
    assert order.appmetrica_device_id is None

    order_auth_context.update()
    assert order_auth_context.raw_auth_context is None


async def test_404(taxi_grocery_orders):
    response = await taxi_grocery_orders.post(
        '/internal/v1/takeout/delete',
        json={'order_id': 'unknown', 'anonym_id': 'anonym_id'},
    )

    assert response.status_code == 404
