import pytest

from taxi_exp.lib import notifications


@pytest.mark.parametrize(
    'predicates_dict,intersections,cuts',
    [
        (
            [
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 0,
                            'range_to': 100,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(0, 100, 'first')],
        ),
        (
            [
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
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(10, 100, 'first')],
        ),
        pytest.param(
            [
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
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(10, 100, 'first')],
            id='with has_default_value',
        ),
        (
            [
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 0,
                            'range_to': 90,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(0, 90, 'first')],
        ),
        pytest.param(
            [
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 1000,
                            'range_from': 0,
                            'range_to': 903,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(0, 90.3, 'first')],
            id='divisor usage',
        ),
        (
            [
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
                    'clause': {'title': 'first'},
                },
            ],
            [],
            [(10, 90, 'first')],
        ),
        (
            [
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
                    'clause': {'title': 'first'},
                },
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 0,
                            'range_to': 10,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'second'},
                },
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 90,
                            'range_to': 100,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'third'},
                },
            ],
            [],
            [(0, 10, 'second'), (10, 90, 'first'), (90, 100, 'third')],
        ),
        (
            [
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 0,
                            'range_to': 100,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'first'},
                },
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 0,
                            'range_to': 10,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'second'},
                },
                {
                    'predicate': {
                        'init': {
                            'arg_name': 'driver_id',
                            'divisor': 100,
                            'range_from': 90,
                            'range_to': 100,
                            'salt': '0',
                        },
                        'type': 'mod_sha1_with_salt',
                    },
                    'clause': {'title': 'third'},
                },
            ],
            [('second', 'first'), ('first', 'third')],
            [(0, 10, 'second'), (0, 100, 'first'), (90, 100, 'third')],
        ),
    ],
)
def test_holes_and_intersections(predicates_dict, intersections, cuts):
    (
        _intersections,
        _cuts,
    ) = notifications.segmentation_check.check_distribution(predicates_dict)
    assert _intersections == intersections
    assert _cuts == cuts
