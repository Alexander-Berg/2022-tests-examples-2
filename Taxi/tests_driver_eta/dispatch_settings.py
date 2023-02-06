_DEFAULT_VALUES = {
    'ANTISURGE_BONUS_COEF': 2.0,
    'ANTISURGE_BONUS_GAP': 1.0,
    'DISPATCH_DRIVER_TAGS_BONUSES': {
        '__default__': 0,
        'park_bonus_top': 30,
        'park_car_id_tag': 60,
        'private_car': 20,
        'reposition_super_surge': 50,
        'silver': 10,
        'topbusinesscars_new': 40,
    },
    'DISPATCH_GRADE_BONUS_SECONDS': {
        '10': 80,
        '8': 60,
        '9': 60,
        '__default__': 0,
    },
    'DISPATCH_MAX_POSITIVE_BONUS_SECONDS': 2000,
    'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {
        '__default__': 0,
        'business': 20,
        'comfortplus': 10,
    },
    'DISPATCH_MIN_NEGATIVE_BONUS_SECONDS': -2000,
    'DISPATCH_REPOSITION_BONUS': {
        'SuperSurge': 120,
        'SuperSurge_completed': 60,
        '__default__': 10,
        'home': 120,
        'poi': 100,
    },
    'MAX_ROBOT_DISTANCE': 4900,
    'MAX_ROBOT_TIME': 720,
    'PAID_SUPPLY_MAX_LINE_DIST': 20000,
    'PAID_SUPPLY_MAX_SEARCH_ROUTE_DISTANCE': 20000,
    'PAID_SUPPLY_MAX_SEARCH_ROUTE_TIME': 2000,
    'SURGES_RATIO_BONUS_COEFF': 0.5,
    'SURGES_RATIO_MAX_BONUS': 60,
    'SURGES_RATIO_MIN_BONUS': -60,
    'SURGE_BONUS_COEF': 0.5,
}

DISPATCH_SETTINGS = [
    {
        'zone_name': '__default__',
        'tariff_name': '__default__base__',
        'parameters': [{'values': _DEFAULT_VALUES}],
    },
]
