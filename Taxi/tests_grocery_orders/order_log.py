import copy
import datetime
import decimal

from . import models

DEPOT_TIN = '1234'
DEPOT_NAME = 'super_depot'
DEPOT_ADDRESS = 'super depot address'

DEPOT_FOR_CHECK = {
    'name': DEPOT_NAME,
    'address': DEPOT_ADDRESS,
    'tin': DEPOT_TIN,
    'currency': 'RUB',
}

COURIER = {
    'name': 'courier_name',
    'driver_id': 'driver_id0',
    'transport_type': 'transport_type0',
    'eats_courier_id': 'eats_courier_id0',
    'courier_full_name': 'courier_full_name0',
    'organization_name': 'organization_name0',
    'legal_address': 'legal_address0',
    'ogrn': 'ogrn0',
    'work_schedule': 'work_schedule0',
    'tin': 'tin0',
    'vat': 'vat0',
    'balance_client_id': 'balance_client_id0',
}

CART_ITEMS = [
    models.GroceryCartItem(
        item_id='item_id_1', price='100', quantity='3', refunded_quantity='2',
    ),
    models.GroceryCartItem(
        item_id='item_id_2', price='200', quantity='2', refunded_quantity='1',
    ),
    models.GroceryCartItem(item_id='item_id_3', price='300', quantity='1'),
]


def _compare_locations(order_log_location, db_location):
    order_log_location = [int(s) for s in order_log_location]
    db_location = (
        db_location.replace('(', '').replace(')', '').replace(',', ' ')
    )
    db_location = [float(s) for s in db_location.split()]
    return order_log_location == db_location


def _calculate_refund(cart_items):
    refund = decimal.Decimal(0)
    for item in cart_items:
        refund += decimal.Decimal(item.refunded_quantity) * decimal.Decimal(
            item.price,
        )
    return str(refund)


def _check_restaurant(legal_entity, depot):
    assert legal_entity['title'] == 'depot'
    additional_properties = legal_entity['additional_properties']

    if 'name' in depot:
        assert additional_properties[0]['title'] == 'depot_name'
        assert additional_properties[0]['value'] == depot['name']
    if 'address' in depot:
        assert additional_properties[1]['title'] == 'address'
        assert additional_properties[1]['value'] == depot['address']
    if 'tin' in depot:
        assert additional_properties[2]['title'] == 'tin'
        assert additional_properties[2]['value'] == depot['tin']


def _check_depot(order_log_info, depot):
    legal_entities = order_log_info['legal_entities']

    if 'currency' in depot:
        assert order_log_info['currency'] == depot['currency']

    for legal_entity in legal_entities:
        if legal_entity['type'] == 'restaurant':
            _check_restaurant(legal_entity, depot)
            return
    assert False, 'restaurant is not found'


def _check_delivery_service(legal_entity, courier):
    assert legal_entity['title'] == 'delivery'
    additional_properties = legal_entity['additional_properties']

    delivery_prefix = 'delivery_'  # namespace for tanker
    for additional_property in additional_properties:
        title = additional_property['title']
        assert title.startswith(delivery_prefix)
        assert (
            courier[title[len(delivery_prefix) :]]
            == additional_property['value']
        )


def _check_courier(order_log_info, courier):
    legal_entities = order_log_info['legal_entities']

    for legal_entity in legal_entities:
        if legal_entity['type'] == 'delivery_service':
            _check_delivery_service(legal_entity, courier)
            return
    assert False, 'delivery_service is not found'


def _check_cart_items(order_log_info, cart_items):
    assert len(order_log_info['cart_items']) == len(cart_items)
    refund = _calculate_refund(cart_items)
    if float(refund) > 0:
        assert order_log_info['refund'] == refund

    for cart_item, item in zip(order_log_info['cart_items'], cart_items):
        assert cart_item['id'] == item.item_id
        assert cart_item['item_name'] == item.title
        assert cart_item['price'] == item.price
        assert cart_item['quantity'] == item.quantity
        if 'gross_weight' in cart_item:
            assert decimal.Decimal(
                cart_item['gross_weight'],
            ) == decimal.Decimal(item.gross_weight)


def _cmp_as_decimal(lhs, rhs):
    if lhs is None and rhs is None:
        return True
    return decimal.Decimal(lhs) == decimal.Decimal(rhs)


def _check_order_log_items(order_log_info, order_log_cart_items):
    assert len(order_log_info['cart_items']) == len(order_log_cart_items)

    for cart_item, item in zip(
            order_log_info['cart_items'], order_log_cart_items,
    ):
        assert cart_item['id'] == item.id
        assert cart_item['item_name'] == item.item_name
        assert _cmp_as_decimal(cart_item['price'], item.price)
        assert _cmp_as_decimal(cart_item['quantity'], item.quantity)

        assert _cmp_as_decimal(
            cart_item.get('gross_weight'), item.gross_weight,
        )
        assert _cmp_as_decimal(
            cart_item.get('cashback_gain'), item.cashback_gain,
        ), (cart_item.get('cashback_gain'), item.cashback_gain)
        assert _cmp_as_decimal(
            cart_item.get('cashback_charge'), item.cashback_charge,
        )
        assert cart_item.get('parcel_vendor') == item.parcel_vendor
        assert cart_item.get('parcel_ref_order') == item.parcel_ref_order


def check_order_log_payload(
        payload,
        order,
        cart_items=copy.deepcopy(CART_ITEMS),
        depot=copy.deepcopy(DEPOT_FOR_CHECK),
        courier=None,
        is_finish=False,
        is_checkout=False,
        delivery_cost='500',
        delivery_eta=None,
        order_log_cart_items=None,
        cashback_gain=None,
        cashback_charge=None,
):
    assert 'order_log_info' in payload
    assert payload['order_id'] == order.order_id
    order_log_info = payload['order_log_info']

    if is_checkout:
        assert order_log_info['order_state'] == 'created'
        assert order_log_info['order_type'] == 'grocery'
        assert order_log_info['delivery_type'] == 'courier'
        assert 'order_promise' in order_log_info

    assert 'receipts' not in order_log_info

    assert order_log_info['order_source'] == 'yango'
    assert order_log_info['short_order_id'] == order.short_order_id
    assert order_log_info['depot_id'] == order.depot_id
    assert (
        order_log_info['cart_id'] == order.cart_id
        or order_log_info['cart_id'] == order.child_cart_id
    )

    items_sum = sum(
        [
            decimal.Decimal(item.price) * decimal.Decimal(item.quantity)
            for item in cart_items
        ],
    )
    price_with_delivery = items_sum + decimal.Decimal(
        delivery_cost or 0,
    )  # delivery_cost may be None

    assert (
        decimal.Decimal(order_log_info['cart_total_price'])
        == price_with_delivery
    ), (
        decimal.Decimal(order_log_info['cart_total_price']),
        price_with_delivery,
    )

    assert order_log_info['cart_total_discount'] == '500'

    if delivery_cost is not None:
        assert order_log_info['delivery_cost'] == delivery_cost
    if delivery_eta is not None:
        assert order_log_info['delivery_eta'] == delivery_eta

    assert (
        datetime.datetime.fromisoformat(order_log_info['order_created_date'])
        == order.created
    )
    if is_finish:
        assert order_log_info['order_type'] == 'grocery'

        assert (
            order_log_info['order_state'] == 'closed'
            or order_log_info['order_state'] == 'canceled'
        )

        assert (
            datetime.datetime.fromisoformat(
                order_log_info['order_finished_date'],
            )
            == order.finish_started
        )

        if (
                order.dispatch_status_info is not None
                and order.dispatch_status_info.dispatch_courier_name
                is not None
        ):
            assert (
                order.dispatch_status_info.dispatch_courier_name
                == order_log_info['courier']['courier_full_name']
            )
        else:
            assert 'courier' not in order_log_info

        assert order_log_info['delivery_type'] == 'courier'

    assert order_log_info['yandex_uid'] == order.yandex_uid
    assert order_log_info['personal_phone_id'] == order.personal_phone_id
    assert order_log_info['eats_user_id'] == order.eats_user_id

    if order.personal_email_id is not None:
        assert order_log_info['personal_email_id'] == order.personal_email_id

    assert _compare_locations(
        order_log_info['destination']['point'], order.location,
    )

    assert (
        order_log_info['destination']['short_text']
        == order.street + ', ' + order.house
    )
    if order.house is not None:
        assert order_log_info['destination']['house']
    if order.street is not None:
        assert order_log_info['destination']['street']
    if order.city is not None:
        assert order_log_info['destination']['city']
    if order.doorcode is not None:
        assert order_log_info['destination']['doorcode'] == order.doorcode
    if order.entrance is not None:
        assert order_log_info['destination']['entrance'] == order.entrance
    if order.floor is not None:
        assert order_log_info['destination']['floor'] == order.floor
    if order.comment is not None:
        assert order_log_info['destination']['comment'] == order.comment
    if order.doorcode_extra is not None:
        assert (
            order_log_info['destination']['doorcode_extra']
            == order.doorcode_extra
        )
    if order.building_name is not None:
        assert (
            order_log_info['destination']['building_name']
            == order.building_name
        )
    if order.doorbell_name is not None:
        assert (
            order_log_info['destination']['doorbell_name']
            == order.doorbell_name
        )
    if order.left_at_door is not None:
        assert (
            order_log_info['destination']['left_at_door'] == order.left_at_door
        )
    if order.meet_outside is not None:
        assert (
            order_log_info['destination']['meet_outside'] == order.meet_outside
        )
    if order.no_door_call is not None:
        assert (
            order_log_info['destination']['no_door_call'] == order.no_door_call
        )
    if depot is not None:
        _check_depot(order_log_info, depot)

    if courier:
        _check_courier(order_log_info, courier)

    if cart_items is not None:
        _check_cart_items(order_log_info, cart_items)

    if order_log_cart_items is not None:
        _check_order_log_items(order_log_info, order_log_cart_items)

    assert _cmp_as_decimal(cashback_gain, order_log_info.get('cashback_gain'))
    assert _cmp_as_decimal(
        cashback_charge, order_log_info.get('cashback_charge'),
    )
    assert order_log_info['grocery_flow_version'] == order.grocery_flow_version
    assert order_log_info['app_info'] == order.app_info


def check_eats_checkout(
        payload,
        order_created_date,
        user_id,
        order_id,
        depot_id,
        cart_items=copy.deepcopy(CART_ITEMS),
        depot=copy.deepcopy(DEPOT_FOR_CHECK),
        appmetrica_device_id=None,
):
    assert 'order_log_info' in payload
    assert payload['order_id'] == order_id
    order_log_info = payload['order_log_info']
    assert order_log_info['order_type'] == 'eats'
    assert order_log_info['order_state'] == 'created'
    assert order_log_info['personal_phone_id'] == 'ppp'
    assert order_log_info['eats_user_id'] == user_id
    assert 'short_order_id' not in order_log_info
    assert order_log_info['depot_id'] == depot_id
    assert order_log_info['delivery_cost'] == '0'
    if appmetrica_device_id is not None:
        assert order_log_info['appmetrica_device_id'] == appmetrica_device_id
    assert order_log_info['destination'] == {
        'point': [37.0, 55.0],
        'short_text': 'Varshavskoye Highway' ', ' '141Ак1',
        'street': 'Varshavskoye Highway',
        'house': '141Ак1',
        'city': 'Moscow',
        'flat': '666',
        'doorcode': '42',
        'entrance': '1',
        'floor': '13',
        'comment': 'please, fast!',
    }
    assert order_log_info['order_source'] == 'yango'
    assert datetime.datetime.fromisoformat(
        order_log_info['order_created_date'],
    ) == datetime.datetime.fromisoformat(order_created_date)
    if depot is not None:
        _check_depot(order_log_info, depot)

    if cart_items is not None:
        _check_cart_items(order_log_info, cart_items)
