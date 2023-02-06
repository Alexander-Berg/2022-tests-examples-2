import pytest

from . import experiments
from . import models

NOW = '2020-03-13T07:19:13+00:00'
TWO_WEEKS_AFTER_NOW = '2020-03-27T07:19:13+00:00'
THREE_WEEKS_AFTER_NOW = '2020-04-03T07:19:13+00:00'

GROCERY_COMPENSATION_PROMOCODE_LIFETIME_CONFIG = pytest.mark.experiments3(
    name='grocery_compensation_promocode_lifetime',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled = default',
            'predicate': {'type': 'true'},
            'value': {'fixed': {'days': 14}, 'percent': {'days': 21}},
        },
    ],
    is_config=True,
)


@pytest.mark.parametrize(
    'url, has_response',
    [
        ('/admin/orders/v1/promocode/generate', True),
        ('/processing/v1/compensation/promocode', False),
    ],
)
@pytest.mark.now(NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
@GROCERY_COMPENSATION_PROMOCODE_LIFETIME_CONFIG
@pytest.mark.parametrize(
    'promocode_type,promocode_value,promocode_series',
    [
        ('fixed', 50, 'FIXED_SERIES_100'),
        ('fixed', 100, 'FIXED_SERIES_100'),
        ('fixed', 200, 'FIXED_SERIES_300'),
        ('percent', None, 'PERCENT_SERIES'),
        ('percent', 10, 'PERCENT_SERIES_10'),
        ('percent', 20, 'PERCENT_SERIES_20'),
        ('percent', 500, 'PERCENT_SERIES'),
    ],
)
async def test_basic_promo(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        promocode_type,
        promocode_value,
        promocode_series,
        processing,
        url,
        has_response,
):
    phone_id = 'ndajkscs'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    if promocode_type == 'percent':
        if promocode_value is None:
            token = f'{order.order_id}-percent'
        else:
            token = f'{order.order_id}-percent-{promocode_value}'
    else:
        token = f'{order.order_id}-fixed-{promocode_value}'

    coupons.check_request(
        phone_id=phone_id,
        yandex_uid=yandex_uid,
        series_id=promocode_series,
        token=token,
        value=promocode_value if promocode_type == 'fixed' else None,
        expire_at=TWO_WEEKS_AFTER_NOW
        if promocode_type == 'fixed'
        else THREE_WEEKS_AFTER_NOW,
    )

    request_json = {
        'order_id': order.order_id,
        'promocode_type': promocode_type,
    }
    if promocode_value:
        request_json['promocode_value'] = promocode_value

    response = await taxi_grocery_orders.post(url, json=request_json)

    assert response.status == 200
    order.check_order_history(
        'admin_action',
        {'to_action_type': 'promocode', 'status': 'success', 'admin_info': {}},
    )
    if has_response:
        assert response.json()['promocode'] == 'SOME_PROMOCODE'

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_notification'
    assert event.payload['code'] == 'compensation'


@pytest.mark.parametrize(
    'url',
    [
        '/admin/orders/v1/promocode/generate',
        '/processing/v1/compensation/promocode',
    ],
)
@experiments.LAVKA_PROMOCODE_CONFIG
async def test_no_series(
        taxi_grocery_orders, pgsql, grocery_cart, grocery_depots, url,
):
    promocode_type = 'fixed'
    promocode_value = 500

    phone_id = 'ndajkscs'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'

    order = models.Order(
        pgsql=pgsql,
        phone_id=phone_id,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    request_json = {
        'order_id': order.order_id,
        'promocode_type': promocode_type,
        'promocode_value': promocode_value,
    }

    response = await taxi_grocery_orders.post(url, json=request_json)
    assert response.status == 400
    order.update()
    order.check_order_history(
        'admin_action',
        {'to_action_type': 'promocode', 'status': 'fail', 'admin_info': {}},
    )


@pytest.mark.parametrize(
    'url',
    [
        '/admin/orders/v1/promocode/generate',
        '/processing/v1/compensation/promocode',
    ],
)
@pytest.mark.parametrize(
    'order_flow', ['tristero_flow_v2', 'tristero_no_auth_flow_v1'],
)
async def test_no_auth_context(taxi_grocery_orders, pgsql, order_flow, url):
    order = models.Order(pgsql=pgsql, grocery_flow_version=order_flow)

    response = await taxi_grocery_orders.post(
        url, json={'order_id': order.order_id},
    )

    assert response.status == 400


@pytest.mark.now(NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
@pytest.mark.parametrize(
    'url',
    [
        '/admin/orders/v1/promocode/generate',
        '/processing/v1/compensation/promocode',
    ],
)
async def test_new_flow(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        processing,
        url,
):
    promocode_type = 'percent'
    promocode_value = 1337
    promocode_series = 'FARADAY_SERIES'
    personal_phone_id = 'azsa'
    yandex_uid = '1232146712'

    order = models.Order(
        pgsql=pgsql,
        phone_id=None,
        personal_phone_id=personal_phone_id,
        yandex_uid=yandex_uid,
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    coupons.check_request(
        phone_id=None, yandex_uid=yandex_uid, series_id=promocode_series,
    )

    request_json = {
        'order_id': order.order_id,
        'promocode_type': promocode_type,
        'promocode_value': promocode_value,
    }

    response = await taxi_grocery_orders.post(url, json=request_json)
    assert response.status == 200

    order.check_order_history(
        'admin_action',
        {'to_action_type': 'promocode', 'status': 'success', 'admin_info': {}},
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[0]
    assert event.payload['order_id'] == order.order_id
    assert event.payload['reason'] == 'order_notification'
    assert event.payload['code'] == 'compensation'


@pytest.mark.now(NOW)
@experiments.LAVKA_PROMOCODE_CONFIG
async def test_numeric_promocode_value(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        coupons,
        grocery_depots,
        processing,
):
    promocode_type = 'fixed'
    promocode_value = 151
    promocode_value_numeric = '150.1902'
    promocode_series = 'FIXED_SERIES_300'
    phone_id = 'azsa'
    yandex_uid = '1232146712'

    order = models.Order(pgsql=pgsql, phone_id=phone_id, yandex_uid=yandex_uid)
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    coupons.check_request(
        phone_id=phone_id,
        yandex_uid=yandex_uid,
        series_id=promocode_series,
        value=promocode_value,
        value_numeric=promocode_value_numeric,
    )

    request_json = {
        'order_id': order.order_id,
        'promocode_type': promocode_type,
        'promocode_value': promocode_value,
        'promocode_value_numeric': promocode_value_numeric,
    }

    response = await taxi_grocery_orders.post(
        '/admin/orders/v1/promocode/generate', json=request_json,
    )
    assert response.status == 200

    order.check_order_history(
        'admin_action',
        {'to_action_type': 'promocode', 'status': 'success', 'admin_info': {}},
    )
