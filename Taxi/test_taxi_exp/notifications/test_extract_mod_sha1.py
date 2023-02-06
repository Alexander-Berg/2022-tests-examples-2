import pytest

from taxi_exp.lib import notifications


@pytest.mark.parametrize(
    'predicate,mod_sha1_list',
    [
        (
            {
                'init': {
                    'arg_name': 'driver_id',
                    'divisor': 100,
                    'range_from': 0,
                    'range_to': 100,
                    'salt': '0',
                },
                'type': 'mod_sha1_with_salt',
            },
            [
                {
                    'init': {
                        'arg_name': 'driver_id',
                        'divisor': 100,
                        'range_from': 0,
                        'range_to': 100,
                        'salt': '0',
                    },
                    'type': 'mod_sha1_with_salt',
                },
            ],
        ),
        (
            {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'country',
                                'set': ['rus', 'blr'],
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'arg_name': 'phone_id',
                                'divisor': 100,
                                'range_from': 0,
                                'range_to': 100,
                                'salt': 'salt_123',
                            },
                            'type': 'mod_sha1_with_salt',
                        },
                    ],
                },
                'type': 'all_of',
            },
            [
                {
                    'init': {
                        'arg_name': 'phone_id',
                        'divisor': 100,
                        'range_from': 0,
                        'range_to': 100,
                        'salt': 'salt_123',
                    },
                    'type': 'mod_sha1_with_salt',
                },
            ],
        ),
        (
            {
                'init': {
                    'arguments': [
                        {'arg_name': 'park_id'},
                        {'arg_name': 'driver_profile_id'},
                    ],
                    'divisor': 100,
                    'range_from': 0,
                    'range_to': 100,
                    'salt': 'bs_orders_completed_experiment',
                },
                'type': 'mod_sha1_with_salt',
            },
            [
                {
                    'init': {
                        'arguments': [
                            {'arg_name': 'park_id'},
                            {'arg_name': 'driver_profile_id'},
                        ],
                        'divisor': 100,
                        'range_from': 0,
                        'range_to': 100,
                        'salt': 'bs_orders_completed_experiment',
                    },
                    'type': 'mod_sha1_with_salt',
                },
            ],
        ),
        (
            {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arguments': [
                                    {
                                        'arg_name': 'request_timestamp',
                                        'round_up': 600000,
                                    },
                                    {'arg_name': 'phone_id'},
                                ],
                                'divisor': 100,
                                'range_from': 50,
                                'range_to': 100,
                                'salt': 'buffer_bonus_for_order',
                            },
                            'type': 'mod_sha1_with_salt',
                        },
                        {
                            'init': {
                                'arg_name': 'tariff_zone',
                                'set': [
                                    'moscow',
                                    'spb',
                                    'ekb',
                                    'rostovondon',
                                    'penza',
                                    'samara',
                                    'kazan',
                                    'novosibirsk',
                                    'tumen',
                                    'omsk',
                                    'volgograd',
                                    'orenburg',
                                    'nizhnynovgorod',
                                    'krasnoyarsk',
                                    'izhevsk',
                                ],
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'arg_name': 'payment_option',
                                'arg_type': 'string',
                                'value': 'corp',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            [
                {
                    'init': {
                        'arguments': [
                            {
                                'arg_name': 'request_timestamp',
                                'round_up': 600000,
                            },
                            {'arg_name': 'phone_id'},
                        ],
                        'divisor': 100,
                        'range_from': 50,
                        'range_to': 100,
                        'salt': 'buffer_bonus_for_order',
                    },
                    'type': 'mod_sha1_with_salt',
                },
            ],
        ),
    ],
)
def test_extract_mod_sha1(predicate, mod_sha1_list):
    assert mod_sha1_list == list(
        # pylint: disable=protected-access
        notifications.segmentation_check._extract_mod_sha1(predicate),
    )
