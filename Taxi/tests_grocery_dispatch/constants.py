import uuid

ORDER_ID = '123123'
ORDER_ID_2 = '123124'
SHORT_ORDER_ID = 'short-order-id-42'
DEPOT_ID = '123456'
DEPOT_ID_2 = '0'
CLAIM_ID = 'claim_1'
CLAIM_ID_2 = 'claim_2'
DISPATCH_TYPE = 'cargo_sync'
VERSION = 1
PERSONAL_PHONE_ID = 'personal_phone_id_123'


NOW = '2020-10-05T16:28:00+00:00'
NOW_TS = 1601915280
DELIVERY_ETA_TS = '2020-10-05T16:38:00.000Z'

DELIVERY_PERFECT_TIME = '2020-10-05T16:58:00+00:00'
# now + max_eta + time_intervals_endpoint_strict_span
DELIVERY_STRICT_TIME = '2020-10-05T17:03:00+00:00'
DISPATCH_ID = str(uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}'))

COURIER_CONTACT_PHONE = '+79091237492'
COURIER_CONTACT_EXT = '632'
PERFORMER_NAME = 'test_name'

PARK_ID = '123432'
DRIVER_ID = '23423'
PERFORMER_ID = f'{PARK_ID}_{DRIVER_ID}'
EATS_PROFILE_ID = '12345678'
PROFILE_ID = '123_123'

SMOOTHING_PERIOD = 1000
SMOOTHING_FACTOR = 0.15

CREATE_REQUEST_DATA = {
    'order_id': ORDER_ID,
    'short_order_id': SHORT_ORDER_ID,
    'depot_id': DEPOT_ID,
    'location': {'lon': 39.60258, 'lat': 52.569089},
    'zone_type': 'pedestrian',
    'created_at': '2020-10-05T16:28:00.000Z',
    'max_eta': 900,
    'items': [
        {
            'item_id': 'item_id_1',
            'title': 'some product',
            'price': '12.99',
            'currency': 'RUB',
            'quantity': '1',
        },
        {
            'item_id': 'item_id_2',
            'title': 'some product_2',
            'price': '13.88',
            'currency': 'RUB',
            'quantity': '1',
        },
    ],
    'user_locale': 'ru',
    'personal_phone_id': PERSONAL_PHONE_ID,
    'comment': 'user comment',
    'door_code': 'doorcode',
    'door_code_extra': 'door_code_extra',
    'doorbell_name': 'doorbell_name',
    'building_name': 'building_name',
    'floor': 'floor',
    'flat': 'flat',
    'city': 'city',
    'street': 'street',
}
