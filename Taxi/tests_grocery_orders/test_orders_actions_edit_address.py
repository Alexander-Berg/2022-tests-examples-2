import json

import pytest

from . import experiments
from . import models


DEFAULT_LOCATION = (37.601295, 55.585286)


@pytest.mark.parametrize(
    'dispatch_status, dispatch_delivery_type, location, house,'
    'dispatch_error_code, is_bad_address, result_code',
    [
        (
            'accepted',
            None,
            (37.601295, 55.585286),
            'order_building',
            None,
            False,
            200,
        ),
        ('accepted', None, (37, 55), 'order_building', None, False, 400),
        (
            'accepted',
            None,
            (37.601295, 55.585286),
            'order_building',
            None,
            True,
            404,
        ),
        (
            'delivering',
            None,
            (37.601295, 55.585286),
            'order_building',
            None,
            False,
            405,
        ),
        (
            'accepted',
            'courier',
            (37.601295, 55.585286),
            'order_building',
            None,
            False,
            200,
        ),
        (
            'accepted',
            'yandex_taxi',
            (37.601295, 55.585286),
            'order_building',
            None,
            False,
            405,
        ),
        (
            'accepted',
            None,
            (37.601295, 55.585286),
            'order_building',
            500,
            False,
            500,
        ),
        (
            None,
            None,
            (37.601295, 55.585286),
            'order_building',
            None,
            False,
            500,
        ),
        ('accepted', None, (37.601295, 55.585286), '100', None, False, 400),
        ('accepted', None, (37.601295, 55.585286), None, None, False, 400),
    ],
)
@experiments.EDIT_ADDRESS
@experiments.CORRECT_INFO
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        yamaps_local,
        dispatch_status,
        dispatch_delivery_type,
        location,
        house,
        dispatch_error_code,
        is_bad_address,
        result_code,
):
    dispatch_id = '01234567-89ab-cdef-0123-456789abcdef'
    if dispatch_status:
        dispatch_status_info = models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status=dispatch_status,
            dispatch_cargo_status='new',
        )
    else:
        dispatch_status_info = models.DispatchStatusInfo()
    if dispatch_delivery_type is not None:
        dispatch_status_info.dispatch_status_meta = {
            'cargo_dispatch': {
                'dispatch_delivery_type': dispatch_delivery_type,
            },
        }
    order = models.Order(
        pgsql=pgsql,
        dispatch_status_info=dispatch_status_info,
        dispatch_flow='grocery_dispatch',
        location=str(location),
        entrance='',
        comment='',
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_zone_type('pedestrian')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)
    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        order_id=order.order_id,
        status='delivered',
        street=order.street,
        building=house or order.house,
        flat=order.flat,
        door_code=order.doorcode,
        porch=order.entrance,
        floor=order.floor,
        comment=order.comment,
        location={'lon': location[0], 'lat': location[1]},
        edit_error_code=dispatch_error_code,
    )
    yamaps_local.set_data(is_empty_response=is_bad_address)

    request = {
        'order_id': order.order_id,
        'house': house,
        'street': order.street,
    }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/edit/address', json=request,
    )

    assert response.status == result_code

    if result_code == 400:
        return

    if (
            not dispatch_status == 'accepted'
            or dispatch_delivery_type == 'yandex_taxi'
    ):
        assert yamaps_local.times_called() == 0
    else:
        assert yamaps_local.times_called() == 1

    if result_code == 200 and dispatch_status == 'accepted':
        assert grocery_dispatch.times_edit_called() == 1
        order.check_order_history(
            'edit_address',
            {
                'old_address': (
                    f'{order.street}, {order.house}, {order.flat}, '
                    f'{order.doorcode}, {order.entrance}, '
                    f'{order.floor}, {order.comment}'
                ),
                'new_address': (
                    f'{order.street}, {house or order.house}, {order.flat}, '
                    f'{order.doorcode}, {order.entrance}, '
                    f'{order.floor}, {order.comment}'
                ),
            },
        )

        order.update()
        if house:
            assert order.house == house
    elif dispatch_error_code is None:
        assert grocery_dispatch.times_edit_called() == 0


@pytest.mark.parametrize(
    'orders_count, is_fraud, depot_id, result_code, edit_house',
    [
        (0, False, models.DEFAULT_DEPOT_ID, 200, False),
        (5, False, models.DEFAULT_DEPOT_ID, 200, False),
        (0, True, models.DEFAULT_DEPOT_ID, 405, False),
        (5, False, models.DEFAULT_DEPOT_ID, 200, False),
        (5, False, None, 500, False),
        (0, True, models.DEFAULT_DEPOT_ID, 400, True),
        (5, False, models.DEFAULT_DEPOT_ID, 400, True),
        (5, False, None, 500, True),
    ],
)
@experiments.EDIT_ADDRESS
@experiments.CORRECT_INFO
@experiments.antifraud_check_experiment(enabled=True)
async def test_check_newbie_antifraud(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_dispatch,
        grocery_depots,
        grocery_marketing,
        antifraud,
        yamaps_local,
        orders_count,
        is_fraud,
        depot_id,
        result_code,
        edit_house,
):
    dispatch_id = '01234567-89ab-cdef-0123-456789abcdef'
    house = '100'
    if edit_house is False:
        house = 'order_building'
    yandex_uid = 'yandex_uid'
    dispatch_status_info = models.DispatchStatusInfo(
        dispatch_id=dispatch_id,
        dispatch_status='accepted',
        dispatch_cargo_status='new',
    )
    order = models.Order(
        pgsql=pgsql,
        dispatch_status_info=dispatch_status_info,
        dispatch_flow='grocery_dispatch',
        location=str(DEFAULT_LOCATION),
        entrance='',
        comment='',
        yandex_uid=yandex_uid,
        depot_id=models.DEFAULT_DEPOT_ID,
    )
    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': {'X-Yandex-UID': yandex_uid}}),
    )
    cart = grocery_cart.add_cart(cart_id=order.cart_id)
    cart.set_delivery_zone_type('pedestrian')
    if depot_id is not None:
        cart.set_depot_id(depot_id=depot_id)
        grocery_depots.add_depot(legacy_depot_id=depot_id)
    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        order_id=order.order_id,
        status='delivered',
        street=order.street,
        building=house,
        flat=order.flat,
        door_code=order.doorcode,
        porch=order.entrance,
        floor=order.floor,
        comment=order.comment,
        location={'lon': DEFAULT_LOCATION[0], 'lat': DEFAULT_LOCATION[1]},
    )
    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )
    antifraud.set_is_fraud(is_fraud)
    request = {
        'order_id': order.order_id,
        'house': house,
        'street': order.street,
    }

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/edit/address', json=request,
    )

    assert response.status == result_code

    if result_code == 500 or edit_house:
        return

    assert antifraud.times_discount_antifraud_called() == 1

    if result_code == 405:
        assert yamaps_local.times_called() == 0
    else:
        assert yamaps_local.times_called() == 1

    if result_code == 200:
        assert grocery_dispatch.times_edit_called() == 1
        order.check_order_history(
            'edit_address',
            {
                'old_address': (
                    f'{order.street}, {order.house}, {order.flat}, '
                    f'{order.doorcode}, {order.entrance}, '
                    f'{order.floor}, {order.comment}'
                ),
                'new_address': (
                    f'{order.street}, {house}, {order.flat}, '
                    f'{order.doorcode}, {order.entrance}, '
                    f'{order.floor}, {order.comment}'
                ),
            },
        )

        order.update()
        assert order.house == house
    else:
        assert grocery_dispatch.times_edit_called() == 0
