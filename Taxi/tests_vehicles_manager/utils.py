FLEET_API_CLIENT_ID = 'test'
FLEET_API_KEY_ID = '17'
X_REAL_IP = '8.7.6.5'
PARK_ID = '123'
VEHILCE_ID = '12345'
IDEMPOTENCY_TOKEN = '67754336-d4d1-43c1-aadb-cabd06674ea6'

AUTHOR_FLEET_API_HEADERS = {
    'X-Fleet-API-Client-ID': FLEET_API_CLIENT_ID,
    'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
    'X-Real-Ip': X_REAL_IP,
    'X-Idempotency-Token': IDEMPOTENCY_TOKEN,
    'X-Park-ID': PARK_ID,
    'Accept-Language': 'ru',
}

DEFAULT_VEHICLE_SPECIFICATIONS = {
    'model': 'test',
    'brand': 'test',
    'color': 'Желтый',
    'year': 5,
    'transmission': 'unknown',
}
DEFAULT_VEHICLE_LICENSES = {'licence_plate_number': '12345'}

DEFAULT_PARK_PROFILE = {'callsign': '123', 'status': 'working'}

DEFAULT_CARGO = {
    'cargo_loaders': 1,
    'carrying_capacity': 3000,
    'cargo_hold_dimensions': {'length': 100, 'width': 200, 'height': 300},
}

OPTEUM_CAR_ORDER_CATEGORIES = {'categories': ['cargo', 'test']}

DEFAULT_CONFIG = {
    'cities': [],
    'countries': [],
    'dbs': [],
    'dbs_disable': [],
    'enable': True,
    'enable_support': True,
    'enable_support_users': [],
}

DEFAULT_RUS_CONFIG = {
    'cities': [],
    'countries': ['rus'],
    'dbs': [],
    'dbs_disable': [],
    'enable': True,
}

EXTERNAL_CATEGORIES = [
    'econom',
    'comfort',
    'comfort_plus',
    'business',
    'minivan',
    'vip',
    'wagon',
    'pool',
    'start',
    'standart',
    'ultimate',
    'maybach',
    'promo',
    'premium_van',
    'premium_suv',
    'suv',
    'personal_driver',
    'cargo',
    'express',
    'courier',
    'eda',
    'lavka',
    'selfdriving',
    'scooters',
]

FLEET_API_CAR_CATEGORIES = {'external_categories': EXTERNAL_CATEGORIES}

VALIDATION_DISABLED_FIELDS = {
    'brand': {'field': 'vehicle_specifications.brand', 'replace_value': 'BMW'},
    'model': {'field': 'vehicle_specifications.model', 'replace_value': '7er'},
    'year': {'field': 'vehicle_specifications.year', 'replace_value': 2021},
    'body_number': {
        'field': 'vehicle_specifications.body_number',
        'replace_value': '987697898',
    },
    'mileage': {
        'field': 'vehicle_specifications.mileage',
        'replace_value': None,
    },
    'vin': {
        'field': 'vehicle_specifications.vin',
        'replace_value': '12431241234124',
    },
    'transmission': {
        'field': 'vehicle_specifications.transmission',
        'replace_value': 'unknown',
    },
    'color': {
        'field': 'vehicle_specifications.color',
        'replace_value': 'Белый',
    },
    'number': {
        'field': 'vehicle_licenses.licence_plate_number',
        'replace_value': '6345634563465',
    },
    'permit_num': {
        'field': 'vehicle_licenses.licence_number',
        'replace_value': '9789789789789',
    },
    'registration_cert': {
        'field': 'vehicle_licenses.registration_certificate',
        'replace_value': '1111111111111',
    },
    'callsign': {
        'field': 'park_profile.callsign',
        'replace_value': 'qwrty12312',
    },
    'description': {'field': 'park_profile.comment', 'replace_value': None},
    'fuel_type': {
        'field': 'park_profile.fuel_type',
        'replace_value': 'propan',
    },
    'rental': {
        'field': 'park_profile.is_park_property',
        'replace_value': False,
    },
    'rental_status': {
        'field': 'park_profile.ownership_type',
        'replace_value': 'park',
    },
    'carrier_permit_owner_id': {
        'field': 'park_profile.license_owner_id',
        'replace_value': '456787656787678',
    },
    'amenities': {
        'field': 'park_profile.amenities',
        'replace_value': ['conditioner'],
    },
    'tariffs': {'field': 'park_profile.tariffs', 'replace_value': ['test']},
    'categories': {
        'field': 'park_profile.categories',
        'replace_value': ['econom', 'cargo'],
    },
    'status': {'field': 'park_profile.status', 'replace_value': 'in_garage'},
    'leasing_company': {
        'field': 'park_profile.leasing_conditions.company',
        'replace_value': 'alpha',
    },
    'leasing_term': {
        'field': 'park_profile.leasing_conditions.term',
        'replace_value': 320,
    },
    'leasing_monthly_payment': {
        'field': 'park_profile.leasing_conditions.monthly_payment',
        'replace_value': 90000,
    },
    'leasing_interest_rate': {
        'field': 'park_profile.leasing_conditions.interest_rate',
        'replace_value': '4.61',
    },
    'leasing_start_date': {
        'field': 'park_profile.leasing_conditions.start_date',
        'replace_value': '2018-01-02',
    },
    'cargo_loaders': {'field': 'cargo.cargo_loaders', 'replace_value': 2},
    'carrying_capacity': {
        'field': 'cargo.carrying_capacity',
        'replace_value': 50,
    },
    'cargo_hold_dimensions': {
        'field': 'cargo.cargo_hold_dimensions',
        'replace_value': {'height': 110, 'length': 90, 'width': 100},
    },
    'boosters': {'field': 'child_safety.booster_count', 'replace_value': 1},
    'chairs': {
        'field': 'child_safety.chairs',
        'replace_value': [{'categories': ['Category0'], 'isofix': True}],
    },
}

DEFAULT_REQUEST = {
    'cargo': {
        'cargo_hold_dimensions': {'height': 1, 'length': 5, 'width': 0},
        'cargo_loaders': 5,
        'carrying_capacity': 5,
    },
    'child_safety': {
        'booster_count': 2,
        'chairs': [{'categories': ['Category0'], 'isofix': True}],
    },
    'park_profile': {
        'amenities': ['wifi'],
        'callsign': 'test',
        'categories': ['econom', 'cargo'],
        'comment': 'good',
        'fuel_type': 'gas',
        'is_park_property': True,
        'ownership_type': 'leasing',
        'leasing_conditions': {
            'company': 'sber',
            'start_date': '2018-01-01',
            'term': 1000,
            'monthly_payment': 50000,
            'interest_rate': '4.6',
        },
        'license_owner_id': '5325423',
        'status': 'working',
        'tariffs': ['new'],
    },
    'vehicle_licenses': {
        'licence_number': '1241243',
        'licence_plate_number': '1234',
        'registration_certificate': '12341234',
    },
    'vehicle_specifications': {
        'body_number': '1234',
        'brand': 'lada',
        'color': 'Желтый',
        'mileage': 5000,
        'model': 'lada',
        'transmission': 'mechanical',
        'vin': '12431241234124',
        'year': 2001,
    },
}


def get_required_caregories_config():
    data = {
        'include': {
            'categories': ['wifi', 'top'],
            'categories_related': ['cargo', 'red'],
        },
        'exclude': {
            'categories': ['express', 'courier'],
            'categories_related': ['new_car'],
        },
    }

    result = []
    for kind in ['include', 'exclude']:
        config = DEFAULT_CONFIG.copy()
        config['kind'] = 'required'
        config['categories'] = data[kind]['categories']
        config['categories_related'] = {
            'kind': kind,
            'set': data[kind]['categories_related'],
        }
        result.append(config)
    return result


def make_vehicle_request_body(
        vehicle_specifications=None,
        vehicle_licenses=None,
        park_profile=None,
        cargo=None,
        child_safety=None,
):
    return {
        'vehicle_specifications': vehicle_specifications,
        'vehicle_licenses': vehicle_licenses,
        'park_profile': park_profile,
        'cargo': cargo,
        'child_safety': child_safety,
    }
