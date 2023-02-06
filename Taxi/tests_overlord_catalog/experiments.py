import pytest

# pylint: disable=invalid-name
zone_priority_config_default = pytest.mark.experiments3(
    name='zone_priority',
    consumers=['grocery-depots-internal/zone_priority'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'pedestrian': 100,
        'yandex_taxi': 10,
        'yandex_taxi_remote': 5,
        'yandex_taxi_night': 1,
        'rover': 0,
    },
    is_config=True,
)

zone_priority_config_taxi_most_priority = pytest.mark.experiments3(
    name='zone_priority',
    consumers=['grocery-depots-internal/zone_priority'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'pedestrian': 10,
        'yandex_taxi': 100,
        'yandex_taxi_remote': 5,
        'yandex_taxi_night': 1,
        'rover': 0,
    },
    is_config=True,
)

overlord_catalog_opened_depots_params = pytest.mark.experiments3(
    name='overlord_catalog_opened_depots_params',
    consumers=['overlord-catalog/opened-depots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'One depot',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': '123456',
                },
            },
            'value': {'enabled': True, 'start': 19, 'end': 21},
        },
        {
            'title': 'Another depot',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': '654321',
                },
            },
            'value': {'enabled': False, 'start': 12, 'end': 14},
        },
    ],
    default_value={'enabled': True, 'start': 10, 'end': 15},
    is_config=True,
)


def _make_overlord_depot_hidings_experiment(depot_hidings):
    return pytest.mark.experiments3(
        name='overlord_depots_hidings',
        consumers=['grocery-depots-internal/depots_hidings'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'depots_hidings': depot_hidings},
        is_config=True,
    )


def hide_depot(depot_id):
    return _make_overlord_depot_hidings_experiment(
        [{'depot_id': depot_id, 'hidden': True}],
    )
