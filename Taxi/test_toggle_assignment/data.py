import datetime

ORDER_META = {
    'allowed_classes': ['vip', 'econom', 'business'],
    'classes': ['vip', 'econom', 'business'],
    'point': [37.622648, 55.756032],
    'destination': [37.622648, 55.756032],
    'order': {
        'nearest_zone': 'example',
        'created': datetime.datetime.now().timestamp(),
        'request': {
            'offer': 'offer_f64a0b4d8488395bc9f652addd',
            'source': {'geopoint': [37.622648, 55.756032]},
            'due': datetime.datetime.now().timestamp(),
            'surge_price': 2.0,
        },
        'user_phone_id': 'user_phone_id_0',
    },
    'service': 'taxi',
}

CANDIDATE = {
    'id': 'dbid0_uuid0',
    'dbid': 'dbid0',
    'uuid': 'uuid0',
    'car_number': 'some_number',
    'classes': ['econom'],
    'unique_driver_id': 'some_id',
    'position': [37.622647, 55.756032],
    'profile': {'grades': {'g_econom': 1, 'g_minivan': 1}},
    'route_info': {'distance': 15000, 'time': 200, 'approximate': False},
    'license_id': 'license_id',
    'status': {'driver': 'free'},
    'chain_info': {
        'destination': [55.0, 35.0],
        'left_dist': 100,
        'left_time': 10,
        'order_id': 'some_order_id',
    },
    'metadata': {'reposition_check_required': True},
}

SCORING_RESPONSE = {'candidates': [{'id': 'dbid0_uuid0', 'score': 200}]}
