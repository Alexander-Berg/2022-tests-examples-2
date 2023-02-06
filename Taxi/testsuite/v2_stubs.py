DRIVER_ETA_REQUEST = {
    'route_points': [[0, 0]],
    'zone_id': 'moscow',
    'classes': [
        {'class_name': 'comfort', 'is_extended_radius': True},
        {'class_name': 'econom', 'is_extended_radius': False},
        {'class_name': 'vip', 'is_extended_radius': True},
        {'class_name': 'express', 'is_extended_radius': True},
    ],
    'payment_method': 'googlepay',
    'provide_candidates': True,
    'extra_params': [
        {
            'consumers': ['candidates', 'lookup_ordering'],
            'params': {
                'order': {'request': {'offer': 'offer_id'}},
                'metadata': 'something',
            },
        },
        {
            'consumers': ['candidates'],
            'params': {
                'order': {'request': {'check_new_logistic_contract': True}},
            },
        },
        {
            'consumers': ['lookup_ordering'],
            'params': {
                'lookup_ordering_parameter': 'lookup_ordering_parameter_value',
            },
        },
    ],
}

CANDIDATES_REQUEST = {
    'allowed_classes': ['comfort', 'econom', 'express', 'vip'],
    'metadata': 'something',
    'order': {
        'request': {'check_new_logistic_contract': True, 'offer': 'offer_id'},
        'user_phone_id': 'phone_id_0',
        'intercity': {'enabled': False},
    },
    'point': [0.0, 0.0],
    'search_settings': {
        'comfort': {'extended_radius': True},
        'econom': {'extended_radius': True},
        'vip': {'extended_radius': True},
        'express': {'extended_radius': True},
    },
    'payment_method': 'card',
    'timeout': 200,
    'zone_id': 'moscow',
}

CANDIDATES_RESPONSE = {
    'candidates': [
        {
            'id': 'dbid2_uuid2',
            'dbid': 'dbid2',
            'uuid': 'uuid2',
            'position': [55.0, 35.0],
            'classes': ['econom'],
            'route_info': {'distance': 0, 'time': 200, 'approximate': False},
            'status': {'driver': 'free'},
        },
        {
            'id': 'dbid1_uuid1',
            'dbid': 'dbid1',
            'uuid': 'uuid1',
            'position': [55.0, 35.0],
            'classes': ['econom', 'vip'],
            'route_info': {'distance': 0, 'time': 100, 'approximate': False},
            'status': {'driver': 'free'},
        },
        {
            'id': 'dbid0_uuid0',
            'dbid': 'dbid0',
            'uuid': 'uuid0',
            'position': [55.0, 35.0],
            'classes': ['econom', 'vip', 'comfort'],
            'route_info': {'distance': 0, 'time': 50, 'approximate': False},
            'status': {'driver': 'free'},
        },
    ],
    'search_details': {
        'econom': {
            'preferred': {
                'line_distance': 1001,
                'route_time': 101,
                'route_distance': 1101,
            },
            'actual': {
                'line_distance': 2001,
                'route_time': 201,
                'route_distance': 2101,
            },
        },
        'comfort': {
            'preferred': {
                'line_distance': 1002,
                'route_time': 102,
                'route_distance': 1102,
            },
            'actual': {
                'line_distance': 2002,
                'route_time': 202,
                'route_distance': 2102,
            },
        },
        'vip': {
            'preferred': {
                'line_distance': 1003,
                'route_time': 103,
                'route_distance': 1103,
            },
            'actual': {
                'line_distance': 2003,
                'route_time': 203,
                'route_distance': 2103,
            },
        },
        'express': {
            'preferred': {
                'line_distance': 1004,
                'route_time': 104,
                'route_distance': 1104,
            },
            'actual': {
                'line_distance': 2004,
                'route_time': 204,
                'route_distance': 2104,
            },
        },
    },
}


LOOKUP_ORDERING_REQUEST = {
    'intent': 'eta',
    'requests': [
        {
            'search': {
                'payment_method': 'card',
                'allowed_classes': ['comfort'],
                'order': {
                    'request': {
                        'offer': 'offer_id',
                        'source': {'geopoint': [0.0, 0.0]},
                        'surge_price': None,
                    },
                    'nearest_zone': 'moscow',
                    'user_phone_id': 'phone_id_0',
                    'user_id': '',
                    'intercity': {'enabled': False},
                    'is_intercity': False,
                },
                'metadata': 'something',
                'lookup_ordering_parameter': 'lookup_ordering_parameter_value',
                'meta_info': {},
            },
            'candidates': [
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'classes': ['econom', 'vip', 'comfort'],
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
            ],
        },
        {
            'search': {
                'payment_method': 'card',
                'allowed_classes': ['econom'],
                'order': {
                    'request': {
                        'offer': 'offer_id',
                        'source': {'geopoint': [0.0, 0.0]},
                        'surge_price': None,
                    },
                    'nearest_zone': 'moscow',
                    'user_phone_id': 'phone_id_0',
                    'user_id': '',
                    'intercity': {'enabled': False},
                    'is_intercity': False,
                },
                'metadata': 'something',
                'lookup_ordering_parameter': 'lookup_ordering_parameter_value',
                'meta_info': {},
            },
            'candidates': [
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'classes': ['econom'],
                    'route_info': {
                        'time': 200,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'classes': ['econom', 'vip'],
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'classes': ['econom', 'vip', 'comfort'],
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
            ],
        },
        {
            'search': {
                'payment_method': 'card',
                'allowed_classes': ['vip'],
                'order': {
                    'request': {
                        'offer': 'offer_id',
                        'source': {'geopoint': [0.0, 0.0]},
                        'surge_price': None,
                    },
                    'nearest_zone': 'moscow',
                    'user_phone_id': 'phone_id_0',
                    'user_id': '',
                    'intercity': {'enabled': False},
                    'is_intercity': False,
                },
                'metadata': 'something',
                'lookup_ordering_parameter': 'lookup_ordering_parameter_value',
                'meta_info': {},
            },
            'candidates': [
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'classes': ['econom', 'vip'],
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
                {
                    'position': [55.0, 35.0],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'classes': ['econom', 'vip', 'comfort'],
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
            ],
        },
    ],
}


LOOKUP_ORDERING_RESPONSE = {
    'responses': [
        {'candidates': [{'id': 'dbid0_uuid0', 'score': 1}], 'search': {}},
        {
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 1},
                {'id': 'dbid0_uuid0', 'score': 2},
                {'id': 'dbid2_uuid2', 'score': 3},
            ],
            'search': {'some': 0},
        },
        {
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 1},
                {'id': 'dbid0_uuid0', 'score': 2},
            ],
        },
    ],
}


UMLAAS_DISPATCH_REQUEST = {
    'payment_method': 'card',
    'request_source_type': 'driver-eta',
    'airport': False,
    'is_intercity': False,
    'tariff_zone': 'moscow',
    'route_points': [[0.0, 0.0]],
    'classes_info': [
        {
            'free_time': 102.0,
            'free_distance': 1102.0,
            'actual_distance': 2102.0,
            'actual_line_distance': 2002.0,
            'actual_time': 202.0,
            'no_data_from_candidates': False,
            'tariff_class': 'comfort',
            'estimated_waiting': 50.0,
            'candidates': [
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 1,
                },
            ],
        },
        {
            'free_time': 101.0,
            'free_distance': 1101.0,
            'actual_distance': 2101.0,
            'actual_line_distance': 2001.0,
            'actual_time': 201.0,
            'no_data_from_candidates': False,
            'tariff_class': 'econom',
            'estimated_waiting': 100.0,
            'candidates': [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 1,
                },
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 2,
                },
                {
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 200,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 3,
                },
            ],
        },
        {
            'free_time': 104.0,
            'free_distance': 1104.0,
            'actual_distance': 2104.0,
            'actual_line_distance': 2004.0,
            'actual_time': 204.0,
            'no_data_from_candidates': False,
            'tariff_class': 'express',
        },
        {
            'free_time': 103.0,
            'free_distance': 1103.0,
            'actual_distance': 2103.0,
            'actual_line_distance': 2003.0,
            'actual_time': 203.0,
            'no_data_from_candidates': False,
            'tariff_class': 'vip',
            'estimated_waiting': 100.0,
            'candidates': [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 1,
                },
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                    'score': 2,
                },
            ],
        },
    ],
}


UMLAAS_DISPATCH_RESPONSE = {
    'verdicts': [
        {
            'tariff_class': 'econom',
            'estimate_distance': 100,
            'estimate_time': 42,
            'order_allowed': True,
        },
        {
            'tariff_class': 'vip',
            'estimate_distance': 10000,
            'estimate_time': 4200,
            'order_allowed': True,
        },
        {'tariff_class': 'comfort', 'order_allowed': False},
        {
            'tariff_class': 'express',
            'estimate_distance': 1000,
            'estimate_time': 100,
            'order_allowed': True,
        },
    ],
}

UMLAAS_DISPATCH_EMPTY_REQUEST = {
    'payment_method': 'card',
    'request_source_type': 'driver-eta',
    'airport': False,
    'is_intercity': False,
    'tariff_zone': 'moscow',
    'route_points': [[0.0, 0.0]],
    'classes_info': [
        {
            'free_time': 0,
            'free_distance': 0,
            'no_data_from_candidates': True,
            'tariff_class': 'comfort',
        },
        {
            'free_time': 0,
            'free_distance': 0,
            'no_data_from_candidates': True,
            'tariff_class': 'econom',
        },
        {
            'free_time': 0,
            'free_distance': 0,
            'no_data_from_candidates': True,
            'tariff_class': 'express',
        },
        {
            'free_time': 0,
            'free_distance': 0,
            'no_data_from_candidates': True,
            'tariff_class': 'vip',
        },
    ],
}

UMLAAS_DISPATCH_EMPTY_RESPONSE = {
    'verdicts': [
        {'tariff_class': 'econom', 'order_allowed': False},
        {'tariff_class': 'vip', 'order_allowed': False},
        {'tariff_class': 'comfort', 'order_allowed': False},
        {'tariff_class': 'express', 'order_allowed': False},
    ],
}

SEARCH_SETTINGS_COMFORT = {
    'limit': 10,
    'max_distance': 3000,
    'max_route_distance': 4000,
    'max_route_time': 100,
}

SEARCH_SETTINGS_ECONOM = {
    'limit': 10,
    'max_distance': 4000,
    'max_route_distance': 5000,
    'max_route_time': 500,
}

SEARCH_SETTINGS_VIP = {
    'limit': 10,
    'max_distance': 20000,
    'max_route_distance': 20000,
    'max_route_time': 200,
}


DRIVER_ETA_RESPONSE = {
    'classes': {
        'express': {
            'found': False,
            'estimated_time': 100.0,
            'estimated_distance': 1000.0,
            'no_cars_order_enabled': True,
            'paid_supply_enabled': False,
            'order_allowed': True,
        },
        'vip': {
            'found': True,
            'estimated_time': 4200.0,
            'estimated_distance': 10000.0,
            'no_cars_order_enabled': False,
            'paid_supply_enabled': True,
            'order_allowed': True,
            'candidates': [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                },
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                },
            ],
        },
        'econom': {
            'found': True,
            'estimated_time': 42,
            'estimated_distance': 100,
            'no_cars_order_enabled': False,
            'paid_supply_enabled': False,
            'order_allowed': True,
            'candidates': [
                {
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 100,
                        'distance': 0,
                        'approximate': False,
                    },
                },
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                },
                {
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 200,
                        'distance': 0,
                        'approximate': False,
                    },
                },
            ],
        },
        'comfort': {
            'found': True,
            'no_cars_order_enabled': False,
            'paid_supply_enabled': False,
            'order_allowed': False,
            'candidates': [
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'chain_info': {},
                    'status': 'free',
                    'route_info': {
                        'time': 50,
                        'distance': 0,
                        'approximate': False,
                    },
                },
            ],
        },
    },
}

DRIVER_ETA_EMPTY_RESPONSE = {
    'classes': {
        'express': {
            'found': False,
            'no_cars_order_enabled': True,
            'paid_supply_enabled': False,
            'order_allowed': True,
            'no_data': True,
        },
        'vip': {
            'found': False,
            'no_cars_order_enabled': True,
            'paid_supply_enabled': False,
            'order_allowed': True,
            'no_data': True,
        },
        'econom': {
            'found': False,
            'no_cars_order_enabled': True,
            'paid_supply_enabled': False,
            'order_allowed': True,
            'no_data': True,
        },
        'comfort': {
            'found': False,
            'no_cars_order_enabled': True,
            'paid_supply_enabled': False,
            'order_allowed': True,
            'no_data': True,
        },
    },
}
