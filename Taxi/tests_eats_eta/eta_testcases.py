# pylint: disable=import-error,too-many-lines
import ast
import datetime

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

from . import utils


DB_ORDERS_UPDATE_OFFSET = 5
CARGO_ROUTE_ETA_TTL = 60
CARGO_COURIER_POSITION_TTL = 120
RETAIL_INFO_TTL = 60
EATS_ETA_FALLBACKS = {
    'router_type': 'car',
    'router_mode': 'best',
    'router_jams': 'jams',
    'router_tolls': 'tolls',
    'courier_speed': 10,
    'courier_arrival_duration': 1000,
    'place_cargo_waiting_time': 300,
    'delivery_duration': 1200,
    'cooking_duration': 300,
    'estimated_picking_time': 1200,
    'picking_duration': 1800,
    'picking_queue_length': 600,
    'place_waiting_duration': 300,
    'customer_waiting_duration': 300,
    'picker_waiting_time': 100,
    'picker_dispatching_time': 100,
    'minimal_remaining_duration': 60,
}


def mock_car_router(eta_testcases_context, time, distance):
    def _proto_driving_summary(time, distance):
        response = ProtoDrivingSummary.Summaries()
        item = response.summaries.add()
        item.weight.time.value = time
        item.weight.time.text = ''
        item.weight.time_with_traffic.value = time
        item.weight.time_with_traffic.text = ''
        item.weight.distance.value = distance
        item.weight.distance.text = ''
        item.flags.blocked = False
        return response.SerializeToString()

    @eta_testcases_context.mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        assert request.method == 'GET'
        if eta_testcases_context.fallbacks['router_tolls'] == 'no_tolls':
            assert request.query['avoid'] == 'tolls'
        else:
            assert 'avoid' not in request.query
        if eta_testcases_context.fallbacks['router_jams'] == 'nojams':
            assert request.query['mode'] == 'nojams'
        else:
            assert (
                request.query['mode']
                == eta_testcases_context.fallbacks['router_mode']
            )
        return eta_testcases_context.mockserver.make_response(
            response=_proto_driving_summary(time, distance),
            status=200,
            content_type='application/x-protobuf',
        )


@pytest.fixture(name='eta_testcases_context')
def _eta_testcases_context(
        now_utc,
        load_json,
        cargo,
        pickers,
        revisions,
        mockserver,
        request,
        taxi_config,
):
    class Context:
        def __init__(self):
            self.now_utc = now_utc
            self.load_json = load_json
            self.cargo = cargo
            self.mockserver = mockserver
            self.taxi_config = taxi_config
            self.fallbacks = EATS_ETA_FALLBACKS
            redis_testcase = request.node.get_closest_marker('redis_testcase')
            self.redis_testcase = (
                redis_testcase.args[0] if redis_testcase else False
            )
            update_mode = request.node.get_closest_marker('update_mode')
            self.update_mode = (
                update_mode.args[0] if update_mode else 'update_expired'
            )
            self.force_first_update = self.update_mode != 'update_expired'
            self.force_update = self.update_mode == 'force_update'
            self.pickers = pickers
            self.revisions = revisions

    return Context()


# pylint: disable=invalid-name
def courier_arrival_duration_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'pickup',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': None,
                        'status': 'skipped',
                    },
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'assigned',
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-1',
                    'claim_status': 'new',
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': None,
                        'status': 'finished',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'cancelled',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-1',
                    'claim_status': 'new',
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': None,
                        'status': 'skipped',
                    },
                },
            },
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'vehicle',
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(22.33,44.55)',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=3000)
                    ),
                    'claim_id': 'claim-0',
                    'claim_status': 'performer_found',
                    'claim_created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=4000)
                    ),
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'batch_info': {
                        'delivery_order': [
                            {'claim_id': 'claim-0', 'order': 1},
                            {'claim_id': 'claim-1', 'order': 2},
                        ],
                    },
                    'batch_info_updated_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': None,
                        'status': 'in_progress',
                        'metrics': {'update_cargo_info': 1},
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def courier_arrival_duration_fallback(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'courier_arrival_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def courier_arrival_duration_has_cargo_eta(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'delivery_type': 'native',
                    'place_visit_status': 'visited',
                    'place_visited_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=1000)
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=3000)
                    ),
                    'claim_created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=4000)
                    ),
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': datetime.timedelta(seconds=3000),
                        'status': 'finished',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'delivery_type': 'native',
                    'place_visit_status': 'pending',
                    'place_visited_at': (
                        eta_testcases_context.now_utc
                        + datetime.timedelta(seconds=1000)
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=4000)
                    ),
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': datetime.timedelta(seconds=5000),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def courier_arrival_duration_has_courier_position(eta_testcases_context):
    mock_car_router(eta_testcases_context, 2500, 2500)

    @eta_testcases_context.mockserver.handler(
        '/maps-pedestrian-router/pedestrian/v2/summary',
    )
    def _mock_route_jams(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    return {
        'orders': [
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'vehicle',
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(22.33,44.55)',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=3000)
                    ),
                    'claim_created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=4000)
                    ),
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': datetime.timedelta(seconds=6500),
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
            },
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'pedestrian',
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.54)',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=1000)
                    ),
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': datetime.timedelta(
                            seconds=11119.507973463116
                            // eta_testcases_context.fallbacks['courier_speed']
                            + 1000,
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
            },
        ],
        'places': [{'id': 1, 'location': '(11.22,33.44)'}],
    }


def picking_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {'order_type': 'native', 'order_status': 'confirmed'},
                'expected_estimations': {
                    'picking_duration': {'value': None, 'status': 'skipped'},
                    'picked_up_at': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'complete',
                    'picking_status': 'complete',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'picking_duration': {'value': None, 'status': 'finished'},
                    'picked_up_at': {'value': None, 'status': 'finished'},
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'picking_status': 'cancelled',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'picking_duration': {'value': None, 'status': 'skipped'},
                    'picked_up_at': {'value': None, 'status': 'skipped'},
                },
            },
        ],
        'places': [],
    }


def picking_fallback(eta_testcases_context):
    picking_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['picking_duration'],
    )
    minimal_remaining_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['minimal_remaining_duration'],
    )
    return {
        'orders': (
            [
                {
                    'order': {
                        'order_type': order_type,
                        'order_status': order_status,
                        'created_at': (
                            eta_testcases_context.now_utc - created_at_offset
                        ),
                        'picking_starts_at': None,
                        'picking_status': 'new',
                        'retail_order_created_at': (
                            eta_testcases_context.now_utc - created_at_offset
                        ),
                        'picking_duration': None,
                        'picking_duration_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                        'picking_start_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                    },
                    'expected_estimations': {
                        'picking_duration': {
                            'value': max(
                                picking_duration,
                                created_at_offset + minimal_remaining_duration,
                            ),
                            'status': estimation_status,
                            'source': (
                                'fallback'
                                if order_type == 'retail'
                                else 'service'
                            ),
                        },
                        'picked_up_at': {
                            'value': eta_testcases_context.now_utc + max(
                                picking_duration - created_at_offset,
                                minimal_remaining_duration,
                            ),
                            'status': estimation_status,
                            'source': (
                                'fallback'
                                if order_type == 'retail'
                                else 'service'
                            ),
                        },
                    },
                    'metrics': {
                        'update_retail_info': int(order_type == 'retail'),
                    },
                }
                for order_type, estimation_status in (
                    ('retail', 'not_started'),
                    ('shop', 'in_progress'),
                )
                for order_status in ('sent', 'confirmed')
                for created_at_offset in (
                    datetime.timedelta(seconds=0),
                    picking_duration * 2,
                )
            ]
            + [
                {
                    'order': {
                        'order_type': 'retail',
                        'order_status': 'confirmed',
                        'created_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                        'picking_starts_at': (
                            eta_testcases_context.now_utc
                            - picking_start_offset
                        ),
                        'picking_status': 'picking',
                        'retail_order_created_at': (
                            eta_testcases_context.now_utc
                        ),
                        'picking_duration': datetime.timedelta(hours=1),
                        'picking_duration_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                        'picking_start_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                    },
                    'expected_estimations': {
                        'picking_duration': {
                            'value': max(
                                picking_duration,
                                picking_start_offset
                                + minimal_remaining_duration,
                            ),
                            'status': 'in_progress',
                            'source': 'fallback',
                        },
                        'picked_up_at': {
                            'value': eta_testcases_context.now_utc + max(
                                picking_duration - picking_start_offset,
                                minimal_remaining_duration,
                            ),
                            'status': 'in_progress',
                            'source': 'fallback',
                        },
                    },
                    'metrics': {'update_retail_info': 1},
                }
                for picking_start_offset in (
                    datetime.timedelta(seconds=0),
                    picking_duration * 2,
                )
            ]
            + [
                {
                    'order': {
                        'order_type': 'retail',
                        'order_status': 'created',
                        'created_at': eta_testcases_context.now_utc,
                        'picking_starts_at': None,
                        'picking_status': 'new',
                        'retail_order_created_at': (
                            eta_testcases_context.now_utc
                        ),
                        'picking_duration': None,
                        'picking_duration_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                        'picking_start_updated_at': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(days=1)
                        ),
                    },
                    'expected_estimations': {
                        'picking_duration': {
                            'value': picking_duration,
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                        'picked_up_at': {
                            'value': (
                                eta_testcases_context.now_utc
                                + picking_duration
                            ),
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                    },
                    'metrics': {'update_retail_info': 0},
                },
            ]
        ),
        'places': [],
    }


def picking_retail(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                    'picking_starts_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=2)
                    ),
                    'picking_status': 'picking',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'picking_duration': datetime.timedelta(hours=1),
                    'picking_duration_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'picking_start_updated_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': datetime.timedelta(
                            hours=2,
                            seconds=eta_testcases_context.fallbacks[
                                'minimal_remaining_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                    'picked_up_at': {
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'minimal_remaining_duration'
                                ],
                            )
                        ),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                    'picking_starts_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=2)
                    ),
                    'picking_status': 'complete',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'picking_duration': datetime.timedelta(hours=1),
                    'picking_duration_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'picking_start_updated_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': datetime.timedelta(hours=1),
                        'status': 'finished',
                        'source': 'service',
                    },
                    'picked_up_at': {
                        'value': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(hours=1)
                        ),
                        'status': 'finished',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                    'picking_starts_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=2)
                    ),
                    'picking_status': 'complete',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'picking_duration': datetime.timedelta(hours=1),
                    'picking_duration_updated_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                    'picking_start_updated_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': datetime.timedelta(hours=1),
                        'status': 'finished',
                        'source': 'service',
                    },
                    'picked_up_at': {
                        'value': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(hours=1)
                        ),
                        'status': 'finished',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(days=1)
                    ),
                    'picking_starts_at': eta_testcases_context.now_utc,
                    'picking_status': 'picking',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'picking_duration': datetime.timedelta(hours=1),
                    'picking_duration_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'picking_start_updated_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': datetime.timedelta(hours=1),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                    'picked_up_at': {
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(hours=1)
                        ),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def cooking_duration_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {'order_type': 'retail'},
                'expected_estimations': {
                    'cooking_duration': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {'order_type': 'shop'},
                'expected_estimations': {
                    'cooking_duration': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {
                    'order_type': 'native',
                    'order_status': 'taken',
                    'delivery_started_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'cooking_duration': {'value': None, 'status': 'finished'},
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def cooking_duration_fallback(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {'order_type': 'native'},
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'cooking_duration'
                            ],
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                },
            },
            {
                'order': {'order_type': 'native', 'order_status': 'confirmed'},
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'cooking_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'fast_food',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=1000)
                    ),
                },
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'cooking_duration'
                            ],
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'fast_food',
                    'order_status': 'confirmed',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=1000)
                    ),
                },
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'cooking_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'native',
                    'created_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(hours=1000)
                    ),
                },
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'cooking_duration'
                            ],
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def cooking_duration_order_cooking_time(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'order_type': 'native',
                    'order_status': 'confirmed',
                    'cooking_time': datetime.timedelta(seconds=200),
                    'created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(seconds=200),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def cooking_duration_place_preparation(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'order_type': 'native',
                    'created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'cooking_duration': {
                        'value': datetime.timedelta(seconds=600),
                        'status': 'not_started',
                        'source': 'partial_fallback',
                    },
                },
            },
        ],
        'places': [
            {
                'id': 1,
                'average_preparation': datetime.timedelta(seconds=100),
                'extra_preparation': datetime.timedelta(seconds=500),
            },
        ],
    }


def courier_arrival_at_nullopt(eta_testcases_context):
    testcase = courier_arrival_duration_nullopt(eta_testcases_context)
    for order in testcase['orders']:
        expected_estimations = order['expected_estimations']
        expected_estimations['courier_arrival_at'] = dict(
            expected_estimations['courier_arrival_duration'], value=None,
        )

    return testcase


# pylint: disable=invalid-name
def courier_arrival_at_courier_arrival_duration(eta_testcases_context):
    courier_arrival_duration_order = {
        'claim_id': 'claim-0',
        'shipping_type': 'delivery',
        'order_status': 'confirmed',
        'picking_status': 'assigned',
        'retail_order_created_at': eta_testcases_context.now_utc,
        'created_at': eta_testcases_context.now_utc,
        'claim_created_at': eta_testcases_context.now_utc - datetime.timedelta(
            seconds=4000,
        ),
    }
    courier_arrival_duration_estimations = {
        'courier_arrival_duration': {
            'value': datetime.timedelta(
                seconds=max(
                    eta_testcases_context.fallbacks[
                        'courier_arrival_duration'
                    ],
                    4000
                    + eta_testcases_context.fallbacks[
                        'minimal_remaining_duration'
                    ],
                ),
            ),
            'status': 'in_progress',
            'source': 'fallback',
        },
    }

    return {
        'orders': [
            {
                'order': dict(
                    courier_arrival_duration_order, order_type='fast_food',
                ),
                'expected_estimations': dict(
                    courier_arrival_duration_estimations,
                    courier_arrival_at={
                        'value': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(seconds=4000)
                            + datetime.timedelta(
                                seconds=max(
                                    eta_testcases_context.fallbacks[
                                        'courier_arrival_duration'
                                    ],
                                    4000
                                    + eta_testcases_context.fallbacks[
                                        'minimal_remaining_duration'
                                    ],
                                ),
                            )
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                ),
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


def courier_arrival_at_pickup_arrived_at(eta_testcases_context):
    order = {
        'claim_id': 'claim-0',
        'claim_status': 'pickup_arrived',
        'shipping_type': 'delivery',
        'order_status': 'confirmed',
        'picking_status': 'assigned',
        'retail_order_created_at': eta_testcases_context.now_utc,
        'created_at': eta_testcases_context.now_utc,
        'claim_created_at': eta_testcases_context.now_utc - datetime.timedelta(
            seconds=4000,
        ),
        'pickup_arrived_at': (
            eta_testcases_context.now_utc - datetime.timedelta(minutes=1)
        ),
        'place_visit_status': 'arrived',
        'place_visited_at': eta_testcases_context.now_utc,
        'place_point_eta_updated_at': eta_testcases_context.now_utc,
    }
    return {
        'orders': [
            {
                'order': order,
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': (
                            order['pickup_arrived_at']
                            - order['claim_created_at']
                        ),
                        'status': 'finished',
                        'source': 'service',
                    },
                    'courier_arrival_at': {
                        'value': order['pickup_arrived_at'],
                        'status': 'finished',
                        'source': 'service',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def courier_arrival_at_native_cooking_duration(eta_testcases_context):
    courier_arrival_duration_order = {
        'claim_id': 'claim-0',
        'shipping_type': 'delivery',
        'order_status': 'confirmed',
        'picking_status': 'assigned',
        'retail_order_created_at': eta_testcases_context.now_utc,
        'created_at': eta_testcases_context.now_utc,
    }
    courier_arrival_duration_estimations = {
        'courier_arrival_duration': {
            'value': datetime.timedelta(
                seconds=eta_testcases_context.fallbacks[
                    'courier_arrival_duration'
                ],
            ),
            'status': 'in_progress',
            'source': 'fallback',
        },
    }

    return {
        'orders': [
            {
                'order': dict(
                    courier_arrival_duration_order,
                    order_type='native',
                    customer_point_eta_updated_at=(
                        eta_testcases_context.now_utc
                    ),
                    customer_visited_at=eta_testcases_context.now_utc,
                    place_point_eta_updated_at=None,
                    courier_position_updated_at=None,
                    cooking_time=datetime.timedelta(hours=2),
                ),
                'expected_estimations': dict(
                    courier_arrival_duration_estimations,
                    courier_arrival_at={
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(hours=2)
                        ),
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                ),
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


def cooking_finishes_at_nullopt(eta_testcases_context):
    testcase = cooking_duration_nullopt(eta_testcases_context)
    for i, order in enumerate(testcase['orders']):
        order['order']['claim_id'] = f'claim-{i}'
        expected_estimations = order['expected_estimations']
        expected_estimations['cooking_finishes_at'] = dict(
            expected_estimations['cooking_duration'], value=None,
        )
    return testcase


# pylint: disable=invalid-name
def cooking_finishes_at_cooking_duration(eta_testcases_context):
    courier_duration_order = {'order_type': 'native'}
    courier_duration_estimations = {
        'cooking_duration': {
            'value': datetime.timedelta(
                seconds=eta_testcases_context.fallbacks['cooking_duration'],
            ),
            'status': 'not_started',
            'source': 'fallback',
        },
    }

    return {
        'orders': [
            {
                'order': dict(courier_duration_order, shipping_type='pickup'),
                'expected_estimations': dict(
                    courier_duration_estimations,
                    cooking_finishes_at={
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'cooking_duration'
                                ],
                            )
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                ),
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def cooking_finishes_at_courier_arrival_duration(eta_testcases_context):
    courier_duration_and_courier_arrival_duration_order = {
        'order_type': 'native',
        'shipping_type': 'delivery',
        'order_status': 'created',
        'picking_status': 'assigned',
        'retail_order_created_at': eta_testcases_context.now_utc,
    }
    cooking_duration_and_courier_arrival_duration_estimations = {
        'cooking_duration': {
            'value': datetime.timedelta(
                seconds=eta_testcases_context.fallbacks['cooking_duration'],
            ),
            'status': 'not_started',
            'source': 'fallback',
        },
        'courier_arrival_duration': {
            'value': datetime.timedelta(
                seconds=eta_testcases_context.fallbacks[
                    'courier_arrival_duration'
                ],
            ),
            'status': 'in_progress',
            'source': 'fallback',
        },
    }

    return {
        'orders': [
            {
                'order': dict(
                    courier_duration_and_courier_arrival_duration_order,
                    order_type='fast_food',
                ),
                'expected_estimations': dict(
                    cooking_duration_and_courier_arrival_duration_estimations,
                    cooking_finishes_at={
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'cooking_duration'
                                ],
                            )
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'courier_arrival_duration'
                                ],
                            )
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                ),
            },
            {
                'order': dict(
                    courier_duration_and_courier_arrival_duration_order,
                    order_type='native',
                ),
                'expected_estimations': dict(
                    cooking_duration_and_courier_arrival_duration_estimations,
                    cooking_finishes_at={
                        'value': max(
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'cooking_duration'
                                ],
                            ),
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'courier_arrival_duration'
                                ],
                            ),
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                ),
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def place_waiting_duration_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'order_type': 'retail',
                    'shipping_type': 'pickup',
                    'order_status': 'taken',
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'picking_status': 'cancelled',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-0',
                    'claim_status': 'new',
                },
                'expected_estimations': {
                    'courier_arrival_duration': {
                        'value': None,
                        'status': 'skipped',
                    },
                    'courier_arrival_at': {'value': None, 'status': 'skipped'},
                    'place_waiting_duration': {
                        'value': None,
                        'status': 'skipped',
                    },
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'taken',
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-1',
                    'claim_status': 'new',
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': None,
                        'status': 'finished',
                        'metrics': {'update_cargo_info': 0},
                    },
                    'picked_up_at': {
                        'value': None,
                        'status': 'finished',
                        'metrics': {'update_cargo_info': 0},
                    },
                    'place_waiting_duration': {
                        'value': None,
                        'status': 'finished',
                        'metrics': {'update_cargo_info': 0},
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def place_waiting_duration_rest(eta_testcases_context):
    testcase = cooking_finishes_at_cooking_duration(eta_testcases_context)
    for i, order in enumerate(testcase['orders']):
        order['order']['claim_id'] = f'claim-{i}'
        order['order']['shipping_type'] = 'delivery'
        order['order']['order_status'] = 'confirmed'
        order['order']['created_at'] = eta_testcases_context.now_utc
        order['metrics'] = {
            'update_cargo_info': eta_testcases_context.force_first_update,
        }
        for estimation in order['expected_estimations'].values():
            estimation['status'] = 'in_progress'
        order['expected_estimations']['courier_arrival_duration'] = {
            'value': (
                datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'courier_arrival_duration'
                    ],
                )
            ),
            'status': 'in_progress',
            'source': 'fallback',
        }
        order['expected_estimations']['courier_arrival_at'] = {
            'value': (
                eta_testcases_context.now_utc
                + datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'courier_arrival_duration'
                    ],
                )
            ),
            'status': 'in_progress',
            'source': 'fallback',
        }
        order['expected_estimations']['place_waiting_duration'] = {
            'value': max(
                max(
                    order['expected_estimations']['cooking_finishes_at'][
                        'value'
                    ],
                    eta_testcases_context.now_utc
                    + datetime.timedelta(
                        seconds=eta_testcases_context.fallbacks[
                            'minimal_remaining_duration'
                        ],
                    ),
                )
                - order['expected_estimations']['courier_arrival_at']['value'],
                datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'place_waiting_duration'
                    ],
                ),
            ),
            'status': 'not_started',
            'source': 'fallback',
        }
    return testcase


# pylint: disable=invalid-name
def place_waiting_duration_retail(eta_testcases_context):
    testcase = picking_retail(eta_testcases_context)
    for i, order in enumerate(testcase['orders']):
        order['order']['claim_id'] = f'claim-{i}'
        order['order']['shipping_type'] = 'delivery'
        order['order']['order_status'] = 'confirmed'
        order['order']['place_visit_status'] = 'arrived'
        order['order'][
            'pickup_arrived_at'
        ] = eta_testcases_context.now_utc - datetime.timedelta(hours=1)
        order['metrics'] = {
            'update_cargo_info': eta_testcases_context.force_first_update,
        }
        for expected_estimation in order['expected_estimations'].values():
            expected_estimation['metrics'] = {'update_cargo_info': 0}
        order['expected_estimations']['courier_arrival_duration'] = {
            'value': (
                order['order']['pickup_arrived_at']
                - order['order']['created_at']
            ),
            'metrics': {
                'update_cargo_info': eta_testcases_context.force_first_update,
            },
            'status': 'finished',
            'source': 'service',
        }
        order['expected_estimations']['courier_arrival_at'] = {
            'value': order['order']['pickup_arrived_at'],
            'status': 'finished',
            'source': 'service',
        }

        order['expected_estimations']['place_waiting_duration'] = {
            'value': max(
                order['expected_estimations']['picked_up_at']['value']
                - order['expected_estimations']['courier_arrival_at']['value'],
                eta_testcases_context.now_utc
                + datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'minimal_remaining_duration'
                    ],
                )
                - order['expected_estimations']['courier_arrival_at']['value'],
                datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'place_waiting_duration'
                    ],
                ),
            ),
            'status': 'in_progress',
            'source': 'service',
        }
    return testcase


# pylint: disable=invalid-name
def delivery_starts_at_nullopt(eta_testcases_context):
    courier_arrival_at_null = courier_arrival_at_nullopt(eta_testcases_context)
    place_waiting_duration_null = place_waiting_duration_nullopt(
        eta_testcases_context,
    )

    for order in courier_arrival_at_null['orders']:
        expected_estimations = order['expected_estimations']

        expected_estimations['delivery_starts_at'] = dict(
            expected_estimations['courier_arrival_duration'], value=None,
        )
        if (
                expected_estimations['courier_arrival_duration']['status']
                == 'in_progress'
        ):
            expected_estimations['delivery_starts_at'][
                'status'
            ] = 'not_started'

    for order in place_waiting_duration_null['orders']:
        expected_estimations = order['expected_estimations']

        expected_estimations['delivery_starts_at'] = dict(
            expected_estimations['place_waiting_duration'], value=None,
        )

    testcase = {
        'orders': (
            courier_arrival_at_null['orders']
            + place_waiting_duration_null['orders']
        ),
        'places': (
            courier_arrival_at_null['places']
            + place_waiting_duration_null['places']
        ),
    }

    for i, order in enumerate(testcase['orders']):
        order['order']['claim_id'] = f'claim-{i}'

    return testcase


# pylint: disable=invalid-name
def delivery_starts_at_already_started(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'order_status': 'taken',
                    'delivery_started_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=42)
                    ),
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_starts_at': {
                        'value': None,
                        'status': 'finished',
                        'metrics': {'update_cargo_info': 0},
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
            {
                'order': {
                    'order_status': 'confirmed',
                    'place_visit_status': 'visited',
                    'place_visited_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=42)
                    ),
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_starts_at': {
                        'value': (
                            eta_testcases_context.now_utc
                            - datetime.timedelta(seconds=42)
                        ),
                        'status': 'in_progress',
                        'source': 'service',
                        'metrics': {
                            'update_cargo_info': (
                                eta_testcases_context.force_first_update
                            ),
                        },
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }


# pylint: disable=invalid-name
def delivery_starts_at_estimated(eta_testcases_context):
    retail = place_waiting_duration_retail(eta_testcases_context)
    rest = place_waiting_duration_rest(eta_testcases_context)
    for order in retail['orders'] + rest['orders']:
        expected_estimations = order['expected_estimations']
        expected_estimations['delivery_starts_at'] = {
            'value': (
                expected_estimations['courier_arrival_at']['value']
                + expected_estimations['place_waiting_duration']['value']
            ),
            'status': expected_estimations['place_waiting_duration']['status'],
            'source': expected_estimations['place_waiting_duration']['source'],
        }

    return {
        'orders': retail['orders'] + rest['orders'],
        'places': retail['places'] + rest['places'],
    }


def delivery_duration_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {'shipping_type': 'pickup'},
                'expected_estimations': {
                    'delivery_duration': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {'order_status': 'complete'},
                'expected_estimations': {
                    'delivery_duration': {'value': None, 'status': 'finished'},
                },
            },
            {
                'order': {'order_status': 'cancelled'},
                'expected_estimations': {
                    'delivery_duration': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {
                    'order_type': 'retail',
                    'order_status': 'confirmed',
                    'picking_status': 'cancelled',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'delivery_duration': {'value': None, 'status': 'skipped'},
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_visited_at': eta_testcases_context.now_utc,
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'delivery_zone_courier_type': 'vehicle',
                    'delivery_coordinates': '(11.22,33.54)',
                    'created_at': eta_testcases_context.now_utc,
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'claim_status': 'pickuped',
                    'claim_id': 'claim-0',
                    'batch_info': {
                        'delivery_order': [
                            {'claim_id': 'claim-0', 'order': 1},
                            {'claim_id': 'claim-1', 'order': 2},
                        ],
                    },
                    'batch_info_updated_at': eta_testcases_context.now_utc,
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': None,
                        'status': 'in_progress',
                        'metrics': {'update_cargo_info': 1},
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }


def delivery_duration_fallback(eta_testcases_context):
    @eta_testcases_context.mockserver.handler('/maps-router/v2/summary')
    def _mock_route_jams(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    return {
        'orders': [
            {
                'order': {
                    'place_id': 0,
                    'order_type': 'native',
                    'order_status': 'taken',
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-0',
                    'claim_status': 'new',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'delivery_duration'
                                ],
                            )
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'vehicle',
                    'delivery_coordinates': '(11.22,33.54)',
                    'created_at': eta_testcases_context.now_utc,
                    'delivery_started_at': eta_testcases_context.now_utc,
                    'claim_id': 'claim-1',
                    'claim_status': 'pickuped',
                    'ml_provider': 'proxy',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'delivery_duration'
                                ],
                            )
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [{'id': 1, 'location': '(11.22,33.44)'}],
    }


def delivery_duration_cargo_eta(eta_testcases_context):
    delivery_started_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=200,
    )
    place_visited_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=1000,
    )
    customer_visited_at = eta_testcases_context.now_utc + datetime.timedelta(
        seconds=500,
    )
    order_created_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=1000,
    )
    place_cargo_waiting_time = datetime.timedelta(seconds=100)

    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': customer_visited_at,
                    'customer_visit_status': 'arrived',
                    'claim_status': 'returned',
                    'delivery_started_at': delivery_started_at,
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (customer_visited_at - delivery_started_at),
                        'status': 'finished',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': (
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=1)
                    ),
                    'customer_visit_status': 'pending',
                    'claim_status': None,
                    'delivery_started_at': delivery_started_at,
                    'claim_id': 'claim-1',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            eta_testcases_context.now_utc
                            + datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'minimal_remaining_duration'
                                ],
                            )
                            - delivery_started_at
                        ),
                        'status': 'in_progress',
                        'source': 'service',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': customer_visited_at,
                    'place_visited_at': place_visited_at,
                    'customer_visit_status': 'pending',
                    'delivery_started_at': delivery_started_at,
                    'place_cargo_waiting_time': place_cargo_waiting_time,
                    'claim_status': 'performer_found',
                    'claim_id': 'claim-2',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            customer_visited_at
                            - place_visited_at
                            - place_cargo_waiting_time
                        ),
                        'status': 'not_started',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': customer_visited_at,
                    'place_visited_at': place_visited_at,
                    'customer_visit_status': 'pending',
                    'delivery_started_at': delivery_started_at,
                    'claim_status': 'performer_found',
                    'claim_id': 'claim-3',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            customer_visited_at
                            - place_visited_at
                            - datetime.timedelta(
                                seconds=eta_testcases_context.fallbacks[
                                    'place_cargo_waiting_time'
                                ],
                            )
                        ),
                        'status': 'not_started',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': customer_visited_at,
                    'place_visited_at': place_visited_at,
                    'customer_visit_status': 'pending',
                    'place_visit_status': 'visited',
                    'claim_status': 'performer_found',
                    'claim_id': 'claim-3',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': customer_visited_at - place_visited_at,
                        'status': 'not_started',
                        'source': 'service',
                    },
                },
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'courier_position': '(11.22,33.44)',
                    'created_at': order_created_at,
                    'customer_visited_at': eta_testcases_context.now_utc,
                    'place_visited_at': eta_testcases_context.now_utc,
                    'customer_visit_status': 'pending',
                    'delivery_started_at': delivery_started_at,
                    'claim_status': 'performer_found',
                    'claim_id': 'claim-4',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': datetime.timedelta(),
                        'status': 'not_started',
                        'source': 'service',
                    },
                },
            },
        ],
        'places': [],
    }


def delivery_duration_no_delivery_coordinates(eta_testcases_context):
    delivery_started_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=200,
    )

    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'confirmed',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'customer_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'customer_visited_at': eta_testcases_context.now_utc,
                    'created_at': eta_testcases_context.now_utc,
                    'delivery_started_at': delivery_started_at,
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'delivery_duration'
                            ],
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


def delivery_duration_cargo_position(eta_testcases_context):
    order_created_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=1000,
    )
    courier_position_updated_at = eta_testcases_context.now_utc
    delivery_started_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=900,
    )
    route_time = 2500

    mock_car_router(eta_testcases_context, route_time, 2500)

    @eta_testcases_context.mockserver.handler(
        '/maps-pedestrian-router/pedestrian/v2/summary',
    )
    def _mock_route_jams(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_visited_at': eta_testcases_context.now_utc,
                    'courier_position_updated_at': courier_position_updated_at,
                    'courier_position': '(11.22,33.44)',
                    'delivery_zone_courier_type': 'vehicle',
                    'delivery_coordinates': '(11.22,33.54)',
                    'created_at': order_created_at,
                    'delivery_started_at': delivery_started_at,
                    'claim_status': 'pickuped',
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            courier_position_updated_at
                            + datetime.timedelta(seconds=route_time)
                            - delivery_started_at
                        ),
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'place_point_eta_updated_at': (
                        eta_testcases_context.now_utc
                    ),
                    'place_visited_at': eta_testcases_context.now_utc,
                    'courier_position_updated_at': courier_position_updated_at,
                    'courier_position': '(11.22,33.44)',
                    'delivery_zone_courier_type': 'pedestrian',
                    'delivery_coordinates': '(11.22,33.54)',
                    'created_at': order_created_at,
                    'delivery_started_at': delivery_started_at,
                    'claim_status': 'pickuped',
                    'claim_id': 'claim-1',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            courier_position_updated_at
                            + datetime.timedelta(
                                seconds=11119.507973463116
                                // eta_testcases_context.fallbacks[
                                    'courier_speed'
                                ],
                            )
                            - delivery_started_at
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }


def delivery_duration_delivery_time(eta_testcases_context):
    place_id = 2
    order_created_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=1000,
    )
    delivery_time = datetime.timedelta(seconds=5000)
    cooking_time = datetime.timedelta(seconds=2000)
    cooking_finishes_at = order_created_at + cooking_time
    courier_arrival_at = max(
        order_created_at
        + max(
            datetime.timedelta(
                seconds=eta_testcases_context.fallbacks[
                    'courier_arrival_duration'
                ],
            ),
            cooking_time,
        ),
        eta_testcases_context.now_utc
        + datetime.timedelta(
            seconds=eta_testcases_context.fallbacks[
                'minimal_remaining_duration'
            ],
        ),
    )
    delivery_starts_at = max(
        courier_arrival_at
        + datetime.timedelta(
            seconds=eta_testcases_context.fallbacks['place_waiting_duration'],
        ),
        cooking_finishes_at,
    )

    @eta_testcases_context.mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    @eta_testcases_context.mockserver.handler(
        '/maps-pedestrian-router/pedestrian/v2/summary',
    )
    def _mock_pedestrian_router(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    return {
        'orders': [
            {
                'order': {
                    'place_id': place_id,
                    'shipping_type': 'delivery',
                    'order_status': 'created',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'created_at': order_created_at,
                    'delivery_coordinates': '(11.22,33.54)',
                    'delivery_time': delivery_time,
                    'cooking_time': cooking_time,
                    'claim_id': 'claim-0',
                    'ml_provider': 'ml',
                },
                'expected_estimations': {
                    'delivery_starts_at': {
                        'value': delivery_starts_at,
                        'status': 'not_started',
                        'source': 'partial_fallback',
                    },
                    'delivery_duration': {
                        'value': delivery_time,
                        'status': 'not_started',
                        'source': 'partial_fallback',
                    },
                },
            },
            {
                'order': {
                    'place_id': place_id,
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'delivery_started_at': delivery_starts_at,
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'created_at': order_created_at,
                    'delivery_time': None,
                    'cooking_time': cooking_time,
                    'claim_id': 'claim-1',
                    'ml_provider': 'ml',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'delivery_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [{'id': place_id}],
    }


def delivery_duration_route_from_place(eta_testcases_context):
    delivery_started_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=900,
    )
    order_created_at = eta_testcases_context.now_utc - datetime.timedelta(
        seconds=1000,
    )
    route_time = 2500

    mock_car_router(eta_testcases_context, 2500, 2500)

    @eta_testcases_context.mockserver.handler(
        '/maps-pedestrian-router/pedestrian/v2/summary',
    )
    def _mock_route_jams(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    return {
        'orders': [
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'delivery_time': datetime.timedelta(seconds=1),
                    'courier_position_updated_at': None,
                    'delivery_zone_courier_type': 'vehicle',
                    'delivery_coordinates': '(22.33,44.55)',
                    'created_at': order_created_at,
                    'delivery_started_at': delivery_started_at,
                    'ml_provider': 'ml',
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': datetime.timedelta(seconds=route_time),
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                'order': {
                    'place_id': 1,
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'picking_status': 'dispatching',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_type': 'native',
                    'delivery_time': None,
                    'courier_position_updated_at': None,
                    'delivery_zone_courier_type': 'pedestrian',
                    'delivery_coordinates': '(11.22,33.54)',
                    'created_at': order_created_at,
                    'delivery_started_at': delivery_started_at,
                    'ml_provider': 'proxy',
                    'claim_id': 'claim-1',
                },
                'expected_estimations': {
                    'delivery_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'delivery_duration'
                            ],
                        ),
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [{'id': 1, 'location': '(11.22,33.44)'}],
    }


def delivery_at_nullopt(eta_testcases_context):
    delivery_duration_null = delivery_duration_nullopt(eta_testcases_context)
    for order in delivery_duration_null['orders']:
        expected_estimations = order['expected_estimations']
        expected_estimations['delivery_at'] = expected_estimations[
            'delivery_duration'
        ]

    return delivery_duration_null


def delivery_at(eta_testcases_context):
    testcase = delivery_duration_delivery_time(eta_testcases_context)
    for order in testcase['orders']:
        expected_estimations = order['expected_estimations']
        expected_estimations['delivery_at'] = {
            'value': (
                order['order'].get('delivery_started_at', None)
                or expected_estimations['delivery_starts_at']['value']
            ) + expected_estimations['delivery_duration']['value'],
            'status': expected_estimations['delivery_duration']['status'],
            'source': expected_estimations['delivery_duration']['source'],
        }
    return testcase


def delivery_arrived_at(eta_testcases_context):
    order = {
        'claim_id': 'claim-0',
        'claim_status': 'delivery_arrived',
        'shipping_type': 'delivery',
        'order_status': 'taken',
        'created_at': eta_testcases_context.now_utc,
        'claim_created_at': eta_testcases_context.now_utc - datetime.timedelta(
            seconds=4000,
        ),
        'delivery_started_at': (
            eta_testcases_context.now_utc - datetime.timedelta(seconds=2000)
        ),
        'delivery_arrived_at': (
            eta_testcases_context.now_utc - datetime.timedelta(minutes=1)
        ),
        'place_visit_status': 'visited',
        'place_visited_at': eta_testcases_context.now_utc - datetime.timedelta(
            seconds=2000,
        ),
        'place_point_eta_updated_at': eta_testcases_context.now_utc,
        'customer_visit_status': 'arrived',
        'customer_visited_at': eta_testcases_context.now_utc,
        'customer_point_eta_updated_at': eta_testcases_context.now_utc,
    }
    return {
        'orders': [
            {
                'order': order,
                'expected_estimations': {
                    'delivery_duration': {
                        'value': (
                            order['delivery_arrived_at']
                            - order['delivery_started_at']
                        ),
                        'status': 'finished',
                        'source': 'service',
                    },
                    'delivery_at': {
                        'value': order['delivery_arrived_at'],
                        'status': 'finished',
                        'source': 'service',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


def complete_at_nullopt(eta_testcases_context):
    return {
        'orders': [
            {
                'order': {
                    'shipping_type': 'delivery',
                    'order_status': 'taken',
                    'claim_id': 'claim-0',
                },
                'expected_estimations': {
                    'complete_at': {
                        'value': None,
                        'cached': False,
                        'status': 'not_started',
                    },
                },
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [],
    }


def complete_at(eta_testcases_context):
    delivery = delivery_at(eta_testcases_context)
    minimal_remaining_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['minimal_remaining_duration'],
    )
    for order in delivery['orders']:
        expected_estimations = order['expected_estimations']
        delivery_status = expected_estimations['delivery_duration']['status']
        if delivery_status == 'finished':
            status = 'in_progress'
        else:
            status = 'not_started'
        expected_estimations['complete_at'] = {
            'value': max(
                expected_estimations['delivery_at']['value']
                + datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'customer_waiting_duration'
                    ],
                ),
                eta_testcases_context.now_utc + minimal_remaining_duration,
            ),
            'status': status,
            'source': expected_estimations['delivery_at']['source'],
        }
    picking = picking_retail(eta_testcases_context)
    for order in picking['orders']:
        order['order']['shipping_type'] = 'pickup'
        expected_estimations = order['expected_estimations']
        picking_estimation_status = expected_estimations['picking_duration'][
            'status'
        ]
        if picking_estimation_status == 'finished':
            status = 'in_progress'
        else:
            status = 'not_started'
        expected_estimations['complete_at'] = {
            'value': max(
                expected_estimations['picked_up_at']['value']
                + datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'customer_waiting_duration'
                    ],
                ),
                eta_testcases_context.now_utc + minimal_remaining_duration,
            ),
            'status': status,
            'source': expected_estimations['picked_up_at']['source'],
        }
    cooking = cooking_finishes_at_cooking_duration(eta_testcases_context)
    for order in cooking['orders']:
        order['order']['shipping_type'] = 'pickup'
        expected_estimations = order['expected_estimations']
        cooking_status = expected_estimations['cooking_duration']['status']
        if cooking_status == 'finished':
            status = 'in_progress'
        else:
            status = 'not_started'
        expected_estimations['complete_at'] = {
            'value': max(
                expected_estimations['cooking_finishes_at']['value']
                + datetime.timedelta(
                    seconds=eta_testcases_context.fallbacks[
                        'customer_waiting_duration'
                    ],
                ),
                eta_testcases_context.now_utc + minimal_remaining_duration,
            ),
            'status': status,
            'source': expected_estimations['cooking_finishes_at']['source'],
        }
    testcase = {
        'orders': delivery['orders'][:1],
        'places': delivery['places'] + picking['places'] + cooking['places'],
    }
    return testcase


def update_cargo_info(eta_testcases_context):
    claim = eta_testcases_context.load_json('claim.json')
    points_eta = eta_testcases_context.load_json('points_eta.json')
    performer_position = eta_testcases_context.load_json(
        'performer_position.json',
    )
    order = {
        'shipping_type': 'delivery',
        'order_status': 'confirmed',
        'delivery_type': 'native',
        'created_at': eta_testcases_context.now_utc,
        'order_type': 'retail',
        'picking_status': 'new',
        'retail_order_created_at': eta_testcases_context.now_utc,
        'picking_duration_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=RETAIL_INFO_TTL)
        ),
        'picking_start_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=RETAIL_INFO_TTL)
        ),
        'corp_client_type': utils.RETAIL_CORP_CLIENT,
    }
    order_update = {
        'batch_info': {
            'delivery_order': [
                {'claim_id': 'claim-0', 'order': 1},
                {'claim_id': 'claim-1', 'order': 2},
            ],
        },
        'batch_info_updated_at': eta_testcases_context.now_utc,
    }
    utils.update_cargo_claim(order_update, 'claim-0', claim)
    del order_update['claim_id']
    utils.update_points_eta(
        order_update, eta_testcases_context.now_utc, points_eta,
    )
    utils.update_performer_position(order_update, performer_position)
    expected_estimations = {
        'delivery_duration': {
            'value': (
                order_update['customer_visited_at']
                - order_update['place_visited_at']
                - order_update['place_cargo_waiting_time']
            ),
            'status': 'not_started',
            'source': 'service',
        },
    }
    testcase = {
        'orders': [
            *[
                {
                    'order': dict(
                        order,
                        claim_status='new',
                        place_point_eta_updated_at=(
                            eta_testcases_context.now_utc
                            - datetime.timedelta(seconds=CARGO_ROUTE_ETA_TTL)
                        ),
                        batch_info=batch_info,
                        batch_info_updated_at=batch_info_updated_at,
                    ),
                    'order_update': order_update,
                    'expected_estimations': expected_estimations,
                    'metrics': {'update_cargo_info': 1},
                }
                for batch_info in [None, {'delivery_order': []}]
                for batch_info_updated_at in [
                    None,
                    eta_testcases_context.now_utc - datetime.timedelta(days=1),
                ]
            ],
            *[
                {
                    'order': dict(
                        order,
                        claim_status='new',
                        place_point_eta_updated_at=(
                            eta_testcases_context.now_utc
                            - datetime.timedelta(seconds=CARGO_ROUTE_ETA_TTL)
                        ),
                        batch_info=batch_info,
                        batch_info_updated_at=eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=1),
                    ),
                    'order_update': {
                        key: value
                        for key, value in order_update.items()
                        if key not in ('batch_info', 'batch_info_updated_at')
                    },
                    'expected_estimations': expected_estimations,
                    'metrics': {'update_cargo_info': 1},
                }
                for batch_info in [None, {'delivery_order': []}]
            ],
            {
                'order': dict(order, order_status='created'),
                'order_update': (
                    order_update if eta_testcases_context.force_update else {}
                ),
                'expected_estimations': (
                    expected_estimations
                    if eta_testcases_context.force_update
                    else {
                        'delivery_duration': {
                            'value': (
                                datetime.timedelta(
                                    seconds=eta_testcases_context.fallbacks[
                                        'delivery_duration'
                                    ],
                                )
                            ),
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                    }
                ),
                'metrics': {
                    'update_cargo_info': eta_testcases_context.force_update,
                },
            },
            {
                'order': order,
                'order_update': (
                    order_update
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': (
                    expected_estimations
                    if eta_testcases_context.force_first_update
                    else {
                        'delivery_duration': {
                            'value': (
                                datetime.timedelta(
                                    seconds=eta_testcases_context.fallbacks[
                                        'delivery_duration'
                                    ],
                                )
                            ),
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                    }
                ),
                'metrics': {
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                'order': dict(
                    order,
                    claim_status='new',
                    courier_position_updated_at=eta_testcases_context.now_utc,
                    courier_position='(22.33,44.55)',
                    customer_point_eta_updated_at=(
                        eta_testcases_context.now_utc
                        - datetime.timedelta(seconds=CARGO_ROUTE_ETA_TTL)
                    ),
                ),
                'order_update': order_update,
                'expected_estimations': expected_estimations,
                'metrics': {'update_cargo_info': 1},
            },
            {
                'order': dict(order, claim_status='new'),
                'order_update': order_update,
                'expected_estimations': expected_estimations,
                'metrics': {'update_cargo_info': 1},
            },
        ],
        'places': [],
    }
    for i, testcase_order in enumerate(testcase['orders']):
        order = testcase_order['order']
        order_nr = f'order-{i}'
        order['order_nr'] = order_nr
        order['claim_id'] = f'claim-{i}'
        eta_testcases_context.cargo.add_claim(
            claim_id=f'claim-{i}',
            order_nr=order_nr,
            created_ts=order_update.get(
                'claim_created_at', eta_testcases_context.now_utc,
            ),
            status=order_update.get('claim_status', 'pickuped'),
            order_type='retail',
        )
        batch_info = testcase_order['order_update'].get(
            'batch_info', order.get('batch_info', None),
        )
        if batch_info is not None:
            eta_testcases_context.cargo.add_batch_info(
                order['claim_id'], **batch_info,
            )
    return testcase


def update_retail_info(eta_testcases_context):
    flow_type = 'picking_packing'
    retail_order_created_at = (
        eta_testcases_context.now_utc - datetime.timedelta(seconds=100)
    )
    picking_status_updated_at = (
        eta_testcases_context.now_utc - datetime.timedelta(seconds=1)
    )
    initial_picking_duration = datetime.timedelta(seconds=1200)
    estimated_waiting_time = datetime.timedelta(
        seconds=eta_testcases_context.pickers.place_load[
            'estimated_waiting_time'
        ],
    )
    picking_starts_at_dispatching = (
        eta_testcases_context.now_utc
        + datetime.timedelta(
            seconds=eta_testcases_context.fallbacks['picker_waiting_time']
            + eta_testcases_context.fallbacks['picker_dispatching_time'],
        )
    )
    pickedup_at_dispatching = (
        picking_starts_at_dispatching + initial_picking_duration
    )
    picking_starts_at_new = (
        picking_starts_at_dispatching + estimated_waiting_time
    )
    pickedup_at_new = picking_starts_at_new + initial_picking_duration

    elapsed_picking_duration = datetime.timedelta(seconds=50)
    remaining_picking_duration = datetime.timedelta(seconds=150)
    total_picking_duration_picking_started = (
        elapsed_picking_duration + remaining_picking_duration
    )
    picking_started_at = (
        eta_testcases_context.now_utc - elapsed_picking_duration
    )
    pickedup_at_picking_started = (
        eta_testcases_context.now_utc + remaining_picking_duration
    )
    cart_created_at = eta_testcases_context.now_utc - datetime.timedelta(
        minutes=5,
    )
    eta_testcases_context.pickers.cart['created_at'] = utils.to_string(
        cart_created_at,
    )
    eta_testcases_context.pickers.estimate[
        'eta_seconds'
    ] = remaining_picking_duration.total_seconds()

    @eta_testcases_context.mockserver.json_handler(
        '/eats-picker-orders/api/v1/orders/status-time',
    )
    def _picker_orders_status_time(request):
        return {
            'timestamps': [
                {
                    'eats_id': eats_id,
                    'status_change_timestamp': utils.to_string(
                        picking_started_at,
                    ),
                }
                for eats_id in request.json['eats_ids']
            ],
        }

    order = {
        'order_type': 'retail',
        'order_status': 'confirmed',
        'created_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=RETAIL_INFO_TTL)
        ),
        'picking_status': 'new',
        'retail_order_created_at': eta_testcases_context.now_utc,
        'picking_duration_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=RETAIL_INFO_TTL)
        ),
        'picking_start_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=RETAIL_INFO_TTL)
        ),
        'claim_status': 'performer_found',
        'place_visit_status': 'pending',
        'customer_visit_status': 'pending',
        'place_point_eta_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=CARGO_ROUTE_ETA_TTL)
        ),
        'customer_point_eta_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=CARGO_ROUTE_ETA_TTL)
        ),
        'courier_position_updated_at': (
            eta_testcases_context.now_utc
            - datetime.timedelta(seconds=CARGO_COURIER_POSITION_TTL)
        ),
    }
    order_update = {
        'picking_status': 'new',
        'picking_duration': initial_picking_duration,
        'picking_starts_at': picking_starts_at_new,
        'picking_flow_type': flow_type,
        'retail_order_created_at': retail_order_created_at,
        'picking_duration_updated_at': eta_testcases_context.now_utc,
        'picking_start_updated_at': eta_testcases_context.now_utc,
    }
    fallback_picking_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['picking_duration'],
    )
    testcase = {
        'orders': [
            {
                'order': order.copy(),
                'order_update': order_update,
                'expected_estimations': {
                    'picking_duration': {
                        'value': initial_picking_duration,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    'picked_up_at': {
                        'value': pickedup_at_new,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                },
            },
            {
                'order': dict(
                    order,
                    picking_duration=initial_picking_duration,
                    picking_duration_updated_at=eta_testcases_context.now_utc,
                ),
                'order_update': order_update,
                'expected_estimations': {
                    'picking_duration': {
                        'value': initial_picking_duration,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 0},
                    },
                    'picked_up_at': {
                        'value': pickedup_at_new,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                },
            },
            {
                'order': dict(
                    order,
                    picking_starts_at=picking_starts_at_new,
                    picking_start_updated_at=eta_testcases_context.now_utc,
                ),
                'order_update': order_update,
                'expected_estimations': {
                    'picking_duration': {
                        'value': initial_picking_duration,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    # picking_starts_at уже имеет актуальное значение
                    'picked_up_at': {
                        'value': pickedup_at_new,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': order_update,
                'expected_estimations': {
                    'picked_up_at': {
                        'value': pickedup_at_new,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    # при вычислении picked_up_at продолжительность сборки
                    # уже была обновлена
                    'picking_duration': {
                        'value': initial_picking_duration,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': dict(
                    order_update,
                    picking_status='dispatching',
                    picking_starts_at=picking_starts_at_dispatching,
                ),
                'expected_estimations': {
                    'picking_duration': {
                        'value': initial_picking_duration,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    'picked_up_at': {
                        'value': pickedup_at_dispatching,
                        'status': 'not_started',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': dict(
                    order_update,
                    picking_status='picking',
                    picking_duration=total_picking_duration_picking_started,
                    picking_starts_at=picking_started_at,
                ),
                'expected_estimations': {
                    'picking_duration': {
                        'value': total_picking_duration_picking_started,
                        'status': 'in_progress',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    # сборка заказа уже началась, время начала сборки
                    # уже получили для вычисления оставшейся
                    # продолжительности сборки
                    'picked_up_at': {
                        'value': pickedup_at_picking_started,
                        'status': 'in_progress',
                        'source': 'service',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': dict(
                    order_update,
                    picking_status='complete',
                    picking_duration=picking_status_updated_at
                    - picking_started_at,
                    picking_starts_at=picking_started_at,
                ),
                'expected_estimations': {
                    'picking_duration': {
                        'value': (
                            picking_status_updated_at - picking_started_at
                        ),
                        'status': 'finished',
                        'source': 'service',
                        'metrics': {'update_retail_info': 1},
                    },
                    # сборка заказа уже началась, время начала сборки
                    # уже получили для вычисления оставшейся
                    # продолжительности сборки
                    'picked_up_at': {
                        'value': picking_status_updated_at,
                        'status': 'finished',
                        'source': 'service',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': {
                    'picking_flow_type': flow_type,
                    'retail_order_created_at': retail_order_created_at,
                    'picking_status': 'cancelled',
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': None,
                        'status': 'skipped',
                        'metrics': {'update_retail_info': 1},
                    },
                    'picked_up_at': {
                        'value': None,
                        'status': 'skipped',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': order.copy(),
                'order_update': {
                    'picking_flow_type': flow_type,
                    'retail_order_created_at': retail_order_created_at,
                    'picking_status': 'cancelled',
                },
                'expected_estimations': {
                    'picked_up_at': {
                        'value': None,
                        'status': 'skipped',
                        'metrics': {'update_retail_info': 1},
                    },
                    'picking_duration': {
                        'value': None,
                        'status': 'skipped',
                        'metrics': {'update_retail_info': 0},
                    },
                },
            },
            {
                'order': dict(
                    order,
                    picking_status=None,
                    picking_duration_updated_at=None,
                ),
                'order_update': (
                    order_update
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': (
                    {
                        'picked_up_at': {
                            'value': pickedup_at_new,
                            'status': 'not_started',
                            'source': 'service',
                        },
                        'picking_duration': {
                            'value': initial_picking_duration,
                            'metrics': {'update_retail_info': False},
                            'status': 'not_started',
                            'source': 'service',
                        },
                    }
                    if eta_testcases_context.force_first_update
                    else {
                        'picked_up_at': {
                            'value': (
                                order['retail_order_created_at']
                                + fallback_picking_duration
                            ),
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                        'picking_duration': {
                            'value': fallback_picking_duration,
                            'status': 'not_started',
                            'source': 'fallback',
                        },
                    }
                ),
                'metrics': {
                    'update_retail_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [{'id': 1, 'location': '(11.22,33.44)'}],
    }
    for i, testcase_order in enumerate(testcase['orders']):
        order = testcase_order['order']
        order_nr = f'order-{i}'
        order['order_nr'] = order_nr
        eta_testcases_context.pickers.add_order(
            order_nr=order_nr,
            status=testcase_order['order_update'].get('picking_status', 'new'),
            flow_type=flow_type,
            created_at=utils.to_string(retail_order_created_at),
            status_updated_at=utils.to_string(picking_status_updated_at),
        )
    return testcase


def update_ml_prediction(eta_testcases_context):
    average_preparation = datetime.timedelta(minutes=15)
    extra_preparation = datetime.timedelta(minutes=5)
    place_cooking_duration = average_preparation + extra_preparation
    fallback_courier_arrival_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['courier_arrival_duration'],
    )
    fallback_cooking_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['cooking_duration'],
    )
    fallback_picking_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['picking_duration'],
    )
    fallback_place_waiting_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['place_waiting_duration'],
    )
    fallback_delivery_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['delivery_duration'],
    )
    fallback_customer_waiting_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['customer_waiting_duration'],
    )
    ml_cooking_duration_source = (
        'service'
        if eta_testcases_context.force_first_update
        else 'partial_fallback'
    )
    ml_delivery_duration_source = (
        'partial_fallback'
        if eta_testcases_context.force_first_update
        else 'fallback'
    )
    testcase = {
        'orders': [
            {
                # ok
                'order': {
                    'order_nr': '1',
                    'place_id': 1,
                    'order_type': 'native',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'pedestrian',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': 'eater-id',
                    'device_id': 'device-id-1',
                },
                'order_update': (
                    {
                        'ml_provider': 'ml',
                        'cooking_time': datetime.timedelta(minutes=11),
                        'delivery_time': datetime.timedelta(minutes=12),
                        'total_time': datetime.timedelta(minutes=25),
                    }
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': {
                    'cooking_duration': {
                        'value': (
                            datetime.timedelta(minutes=11)
                            if eta_testcases_context.force_first_update
                            else place_cooking_duration
                        ),
                        'metrics': {
                            'update_ml_prediction': (
                                eta_testcases_context.force_first_update
                            ),
                        },
                        'status': 'in_progress',
                        'source': ml_cooking_duration_source,
                    },
                    'delivery_duration': {
                        'value': (
                            datetime.timedelta(minutes=12)
                            if eta_testcases_context.force_first_update
                            else fallback_delivery_duration
                        ),
                        'metrics': {'update_ml_prediction': 0},
                        'status': 'not_started',
                        'source': ml_delivery_duration_source,
                    },
                },
                'metrics': {
                    'update_ml_prediction': (
                        eta_testcases_context.force_first_update
                    ),
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # ok
                'order': {
                    'order_nr': '2',
                    'place_id': 1,
                    'order_type': 'fast_food',
                    'delivery_type': 'marketplace',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': None,
                },
                'order_update': (
                    {
                        'ml_provider': 'ml',
                        'cooking_time': datetime.timedelta(minutes=1),
                        'delivery_time': datetime.timedelta(minutes=2),
                        'total_time': datetime.timedelta(minutes=5),
                    }
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': {
                    'cooking_duration': {
                        'value': (
                            datetime.timedelta(minutes=1)
                            if eta_testcases_context.force_first_update
                            else place_cooking_duration
                        ),
                        'metrics': {
                            'update_ml_prediction': (
                                eta_testcases_context.force_first_update
                            ),
                        },
                        'status': 'in_progress',
                        'source': ml_cooking_duration_source,
                    },
                    'delivery_duration': {
                        'value': (
                            datetime.timedelta(minutes=2)
                            if eta_testcases_context.force_first_update
                            else fallback_delivery_duration
                        ),
                        'metrics': {'update_ml_prediction': 0},
                        'status': 'not_started',
                        'source': ml_delivery_duration_source,
                    },
                },
                'metrics': {
                    'update_ml_prediction': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # unknown place
                'order': {
                    'order_nr': '3',
                    'place_id': 2,
                    'order_type': 'fast_food',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': 'device-id-3',
                },
                'order_update': {},
                'expected_estimations': {
                    'cooking_duration': {
                        'value': fallback_cooking_duration,
                        'status': 'in_progress',
                        'source': 'fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': 0,
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # proxy provider
                'order': {
                    'order_nr': '4',
                    'place_id': 1,
                    'order_type': 'fast_food',
                    'delivery_type': 'native',
                    'shipping_type': 'pickup',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': 'device-id-4',
                },
                'order_update': (
                    {
                        'ml_provider': 'proxy',
                        'total_time': (
                            fallback_cooking_duration
                            + fallback_customer_waiting_duration
                        ),
                    }
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': {
                    'cooking_duration': {
                        'value': place_cooking_duration,
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # proxy provider
                'order': {
                    'order_nr': '5',
                    'place_id': 1,
                    'order_type': 'fast_food',
                    'delivery_type': 'native',
                    'shipping_type': 'delivery',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': 'device-id-5',
                },
                'order_update': (
                    {
                        'ml_provider': 'proxy',
                        'total_time': (
                            max(
                                fallback_courier_arrival_duration
                                + fallback_place_waiting_duration,
                                fallback_cooking_duration,
                            )
                            + fallback_delivery_duration
                            + fallback_customer_waiting_duration
                        ),
                    }
                    if eta_testcases_context.force_first_update
                    else {}
                ),
                'expected_estimations': {
                    'cooking_duration': {
                        'value': place_cooking_duration,
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': (
                        eta_testcases_context.force_first_update
                    ),
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # proxy provider, ml prediction not needed
                'order': {
                    'order_nr': '6',
                    'place_id': 1,
                    'order_type': 'retail',
                    'delivery_type': 'native',
                    'shipping_type': 'pickup',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'picking_status': 'assigned',
                    'retail_order_created_at': eta_testcases_context.now_utc,
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': 'device-id-6',
                },
                'order_update': {},
                'expected_estimations': {
                    'picking_duration': {
                        'value': datetime.timedelta(
                            seconds=eta_testcases_context.fallbacks[
                                'picking_duration'
                            ],
                        ),
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': 0,
                    'update_retail_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # 500
                'order': {
                    'order_nr': '7',
                    'place_id': 1,
                    'order_type': 'fast_food',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': '(33.333,55.555)',
                    'eater_id': '123',
                    'device_id': 'device-id-7',
                },
                'order_update': {},
                'expected_estimations': {
                    'cooking_duration': {
                        'value': place_cooking_duration,
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': (
                        eta_testcases_context.force_first_update
                    ),
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
            {
                # no delivery_coordinates
                'order': {
                    'order_nr': '8',
                    'place_id': 1,
                    'order_type': 'fast_food',
                    'delivery_type': 'native',
                    'delivery_zone_courier_type': 'yandex_rover',
                    'order_status': 'confirmed',
                    'delivery_coordinates': None,
                    'eater_id': '123',
                    'device_id': 'device-id-8',
                },
                'order_update': {},
                'expected_estimations': {
                    'cooking_duration': {
                        'value': place_cooking_duration,
                        'status': 'in_progress',
                        'source': 'partial_fallback',
                    },
                },
                'metrics': {
                    'update_ml_prediction': 0,
                    'update_cargo_info': (
                        eta_testcases_context.force_first_update
                    ),
                },
            },
        ],
        'places': [
            {
                'id': 1,
                'brand_id': 123,
                'average_preparation': average_preparation,
                'extra_preparation': extra_preparation,
                'rating_users': 4.87,
                'price_category_value': 1.5,
                'location': '(34.343,56.565)',
            },
        ],
    }
    device_id_to_testcase_order = {}
    for i, testcase_order in enumerate(testcase['orders']):
        order = testcase_order['order']
        order['claim_id'] = f'claim-{i}'
        device_id = order['device_id'] or ''
        device_id_to_testcase_order[device_id] = testcase_order
        eta_testcases_context.revisions.set_default(
            order['order_nr'], str(order['place_id']),
        )
    places_dict = {place['id']: place for place in testcase['places']}

    @eta_testcases_context.mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    @eta_testcases_context.mockserver.handler(
        '/maps-pedestrian-router/pedestrian/v2/summary',
    )
    def _mock_route_jams(request):
        assert request.method == 'GET'
        return eta_testcases_context.mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    @eta_testcases_context.mockserver.json_handler(
        '/umlaas-eats/umlaas-eats/v1/eta',
    )
    def _mock_umlaas(request):
        device_id = request.query['device_id']
        testcase_order = device_id_to_testcase_order[device_id]
        order = testcase_order['order']
        order_update = testcase_order['order_update']
        assert device_id == (order['device_id'] or '')
        assert request.query['service_name'] == 'eats-eta'
        assert 'request_id' in request.query
        try:
            expected_user_id = order['eater_id']
            int(expected_user_id)
        except ValueError:
            expected_user_id = None
        assert request.query.get('user_id', None) == expected_user_id
        order_type = order['order_type']
        assert (
            request.query['place_type'] == 'shop'
            if order_type in {'retail', 'shop'}
            else 'default'
        )
        assert request.query['request_type'] == 'default'
        assert (
            utils.parse_datetime(request.json['predicting_at'])
            == eta_testcases_context.now_utc
        )
        assert (
            utils.parse_datetime(request.json['server_time'])
            == eta_testcases_context.now_utc
        )
        user_location = ast.literal_eval(order['delivery_coordinates'])
        assert request.json['user_location'] == {
            'lon': user_location[0],
            'lat': user_location[1],
        }
        assert len(request.json['requested_times']) == 1
        requested_time = request.json['requested_times'][0]
        expected_cart = [
            {
                'item': {
                    'currency': 'RUB',
                    'name': 'Сливы',
                    'price': 240.0,
                    'weight': {'mass': 500.0, 'type': 'GRM'},
                },
                'quantity': 2,
            },
            {
                'item': {
                    'currency': 'RUB',
                    'name': 'Макароны',
                    'price': 50.0,
                    'weight': {'mass': 0.0, 'type': ''},
                },
                'quantity': 1,
            },
            {
                'item': {
                    'currency': 'RUB',
                    'name': 'Дырка от бублика',
                    'price': 60.0,
                    'weight': {'mass': 0.0, 'type': ''},
                },
                'quantity': 2,
            },
        ]

        expected_cart = {item['item']['name']: item for item in expected_cart}
        cart = {
            item['item']['name']: item for item in requested_time.pop('cart')
        }
        cart_item_ids = set()
        for cart_item in cart.values():
            item_id = cart_item['item'].pop('id')
            assert item_id not in cart_item_ids
            cart_item_ids.add(item_id)
        assert cart_item_ids == set(range(len(cart)))
        assert cart == expected_cart

        place_id = order['place_id']
        place = places_dict[place_id]
        place_location = ast.literal_eval(place['location'])
        expected_place = {
            'id': place_id,
            'average_preparation_time': (
                place['average_preparation'].total_seconds() / 60
            ),
            'place_increment': place['extra_preparation'].total_seconds() / 60,
            'region_delivery_time_offset': 0.0,
            'brand_id': place['brand_id'],
            'is_fast_food': (order_type == 'fast_food'),
            'average_user_rating': place['rating_users'],
            'price_category': round(place['price_category_value']),
            'location': {'lon': place_location[0], 'lat': place_location[1]},
            'delivery_type': order['delivery_type'],
        }
        courier_type = order['delivery_zone_courier_type']
        if courier_type is not None and courier_type != 'yandex_rover':
            expected_place['courier_type'] = courier_type

        default_preparation_time = (
            fallback_picking_duration
            if order_type in {'retail', 'shop'}
            else fallback_cooking_duration
        ).total_seconds() / 60
        default_delivery_time = fallback_delivery_duration.total_seconds() / 60

        if order.get('shipping_type', 'delivery') == 'delivery':
            default_total_time = (
                max(
                    (
                        fallback_courier_arrival_duration
                        + fallback_place_waiting_duration
                    ).total_seconds()
                    / 60,
                    default_preparation_time,
                )
                + default_delivery_time
            )
        else:
            default_total_time = default_preparation_time
        default_total_time += (
            fallback_customer_waiting_duration.total_seconds() / 60
        )

        assert requested_time == {
            'id': place_id,
            'place': expected_place,
            'default_times': {
                'delivery_time': default_delivery_time,
                'cooking_time': default_preparation_time,
                'total_time': default_total_time,
                'boundaries': {
                    'min': round(default_total_time / 3),
                    'max': round(default_total_time * 3),
                },
            },
        }
        if not order_update.get('ml_provider', None):
            return eta_testcases_context.mockserver.make_response(status=500)
        if order_update['ml_provider'] == 'ml':
            cooking_time = order_update['cooking_time'].total_seconds() / 60
            delivery_time = order_update['delivery_time'].total_seconds() / 60
            total_time = order_update['total_time'].total_seconds() / 60
        else:
            cooking_time = default_preparation_time
            delivery_time = default_delivery_time
            total_time = default_total_time
        return utils.make_ml_response(
            place_id,
            cooking_time=cooking_time,
            delivery_time=delivery_time,
            total_time=total_time,
            request_id=request.query['request_id'],
            provider=order_update['ml_provider'],
        )

    return testcase


def partner_picking_slots(eta_testcases_context):
    brand_id = 777
    picking_slot_started_at = (
        eta_testcases_context.now_utc + datetime.timedelta(hours=1)
    )
    picking_slot_finished_at = (
        eta_testcases_context.now_utc + datetime.timedelta(hours=2)
    )

    eta_testcases_context.taxi_config.set_values(
        {'EATS_PARTNER_SLOTS_BRANDS_SETTINGS': {'brand_ids': [f'{brand_id}']}},
    )

    fallback_picking_duration = datetime.timedelta(
        seconds=eta_testcases_context.fallbacks['picking_duration'],
    )

    return {
        'orders': [
            {
                'order': {
                    'place_id': 1,
                    'order_type': 'retail',
                    'delivery_type': 'native',
                    'shipping_type': 'delivery',
                    'order_status': 'created',
                    'picking_slot_started_at': picking_slot_started_at,
                    'picking_slot_finished_at': picking_slot_finished_at,
                },
                'expected_estimations': {
                    'picking_duration': {
                        'value': fallback_picking_duration,
                        'status': 'not_started',
                        'source': 'fallback',
                    },
                    'picked_up_at': {
                        'value': picking_slot_started_at,
                        'status': 'not_started',
                        'source': 'service',
                    },
                },
            },
        ],
        'places': [{'id': 1, 'brand_id': brand_id}],
    }


@pytest.fixture(
    params=[
        'courier_arrival_duration_nullopt',
        'courier_arrival_duration_fallback',
        'courier_arrival_duration_has_cargo_eta',  # TODO
        'courier_arrival_duration_has_courier_position',  # TODO
        'picking_nullopt',
        'picking_fallback',  # TODO
        'picking_retail',
        'cooking_duration_nullopt',
        'cooking_duration_fallback',
        'cooking_duration_order_cooking_time',
        'cooking_duration_place_preparation',
        'courier_arrival_at_nullopt',
        'courier_arrival_at_courier_arrival_duration',
        'courier_arrival_at_native_cooking_duration',
        'cooking_finishes_at_nullopt',
        'cooking_finishes_at_cooking_duration',
        'cooking_finishes_at_courier_arrival_duration',
        'place_waiting_duration_nullopt',
        'place_waiting_duration_rest',
        'place_waiting_duration_retail',
        'delivery_starts_at_nullopt',
        'delivery_starts_at_already_started',
        'delivery_starts_at_estimated',
        'delivery_duration_nullopt',
        'delivery_duration_fallback',
        'delivery_duration_cargo_eta',
        'delivery_duration_no_delivery_coordinates',
        'delivery_duration_cargo_position',
        'delivery_duration_delivery_time',
        'delivery_duration_route_from_place',
        'delivery_at_nullopt',
        'delivery_at',
        'complete_at_nullopt',
        'complete_at',
        'update_cargo_info',
        'update_retail_info',
        'update_ml_prediction',
        'partner_picking_slots',
    ],
)
def eta_testcase(
        request,
        eta_testcases_context,
        experiments3,
        make_order,
        make_place,
        db_insert_order,
        db_insert_place,
):
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_fallbacks_config3(**EATS_ETA_FALLBACKS), None,
    )
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_settings_config3(
            db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
            cargo_route_eta_ttl=CARGO_ROUTE_ETA_TTL,
            cargo_courier_position_ttl=CARGO_COURIER_POSITION_TTL,
            retail_info_ttl=RETAIL_INFO_TTL,
        ),
        None,
    )
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_corp_clients_config3(), None,
    )
    testcase = globals()[request.param](eta_testcases_context)
    for i, data in enumerate(testcase['orders']):
        if 'order_nr' not in data['order']:
            data['order']['order_nr'] = f'order-{i}'
        data['order'] = make_order(
            id=i,
            status_changed_at=eta_testcases_context.now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            **data['order'],
        )
        db_insert_order(data['order'])
    for place in testcase['places']:
        db_insert_place(make_place(**place))

    return testcase


__all__ = [
    '_eta_testcases_context',
    'eta_testcase',
    'DB_ORDERS_UPDATE_OFFSET',
    'CARGO_ROUTE_ETA_TTL',
    'CARGO_COURIER_POSITION_TTL',
    'RETAIL_INFO_TTL',
    'EATS_ETA_FALLBACKS',
]
