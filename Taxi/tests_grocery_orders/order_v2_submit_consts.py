CART_ID = '00000000-0000-0000-0000-d98013100500'
OFFER_ID = 'offer-id'
CART_VERSION = 4
LOCATION_IN_RUSSIA = [37, 55]
LOCATION_IN_ISRAEL = [34.865849, 32.054721]
RUSSIAN_PHONE_NUMBER = '+79993537429'
ISRAELIAN_PHONE_NUMBER = '+972542188598'
AUSTRALIAN_PHONE_NUMBER = '+991234561'
PLACE_ID = 'yamaps://12345'
FLOOR = '13'
FLAT = '666'
URI = (
    'ymapsbm1://geo?ll=37.601%2C55.585&spn=0.001%2C0.'
    '001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%'
    '20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%9'
    '2%D0%B0%D1%80%D1%88%D0%B0%D0%B2%D1%81%D0%BA%D0%B'
    'E%D0%B5%20%D1%88%D0%BE%D1%81%D1%81%D0%B5%2C%2014'
    '1%D0%90%D0%BA1%2C%20%D0%BF%D0%BE%D0%B4%D1%8A%D0%B'
    '5%D0%B7%D0%B4%201%20%7B3457696635%7D'
)
DOORCODE = '42'
COMMENT = 'comment'
DEPOT_ID = '2809'
ENTRANCE = '3333'

DOORCODE_EXTRA = 'doorcode_extra'
BUILDING_NAME = 'building_name'
DOORBELL_NAME = 'doorbell_name'

LEFT_AT_DOOR = False
MEET_OUTSIDE = False
NO_DOOR_CALL = True

PROCESSING_FLOW_VERSION = 'grocery_flow_v1'

REQUEST_PAYMENT_TYPE = 'card'
REQUEST_PAYMENT_ID = 'card-x2809'

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
        'meet_outside': MEET_OUTSIDE,
        'no_door_call': NO_DOOR_CALL,
        'comment': COMMENT,
        'entrance': ENTRANCE,
    },
    'flow_version': PROCESSING_FLOW_VERSION,
    'payment_method_type': REQUEST_PAYMENT_TYPE,
    'payment_method_id': REQUEST_PAYMENT_ID,
}

REGION_ID = 102

BADGE_PAYMENT_METHOD_ID = 'badge:yandex_badge:badge_id'
