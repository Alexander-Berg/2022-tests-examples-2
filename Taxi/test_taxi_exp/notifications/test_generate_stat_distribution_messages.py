import pytest

from taxi_exp.lib import notifications


@pytest.mark.parametrize(
    'exp_body,messages',
    [
        pytest.param(
            {
                'match': {'predicate': {'init': {}, 'type': 'true'}},
                'clauses': [
                    {
                        'predicate': {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'arg_name': 'driver_id',
                                            'divisor': 100,
                                            'range_from': 0,
                                            'range_to': 10,
                                            'salt': '0',
                                        },
                                        'type': 'mod_sha1_with_salt',
                                    },
                                ],
                            },
                            'type': 'all_of',
                        },
                        'title': 'Первая клоза',
                        'value': {},
                    },
                    {
                        'predicate': {
                            'init': {
                                'arg_name': 'driver_id',
                                'divisor': 100,
                                'range_from': 10,
                                'range_to': 100,
                                'salt': '0',
                            },
                            'type': 'mod_sha1_with_salt',
                        },
                        'title': 'Вторая',
                        'value': {},
                    },
                ],
            },
            {
                'notification_type': 'segmentation_info',
                'details': {
                    'key_sets': [
                        {
                            'keyset': {
                                'arg_names': ['driver_id'],
                                'salt': '0',
                            },
                            'segments': [
                                {
                                    'range_from': 0.0,
                                    'range_to': 10.0,
                                    'title': 'Первая клоза',
                                },
                                {
                                    'range_from': 10.0,
                                    'range_to': 100.0,
                                    'title': 'Вторая',
                                },
                            ],
                        },
                    ],
                },
            },
            id='Ordinary report',
        ),
        pytest.param(
            {
                'match': {'predicate': {'init': {}, 'type': 'true'}},
                'clauses': [
                    {
                        'predicate': {
                            'init': {
                                'predicates': [
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
                            },
                            'type': 'all_of',
                        },
                        'title': 'Первая клоза',
                        'value': {},
                    },
                    {
                        'predicate': {
                            'init': {
                                'arg_name': 'driver_id',
                                'divisor': 100,
                                'range_from': 10,
                                'range_to': 90,
                                'salt': '0',
                            },
                            'type': 'mod_sha1_with_salt',
                        },
                        'title': 'Вторая',
                        'value': {},
                    },
                ],
            },
            {
                'message': 'Problems found: intersections found. See details.',
                'notification_type': 'segmentation_warning',
                'details': {
                    'key_sets': [
                        {
                            'keyset': {
                                'arg_names': ['driver_id'],
                                'salt': '0',
                            },
                            'segments': [
                                {
                                    'range_from': 0.0,
                                    'range_to': 100.0,
                                    'title': 'Первая клоза',
                                },
                                {
                                    'range_from': 10.0,
                                    'range_to': 90.0,
                                    'title': 'Вторая',
                                },
                            ],
                            'intersections': [['Первая клоза', 'Вторая']],
                        },
                    ],
                },
            },
            id='Ordinary report if has holes and intersections',
        ),
        pytest.param(
            {
                'match': {'predicate': {'init': {}, 'type': 'true'}},
                'clauses': [
                    {
                        'predicate': {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'arg_name': 'driver_id',
                                            'divisor': 100,
                                            'range_from': 0,
                                            'range_to': 100,
                                            'salt': '01',
                                        },
                                        'type': 'mod_sha1_with_salt',
                                    },
                                ],
                            },
                            'type': 'all_of',
                        },
                        'title': 'Первая клоза',
                        'value': {},
                    },
                    {
                        'predicate': {
                            'init': {
                                'arg_name': 'driver_id',
                                'divisor': 100,
                                'range_from': 10,
                                'range_to': 90,
                                'salt': '0',
                            },
                            'type': 'mod_sha1_with_salt',
                        },
                        'title': 'Вторая',
                        'value': {},
                    },
                ],
            },
            {
                'message': (
                    'Problems found: more than one set of arguments. '
                    'See details.'
                ),
                'notification_type': 'segmentation_warning',
                'details': {
                    'key_sets': [
                        {
                            'keyset': {
                                'arg_names': ['driver_id'],
                                'salt': '01',
                            },
                            'segments': [
                                {
                                    'range_from': 0.0,
                                    'range_to': 100.0,
                                    'title': 'Первая клоза',
                                },
                            ],
                        },
                        {
                            'keyset': {
                                'arg_names': ['driver_id'],
                                'salt': '0',
                            },
                            'segments': [
                                {
                                    'range_from': 10.0,
                                    'range_to': 90.0,
                                    'title': 'Вторая',
                                },
                            ],
                        },
                    ],
                },
            },
            id='multiple keysets',
        ),
        pytest.param(
            {
                'match': {'predicate': {'init': {}, 'type': 'true'}},
                'clauses': [
                    {
                        'predicate': {
                            'init': {
                                'arg_name': 'phone_id',
                                'set': ['539ea6a5e7e5b1f5397ce3c0'],
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        'title': '?????? phone_id',
                        'value': {},
                    },
                    {
                        'predicate': {
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
                        'title': 'clause one',
                        'value': {},
                    },
                ],
            },
            {
                'notification_type': 'segmentation_info',
                'details': {
                    'key_sets': [
                        {
                            'keyset': {
                                'arg_names': ['park_id', 'driver_profile_id'],
                                'salt': 'bs_orders_completed_experiment',
                            },
                            'segments': [
                                {
                                    'range_from': 0.0,
                                    'range_to': 100.0,
                                    'title': 'clause one',
                                },
                            ],
                        },
                    ],
                },
            },
            id='Report with composite argument',
        ),
    ],
)
def test_generate_stat_distribution_messages(exp_body, messages):
    assert (
        messages
        == notifications.segmentation_check.get_stat_distrib_notifications(
            exp_body,
        )
    )
