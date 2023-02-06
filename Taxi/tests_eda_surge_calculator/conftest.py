# pylint: disable=wildcard-import, unused-wildcard-import, import-error

from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
from eda_surge_calculator_plugins import *  # noqa: F403 F401
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )


@pytest.fixture(autouse=True)
def places_static(experiments3):
    experiments3.add_config(
        consumers=['eda-surge-calculator/place'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': 1,
                    },
                    'type': 'eq',
                },
                'value': {
                    'settings': {
                        'limit': 100,
                        'max_distance': 1000,
                        'damper_x': 2,
                        'damper_y': 1.75,
                        'time_quants': 3,
                        'cond_free_threshold': 1200,
                        'cond_busy_threshold': 300,
                        'c1': [-1.9936, -1.5553, -1.1169],
                        'c2': [1.4147, 1.4413, 1.468],
                        'additional_time_percents': [0, 10, 15, 60],
                        'delivery_fee': [100, 120, 160, 200],
                    },
                    'pipelines': ['calc_surge'],
                },
            },
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': 2,
                    },
                    'type': 'eq',
                },
                'value': {
                    'settings': {
                        'limit': 100,
                        'max_distance': 1000,
                        'damper_x': 1,
                        'damper_y': 1,
                        'time_quants': 2,
                        'cond_free_threshold': 200,
                        'cond_busy_threshold': 300,
                        'c1': [-1.9936, -1.5553, -1.1169],
                        'c2': [0.9147, 0.9413, 0.968],
                        'additional_time_percents': [0, 10, 15, 60],
                        'delivery_fee': [100, 120, 160, 200],
                    },
                    'pipelines': ['calc_surge'],
                },
            },
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'arg_name': 'place_id',
                        'arg_type': 'int',
                        'value': 3,
                    },
                    'type': 'eq',
                },
                'value': {
                    'settings': {
                        'limit': 100,
                        'max_distance': 1000,
                        'damper_x': 1,
                        'damper_y': 1,
                        'time_quants': 2,
                        'cond_free_threshold': 200,
                        'cond_busy_threshold': 300,
                        'c1': [-1.9936, -1.5553, -1.1169],
                        'c2': [0.9147, 0.9413, 0.968],
                        'additional_time_percents': [0, 10, 15, 60],
                        'delivery_fee': [100, 120, 160, 200],
                    },
                    'pipelines': ['calc_surge'],
                },
            },
        ],
        name='eats_surge_places_settings_by_place',
    )


@pytest.fixture(autouse=True)
def eats_core_surge(mockserver):
    @mockserver.json_handler('/eats-core-surge/v1/surge/store-info')
    def _store_info_handler(request):
        return {
            'oldDeltaRange': {
                'start': '2018-12-25T11:30:35.000Z',
                'end': '2018-12-25T11:40:35.000Z',
            },
            'newDeltaRange': {
                'start': '2018-12-25T11:30:35.000Z',
                'end': '2018-12-25T11:40:35.000Z',
            },
            'deltas': [
                {
                    'placeId': 1,
                    'regionId': 1,
                    'zoneId': 0,
                    'oldCouriersArrivalTime': 4,
                    'newCouriersArrivalTime': 5,
                },
                {
                    'placeId': 2,
                    'regionId': 2,
                    'zoneId': 0,
                    'oldCouriersArrivalTime': 3,
                    'newCouriersArrivalTime': 4,
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-core-surge/v1/export/settings/surge-regions',
    )
    def _surge_regions_handler(request):
        return {
            'payload': [
                {
                    'id': 1,
                    'regionId': 1,
                    'marketplaceEnabled': True,
                    'nativeEnabled': True,
                    'storeEnabled': True,
                    'createdAt': '2018-10-05T12:20:12+03:00',
                    'damperX': 1,
                    'damperY': 1,
                    'orderDeliveryDelta': -999,
                    'calculatorType': 'manual_threshold_aware',
                    'minimalCourierCount': 1,
                    'oldDeltaWindowWeight': 0.4,
                    'couriersArrivalLimitTime': 4,
                },
                {
                    'id': 2,
                    'regionId': 2,
                    'marketplaceEnabled': True,
                    'nativeEnabled': True,
                    'storeEnabled': True,
                    'createdAt': '2018-10-05T12:20:12+03:00',
                    'damperX': 1,
                    'damperY': 1,
                    'orderDeliveryDelta': -999,
                    'calculatorType': 'manual_threshold_aware',
                    'minimalCourierCount': 3,
                    'oldDeltaWindowWeight': 0.3,
                    'couriersArrivalLimitTime': 5,
                },
            ],
        }

    @mockserver.json_handler('/eats-core-surge/v1/surge/awaiting-assignment')
    def _awaiting_assignment_handler(request):
        region_id = request.json['filter']['regionIds'][0]
        if region_id == 1:
            return {
                'payload': [
                    {
                        'source': {
                            'id': 1,
                            'location': {'latitude': 10.0, 'longitude': 10.0},
                        },
                        'destination': {
                            'location': {
                                'latitude': 10.0012,
                                'longitude': 10.0012,
                            },
                        },
                        'estimatedPreparationFinishedAt': (
                            '2020-04-12T12:05:00+03:00'
                        ),
                    },
                ],
                'meta': {'count': 1},
            }
        return {'payload': [], 'meta': {'count': 0}}

    @mockserver.json_handler('/eats-core-surge/v1/surge/supply')
    def _supply_handler(request):
        region_id = request.json['filter']['regionIds'][0]
        if region_id == 1:
            return {
                'payload': [
                    {
                        'courierId': 11,
                        'regionId': 1,
                        'groupId': 12,
                        'activeDeliveries': [
                            {
                                'source': {
                                    'id': 23,
                                    'location': {
                                        'latitude': 10.0,
                                        'longitude': 10.0,
                                    },
                                },
                                'destination': {
                                    'location': {
                                        'latitude': 10.001,
                                        'longitude': 10.001,
                                    },
                                },
                                'estimatedPreparationFinishedAt': (
                                    '2020-04-12T11:50:00+03:00'
                                ),
                                'estimatedDeliveredAt': (
                                    '2020-04-12T12:12:00+03:00'
                                ),
                            },
                            {
                                'source': {
                                    'id': 23,
                                    'location': {
                                        'latitude': 10.0,
                                        'longitude': 10.0,
                                    },
                                },
                                'destination': {
                                    'location': {
                                        'latitude': 10.001,
                                        'longitude': 10.001,
                                    },
                                },
                                'estimatedPreparationFinishedAt': (
                                    '2020-04-12T11:50:00+03:00'
                                ),
                                'estimatedDeliveredAt': (
                                    '2020-04-12T12:00:00+03:00'
                                ),
                            },
                        ],
                    },
                    {'courierId': 22, 'regionId': 1, 'activeDeliveries': []},
                ],
                'meta': {'count': 2},
            }
        if region_id == 2:
            return {
                'payload': [
                    {'courierId': 33, 'regionId': 2, 'activeDeliveries': []},
                ],
                'meta': {'count': 1},
            }
        return {'payload': [], 'meta': {'count': 0}}

    @mockserver.json_handler('/eats-core-surge/v1/surge/courier-activity')
    def _courier_activity_handler(request):
        return {
            'payload': [
                {
                    'courierId': 11,
                    'regionId': 1,
                    'activeDeliveries': [
                        {
                            'source': {
                                'id': 23,
                                'location': {
                                    'latitude': 10.0,
                                    'longitude': 10.0,
                                },
                            },
                            'destination': {
                                'location': {
                                    'latitude': 10.001,
                                    'longitude': 10.001,
                                },
                            },
                            'estimatedPreparationFinishedAt': (
                                '2020-04-12T11:50:00+03:00'
                            ),
                            'estimatedDeliveredAt': (
                                '2020-04-12T12:12:00+03:00'
                            ),
                            'status': 'taken',
                        },
                        {
                            'source': {
                                'id': 23,
                                'location': {
                                    'latitude': 10.0,
                                    'longitude': 10.0,
                                },
                            },
                            'destination': {
                                'location': {
                                    'latitude': 10.001,
                                    'longitude': 10.001,
                                },
                            },
                            'estimatedPreparationFinishedAt': (
                                '2020-04-12T11:50:00+03:00'
                            ),
                            'estimatedDeliveredAt': (
                                '2020-04-12T12:00:00+03:00'
                            ),
                            'status': 'taken',
                        },
                    ],
                },
                {'courierId': 22, 'regionId': 1, 'activeDeliveries': []},
            ],
            'meta': {'count': 2},
        }

    @mockserver.json_handler('/eats-core-surge/v1/surge/logistic-groups')
    def _surge_logistic_groups(request):
        return {
            'payload': [
                {
                    'id': 12,
                    'places': [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                    ],
                    'metaGroupId': None,
                },
            ],
            'meta': {'count': 1},
        }


@pytest.fixture(autouse=True)
def mock_orders_demand(request, mockserver):
    # if not request.node.ger_closest_marker('custom_orders_demand'):
    @mockserver.json_handler('/grocery-wms/api/external/orders/v1/demand')
    def _orders_demand(request):
        return {'cursor': 'now', 'orders': []}


@pytest.fixture(autouse=True)
def eats_couriers_bindings_journal(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/eats-couriers-binding/updates',
    )
    def _eats_couriers_bindings_journal(request):
        if not request.args['last_known_revision']:
            return {
                'binding': [],
                'last_known_revision': '1',
                'has_next': True,
            }
        if request.args['last_known_revision'] == '1':
            return {
                'binding': [
                    {
                        'taxi_id': 'dbid0_uuid0',
                        'eats_id': '22',
                        'courier_app': 'taximeter',
                    },
                    {
                        'taxi_id': 'dbid0_uuid1',
                        'eats_id': 'external_id_2',
                        'courier_app': 'eats',
                    },
                    {
                        'taxi_id': 'dbid0_uuid2',
                        'eats_id': '108',
                        'courier_app': 'taximeter',
                    },
                ],
                'last_known_revision': '2',
                'has_next': True,
            }
        return {'binding': [], 'last_known_revision': '2', 'has_next': False}


@pytest.fixture(name='overlord_catalog', autouse=True)
def mock_overlord_catalog(mockserver):
    depots = [
        {
            'depot_id': 'store11xx',
            'legacy_depot_id': '1',
            'country_iso3': 'RUS',
            'country_iso2': 'RU',
            'region_id': 223,
            'timezone': 'Europe/Moscow',
            'position': {'location': [10.0, 10.0]},
            'phone_number': '+78007700461',
            'currency': 'RUB',
            'tin': '123456',
            'address': 'depot address 1',
            'company_id': 'company-id',
            'company_type': 'yandex',
            'detailed_zones': [],
        },
        {
            'depot_id': 'store22xx',
            'legacy_depot_id': '2',
            'country_iso3': 'RUS',
            'country_iso2': 'RU',
            'region_id': 223,
            'timezone': 'Europe/Moscow',
            'position': {'location': [11.0, 11.0]},
            'phone_number': '+78007700462',
            'currency': 'RUB',
            'tin': '223456',
            'address': 'depot address',
            'company_id': 'company-id',
            'company_type': 'yandex',
            'detailed_zones': [],
        },
    ]

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/depots')
    def _mock_internal_depots(request):
        return {'depots': depots, 'errors': []}


@pytest.fixture(autouse=True)
@pytest.mark.yt(dyn_table_data=['yt_orders_empty.yaml'])
def yt_orders_empty():
    pass
