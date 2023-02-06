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
    'MAX_ROBOT_DISTANCE': 4900,
    'SURGES_RATIO_BONUS_COEFF': 0.5,
    'SURGES_RATIO_MAX_BONUS': 60,
    'SURGES_RATIO_MIN_BONUS': -60,
    'SURGE_BONUS_COEF': 0.5,
}

_CHILD_TARIFF_VALUES = {
    'DISPATCH_DRIVER_TAGS_BONUSES': {
        'VI': 90,
        '__default__': 0,
        'gold': 20,
        'platinum': 30,
        'silver': 10,
    },
    'DISPATCH_GRADE_BONUS_SECONDS': {
        '10': 80,
        '8': 60,
        '9': 60,
        '__default__': 0,
    },
    'DISPATCH_MAX_POSITIVE_BONUS_SECONDS': 180,
    'DISPATCH_MAX_TARIFF_BONUS_SECONDS': {'__default__': 0},
    'DISPATCH_MIN_NEGATIVE_BONUS_SECONDS': -900,
    'MAX_ROBOT_DISTANCE': 4900,
    'MAX_ROBOT_TIME': 720,
    'SURGE_BONUS_COEF': 300,
}

DISPATCH_SETTINGS = [
    {
        'zone_name': '__default__',
        'tariff_name': '__default__base__',
        'parameters': [{'values': _DEFAULT_VALUES}],
    },
    {
        'zone_name': '__default__',
        'tariff_name': 'child_tariff',
        'parameters': [{'values': _CHILD_TARIFF_VALUES}],
    },
]


def get_airport_dispatch_settings(
        dispatch_max_positive_bonus_seconds=None,
        dispatch_min_negative_bonus_seconds=None,
):
    return DISPATCH_SETTINGS + [
        {
            'zone_name': 'lipetsk_airport',
            'tariff_name': 'econom',
            'parameters': [
                {
                    'values': {
                        'DISPATCH_MAX_POSITIVE_BONUS_SECONDS': (
                            dispatch_max_positive_bonus_seconds
                        ),
                        'DISPATCH_MIN_NEGATIVE_BONUS_SECONDS': (
                            dispatch_min_negative_bonus_seconds
                        ),
                    },
                },
            ],
        },
    ]
