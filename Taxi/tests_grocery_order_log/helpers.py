import datetime

from tests_grocery_order_log import models

CART_ITEMS = [
    {
        'id': 'item_id_1',
        'item_name': 'shishka_ice_cream',
        'price': '500',
        'quantity': '1',
    },
    {
        'id': 'item_id_2',
        'item_name': 'chocolate',
        'price': '400',
        'quantity': '1',
    },
]

RECEIPTS = [
    {'title': 'payment_receipt', 'receipt_url': 'payment_receipt_url'},
    {'title': 'refund_receipt', 'receipt_url': 'refund_receipt_url'},
]

DESTINATION = {
    'point': [37.33333, 55.99999],
    'short_text': 'street, house',
    'street': 'street',
    'house': 'house',
    'city': 'city',
    'flat': 'flat',
    'doorcode': 'doorcode',
    'entrance': 'entrance',
    'floor': 'floor',
    'comment': 'comment',
}


def get_upsert_request(order_id, cart_id, depot_id):
    return {
        'order_id': order_id,
        'order_log_info': {
            'short_order_id': '1111-2222',
            'order_created_date': models.NOW,
            'order_source': 'yango',
            'order_state': 'closed',
            'cart_id': cart_id,
            'depot_id': depot_id,
            'order_finished_date': models.NOW,
            'destination': DESTINATION,
            'refund': '500.0000',
            'cart_total_price': '1000.0000',
            'cart_total_discount': '300.0000',
            'cart_items': CART_ITEMS,
            'receipts': RECEIPTS,
            'yandex_uid': 'super_yandex',
            'eats_user_id': 'super_eats',
            'geo_id': 'super_geo',
            'country_iso3': 'RUS',
            'personal_phone_id': 'super_personal',
            'courier': {'name': 'super_courier'},
            'legal_entities': [
                {
                    'additional_properties': [
                        {'title': 'key', 'value': 'value'},
                    ],
                    'title': 'delivery_service_title',
                    'type': 'delivery_service',
                },
            ],
        },
    }


def check_upserted_order_log(order_log, request):
    assert str(order_log.refund) == '500.0000'
    assert str(order_log.cart_total_price) == '1000.0000'
    assert str(order_log.cart_total_discount) == '300.0000'
    order_log_info = request['order_log_info']
    assert len(order_log.cart_items) == len(order_log_info['cart_items'])
    models.check_cart_items(order_log.cart_items, order_log_info['cart_items'])
    assert order_log.receipts == order_log_info['receipts']
    assert order_log.order_finished_date == datetime.datetime.fromisoformat(
        models.NOW,
    )
    assert order_log.order_created_date == models.NOW_DT
    assert order_log.order_source == order_log_info['order_source']
    assert order_log.destination == order_log_info['destination']
    assert order_log.cart_id == order_log_info['cart_id']
    assert order_log.depot_id == order_log_info['depot_id']
    assert order_log.yandex_uid == order_log_info['yandex_uid']
    assert order_log.eats_user_id == order_log_info['eats_user_id']
    assert order_log.courier == order_log_info['courier']['name']
    assert order_log.legal_entities == order_log_info['legal_entities']
    assert order_log.geo_id == order_log_info['geo_id']
    assert order_log.country_iso3 == order_log_info['country_iso3']


def check_upserted_order_log_index(order_log_index, request):
    order_log_info = request['order_log_info']
    assert order_log_index.order_created_date == models.NOW_DT
    assert order_log_index.cart_id == order_log_info['cart_id']
    assert order_log_index.yandex_uid == order_log_info['yandex_uid']
    assert order_log_index.eats_user_id == order_log_info['eats_user_id']
    assert (
        order_log_index.personal_phone_id
        == order_log_info['personal_phone_id']
    )


def add_cold_storage_and_index(
        grocery_cold_storage, yandex_uid, created_date, order_id, pgsql,
):
    closed_string_cold_storage = '2020-08-11T00:00:00.476685'
    grocery_cold_storage.set_order_log_response(
        items=[
            {
                'item_id': order_id,
                'order_id': order_id,
                'short_order_id': 'short_order_id',
                'updated': created_date[:-6],
                'cart_id': 'cart_id_cold',
                'depot_id': 'test_depot_id',
                'yandex_uid': yandex_uid,
                'geo_id': 'test_geo_id',
                'country_iso3': 'RUS',
                'currency': 'RUB',
                'delivery_cost': '500.000',
                'cart_total_price': '100',
                'courier': 'courier-name',
                'cart_total_discount': '1000.00',
                'order_state': 'closed',
                'legal_entities': [
                    {
                        'type': 'restaurant',
                        'title': 'Лавка',
                        'additional_properties': [
                            {
                                'title': 'Наименование',
                                'value': 'Yandex Go Israel LTD',
                            },
                            {
                                'title': 'Адрес',
                                'value': (
                                    '119048, Москва г, Кооперативная'
                                    + ' ул, дом № 2, корпус 14'
                                ),
                            },
                            {'title': 'ОГРН', 'value': '9718101499'},
                        ],
                    },
                ],
                # Cut the timezone as it won't be sent to us
                'order_created_date': created_date[:-6],
                'order_finished_date': closed_string_cold_storage,
                'refund': '0',
                'cart_items': [
                    {
                        'id': 'item-id-23',
                        'price': '299',
                        'quantity': '2',
                        'item_name': 'item-1-title-4',
                    },
                ],
                'receipts': [],
                'order_source': 'web',
                'destination': {
                    'city': 'order_city',
                    'point': [10.0, 20.0],
                    'short_text': 'order_street, order_building',
                    'street': 'order_street',
                    'house': 'order_building',
                },
                'cashback_gain': '111',
                'cashback_charge': '112',
                'eats_user_id': 'eats_user_id',
                'appmetrica_device_id': 'appmetrica_device_id',
                'anonym_id': None,
            },
        ],
    )

    order_log_index = models.OrderLogIndex(
        pgsql=pgsql,
        order_id=order_id,
        cart_id='cart_id_cold',
        order_created_date=datetime.datetime.fromisoformat(created_date),
        yandex_uid=yandex_uid,
    )
    order_log_index.update_db()
