import datetime

import pytest


def da_headers(picker_id='1'):
    return {
        'Accept-Language': 'en',
        'X-Remote-IP': '12.34.56.78',
        'X-YaEda-CourierId': picker_id,
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'XYPro',
        'X-Request-Application-Version': '9.99 (9999)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'ios',
    }


def compare_db_with_expected_data(db_data, expected_data):
    for key, value in expected_data.items():
        if isinstance(db_data[key], datetime.datetime) and not isinstance(
                value, datetime.datetime,
        ):
            assert db_data[key].isoformat() == value
        else:
            assert db_data[key] == value


def orders_autostart_picking_config(delay=30):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_picker_orders_autostart_picking',
        consumers=['eats-picker-timers/autostart-picking'],
        clauses=[],
        default_value={
            'delay': delay,
            'enabled': True,
            'stq_retries': 3,
            'stq_timeout': 5,
        },
    )


AUTOSTART_APPLICATION = 'taximeter'
AUTOSTART_PLATFORM = 'android'
AUTOSTART_VERSION = '9.65 (5397)'


# pylint: disable=invalid-name
def timers_show_new_timers_config():
    return pytest.mark.experiments3(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_picker_timers_show_new_timers',
        consumers=['eats-picker-timers/show-new-timers'],
        clauses=[
            {
                'title': 'show autostart to front',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'application',
                                    'arg_type': 'string',
                                    'value': AUTOSTART_APPLICATION,
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'platform',
                                    'arg_type': 'string',
                                    'value': AUTOSTART_PLATFORM,
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'version',
                                    'arg_type': 'version',
                                    'value': '9.65.5397',
                                },
                            },
                        ],
                    },
                },
            },
        ],
        default_value={'enabled': False},
    )
