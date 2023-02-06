import pytest

from taxi.config import configs
from taxi.config import exceptions


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
        {},
        True
    ),
    (
        {
            "ru": {}
        },
        False
    ),
    (
        {
            "ru": {
                "mcc": "250"
            }
        },
        False
    ),
    (
        {
            "ru": {
                "mcc": "250",
                "formatted_phone": "formatted_phone",
                "phone": "phone",
                "zones": {
                    "zone1": {
                        "formatted_phone": "formatted_phone",
                        "phone": "phone"
                    }
                }
            }
        },
        True
    ),
    (
        {
            "RU": {
                "mcc": "250",
                "formatted_phone": "formatted_phone",
                "phone": "phone",
                "zones": {
                    "zone1": {
                        "formatted_phone": "formatted_phone",
                        "phone": "phone"
                    }
                }
            }
        },
        False
    ),
    (
        {
            "ru": {
                "mcc": "250",
                "formatted_phone": "formatted_phone",
                "phone": "",
                "zones": {
                    "zone1": {
                        "formatted_phone": "formatted_phone",
                        "phone": "phone"
                    }
                }
            }
        },
        False
    ),
])
def test_callcenter_phones_param(value, is_valid):
    p = configs.CALLCENTER_PHONES
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
        {},
        False
    ),
    (
        {
            '__default__': 1,
            'moscow': 1,
        },
        True
    ),
    (
        {
            '__default__': 1,
            'moscow': {
                '__default__': 1,
                'color_button_experiment': 1
            }
        },
        True
    ),
    (
        {
            '__default__': {
                '__default__': 1,
                'color_button_experiment': 1
            },
            'moscow': {
                '__default__': 1,
                'color_button_experiment': 1
            }
        },
        True
    ),
    (
        {
            '__default__': {},
            'color_button_experiment': {}
        },
        False
    ),
    (
        {
            '__default__': {
                '__default__': 1,
                'color_button_experiment': 1
            },
            'moscow': {
                '__default__': 1,
                'color_button_experiment': {
                    '__default__': 1,
                }
            }
        },
        False
    ),
])
def test_surge_color_button_min_value_zone(value, is_valid):
    p = configs.SURGE_COLOR_BUTTON_MIN_VALUE_ZONE
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
        {},
        True
    ),
    (
        {
            'moscow': {},
        },
        False
    ),
    (
        {
            'moscow': {
                'EXPERIMENT_NAME': 'ghost_moscow'
            }
        },
        True
    ),
    (
        {
            "moscow": {
                "EXPERIMENT_NAME": "ghost_moscow",
                "AFFECT_DISPATCH_CONFIG": True,
                "CONFIG_OVERRIDE": {
                    "SEARCH_SETTINGS_CLASSES": {
                        "__default__": {
                            "WAVE_THICKNESS_MINUTES": 1,
                            "MIN_URGENCY": 150,
                            "MAX_ROBOT_DISTANCE": 12000,
                            "MAX_ROBOT_TIME": 911,
                            "DYNAMIC_DISTANCE_A": 1.5,
                            "DYNAMIC_DISTANCE_B": 2.5,
                            "DYNAMIC_TIME_A": 0.66,
                            "DYNAMIC_TIME_B": 1,
                            "APPLY_ETA_ETR_IN_CAR_RANGING": False,
                            "K_ETR": 0.0,
                            "E_ETA": 0.0,
                            "E_ETR": 0.0,
                            "WAVE_THICKNESS_SECONDS": 120,
                            "SURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_GAP": 0,
                            "DISPATCH_GRADE_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_MAX_TARIFF_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_HOME_BONUS_SECONDS": 0,
                            "DISPATCH_REPOSITION_BONUS": {
                                "__default__": 0
                            },
                            "DISPATCH_DRIVER_TAGS_BONUSES": {
                                "__default__": 0
                            },
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
                            'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MIN": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_STEP": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MAX": 0,
                            "MAX_ROBOT_TIME_SCORE_ENABLED": False,
                            "MAX_ROBOT_TIME_SCORE": 10000
                        },
                        "econom": {
                            "WAVE_THICKNESS_MINUTES": 1,
                            "MIN_URGENCY": 251,
                            "MAX_ROBOT_DISTANCE": 12000,
                            "MAX_ROBOT_TIME": 911,
                            "DYNAMIC_DISTANCE_A": 1.5,
                            "DYNAMIC_DISTANCE_B": 2.5,
                            "DYNAMIC_TIME_A": 0.66,
                            "DYNAMIC_TIME_B": 1,
                            "APPLY_ETA_ETR_IN_CAR_RANGING": False,
                            "K_ETR": 0.0,
                            "E_ETA": 0.0,
                            "E_ETR": 0.0,
                            "WAVE_THICKNESS_SECONDS": 120,
                            "SURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_GAP": 0,
                            "DISPATCH_GRADE_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_MAX_TARIFF_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_HOME_BONUS_SECONDS": 0,
                            "DISPATCH_REPOSITION_BONUS": {
                                "__default__": 0
                            },
                            "DISPATCH_DRIVER_TAGS_BONUSES": {
                                "__default__": 0
                            },
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
                            'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MIN": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_STEP": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MAX": 0,
                            "MAX_ROBOT_TIME_SCORE_ENABLED": False,
                            "MAX_ROBOT_TIME_SCORE": 10000
                        }
                    }
                }
            },
            "spb": {
                "EXPERIMENT_NAME": "ghost_spb",
                "AFFECT_DISPATCH_CONFIG": True,
                "CONFIG_OVERRIDE": {
                    "SEARCH_SETTINGS_CLASSES": {
                        "econom": {
                            "WAVE_THICKNESS_MINUTES": 1,
                            "MIN_URGENCY": 251,
                            "MAX_ROBOT_DISTANCE": 12000,
                            "MAX_ROBOT_TIME": 911,
                            "DYNAMIC_DISTANCE_A": 1.5,
                            "DYNAMIC_DISTANCE_B": 2.5,
                            "DYNAMIC_TIME_A": 0.66,
                            "DYNAMIC_TIME_B": 1,
                            "APPLY_ETA_ETR_IN_CAR_RANGING": False,
                            "K_ETR": 0.0,
                            "E_ETA": 0.0,
                            "E_ETR": 0.0,
                            "WAVE_THICKNESS_SECONDS": 120,
                            "SURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_COEF": 0,
                            "ANTISURGE_BONUS_GAP": 0,
                            "DISPATCH_GRADE_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_MAX_TARIFF_BONUS_SECONDS": {
                                "__default__": 0
                            },
                            "DISPATCH_HOME_BONUS_SECONDS": 0,
                            "DISPATCH_REPOSITION_BONUS": {
                                "__default__": 0
                            },
                            "DISPATCH_DRIVER_TAGS_BONUSES": {
                                "__default__": 0
                            },
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P1': 0,
                            'NEW_DRIVER_BONUS_DURATION_DAYS_P2': 0,
                            'NEW_DRIVER_BONUS_VALUE_SECONDS': 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MIN": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_STEP": 0,
                            "AIRPORT_QUEUE_DISPATCH_BONUS_MAX": 0,
                            "MAX_ROBOT_TIME_SCORE_ENABLED": False,
                            "MAX_ROBOT_TIME_SCORE": 10000
                        }
                    }
                }
            }
        },
        True
    ),
])
def test_ghost_cities(value, is_valid):
    p = configs.GHOST_CITIES
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
            {},
            True
    ),
    (
            {
                'rus': 'yandex'
            },
            True
    ),
    (
            {
                'rus': 'yandex',
                'aze': 'uber'
            },
            True
    ),
    (
            {
                'rus': True
            },
            False
    ),
    (
            {
                'rus': 0
            },
            False
    ),
    (
            {
                'rus': []
            },
            False
    ),
    (
            {
                'ru': 'yandex'
            },
            False
    ),
    (
            {
                'RU': 'yandex'
            },
            False
    ),
])
def test_subventions_personal_sms_routes_param(value, is_valid):
    p = configs.SUBVENTIONS_PERSONAL_SMS_ROUTES
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
        {
            '__default__': {
                'warning': 600,
                'critical': 1800
            },
        },
        True
    ),
    (
        {
            '__default__': {'warning': 600, 'critical': 1800},
            'subventions': {'warning': 600, 'critical': 1800},
            'holded_subventions': {'warning': 600, 'critical': 1800},
            'promocode_compensations': {'warning': 600, 'critical': 1800},
            'commission_transactions': {'warning': 600, 'critical': 1800},
            'all_subventions': {'warning': 600, 'critical': 1800},
            'all_holded_subventions': {'warning': 600, 'critical': 1800},
            'order_commissions': {'warning': 600, 'critical': 1800},
            'subvention_commissions': {'warning': 600, 'critical': 1800},
            'holded_subvention_commissions': {'warning': 600, 'critical': 1800},
            'taximeter_balance_changes': {'warning': 600, 'critical': 1800},
            'childchair_rent_transactions': {'warning': 600, 'critical': 1800},
            'driver_workshifts': {'warning': 600, 'critical': 1800}
        },
        True
    ),
    (
        {},
        False
    ),
    (
        {
            'foobar': {'warning': 600, 'critical': 1800}
        },
        False
    ),
    (
        {
            '__default__': {}
        },
        False
    ),
    (
        {
            '__default__': {
                'warning': 600
            }
        },
            False
    ),
    (
        {
            '__default__': {
                'critical': 1800
            }
        },
        False
    ),
    (
        {
            '__default__': {
                'warning': 600,
                'critical': 1800,
                'extra': 12345
            }
        },
        False
    ),
])
def test_order_billings_delay_monitor_param(value, is_valid):
    p = configs.TLOGS_EVENTS_DELAY_THRESHOLDS
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,is_valid', [
    (
        {
            '__default__': [
                {
                    'group_name': 'econom',
                    'tariffs': [
                        'pool',
                        'econom',
                        'express'
                    ]
                }
            ]
        },
        True
    ),
    (
        {
            '__default__': {
                'econom': ['econom', 'express'],
                'posh': ['business', 'uberx']
            }
        },
        False
    ),
    (
        {
            '__default__': [
                {
                'group_name': 'econom',
                'tariffs': [123, 'express']
                }
            ]
        },
        False
    ),
    (
        {
            '__default__': [
                {
                    'group_name': 'econom',
                    'tariffs': ['no_such_tariff']
                }
            ]
        },
        False
    ),
    (
        {
            '__default__': [
                {
                    'typo': 'econom',
                    'tariffs': ['express']
                }
            ]
        },
        False
    ),
    (
        {
            'moscow': [
                {
                    'group_name': 'show-off',
                    'tariffs': ['vip', 'comfortplus'],
                }
            ]
        },
        True
    ),
])
def test_tariff_groups(value, is_valid):
    p = configs.ZONES_TARIFF_GROUPS
    if is_valid:
        p.validate(value)
    else:
        with pytest.raises(exceptions.ValidationError):
            p.validate(value)
