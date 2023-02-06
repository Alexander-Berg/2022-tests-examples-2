import datetime

import bson
import pytest

DEFAULT_RULES = [
    {
        'chat_type': 'client',
        'proactivity_class': 'short_ride',
        'macro_ids': [1],
        'percentage': 100,
        'tags': ['customer_care_short_ride'],
        'countries': ['rus'],
        'tariffs': ['econom'],
    },
    {
        'chat_type': 'client',
        'proactivity_class': 'point_b_cash',
        'macro_ids': [1],
        'percentage': 100,
        'tags': ['customer_care_point_b_cash'],
        'countries': ['rus'],
    },
]
LONG_RIDE_ORDER = {
    '_id': 'some_order_id',
    'nz': 'msk',
    'request': {'payment': {'type': 'cash'}},
    'performer': {'taxi_alias': {'id': 'some_alias_id'}},
    'statistics': {'travel_time': 300, 'travel_distance': 1000},
    'payment_tech': {'type': 'cash'},
}
SHORT_RIDE_ORDER = {
    '_id': 'some_order_id',
    'nz': 'msk',
    'request': {'payment': {'type': 'cash'}},
    'performer': {'taxi_alias': {'id': 'some_alias_id'}},
    'statistics': {'travel_time': 180, 'travel_distance': 600},
    'payment_tech': {'type': 'cash'},
}
CARD_TO_CASH_ORDER = {
    '_id': 'some_order_id',
    'nz': 'msk',
    'request': {'payment': {'type': 'card'}},
    'performer': {'taxi_alias': {'id': 'some_alias_id'}},
    'statistics': {'travel_time': 340, 'travel_distance': 10000},
    'payment_tech': {'type': 'cash'},
}
POINT_B_COMPLETE_ORDER_PROC = {
    '_id': 'some_order_id',
    'order': {
        'calc': {
            'distance': 10000,
            'time': 1800,
            'allowed_tariffs': {'__park__': {'econom': 500.5}},
        },
        'performer': {'paid_supply': True},
        'request': {'sp': 1.2, 'destinations': [{'geopoint': [35.0, 55.0]}]},
        'fixed_price': {'paid_supply_price': 150},
        'cost': 650,
    },
    'order_info': {
        'statistics': {
            'status_updates': [
                {
                    'p': {
                        'taxi_status': 'complete',
                        'geopoint': [35.001, 55.001],
                    },
                },
            ],
        },
    },
    'candidates': [{'tariff_class': 'econom'}],
    'performer': {'candidate_index': 0},
}
EMPTY_FEEDBACK = {
    'call_me': False,
    'app_comment': False,
    'choices': {},
    'rating': 3,
}
RUS_TARIFF_SETTINGS = {
    'zones': [{'zone': 'msk', 'tariff_settings': {'country': 'rus'}}],
}


@pytest.mark.parametrize(
    [
        'expires_at',
        'percentage',
        'rules',
        'archive_api_status',
        'order',
        'order_proc',
        'feedback_status',
        'feedback',
        'tariff_settings',
        'expected_fetch_order',
        'expected_fetch_order_proc',
        'expected_fetch_tariff',
        'expected_fetch_feedback',
        'expected_create_chat',
        'expected_create_chat_tags',
    ],
    [
        # All OK
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            True,
            ['customer_care_short_ride', 'proactivity_chat'],
        ),
        # No travel distance
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            {
                '_id': 'some_order_id',
                'nz': 'msk',
                'request': {'payment': {'type': 'cash'}},
                'performer': {'taxi_alias': {'id': 'some_alias_id'}},
                'statistics': {'travel_time': 180, 'total_distance': 600},
                'payment_tech': {'type': 'cash'},
            },
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            True,
            ['customer_care_short_ride', 'proactivity_chat'],
        ),
        # Expired
        (
            datetime.datetime.utcnow() - datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            False,
            False,
            False,
            False,
            False,
            None,
        ),
        # Order not found
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            404,
            None,
            None,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            False,
            False,
            False,
            False,
            None,
        ),
        # Feedback not found
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            404,
            None,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            True,
            ['customer_care_short_ride', 'proactivity_chat'],
        ),
        # Not empty feedback
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            {
                'call_me': False,
                'app_comment': False,
                'choices': {},
                'msg': 'some message',
            },
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Zero global percentage
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            0,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            False,
            False,
            False,
            False,
            False,
            None,
        ),
        # Zero rule percentage
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            [
                {
                    'chat_type': 'client',
                    'proactivity_class': 'short_ride',
                    'macro_ids': [1],
                    'percentage': 0,
                    'tags': ['customer_care_short_ride'],
                    'countries': ['rus'],
                    'tariffs': ['econom'],
                },
            ],
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Tariff mismatch
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            [
                {
                    'chat_type': 'client',
                    'proactivity_class': 'short_ride',
                    'macro_ids': [1],
                    'percentage': 100,
                    'tags': ['customer_care_short_ride'],
                    'countries': ['rus'],
                    'tariffs': ['maybach'],
                },
            ],
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Not so short ride
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            LONG_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Point B changed
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            LONG_RIDE_ORDER,
            {
                '_id': 'some_order_id',
                'changes': {'objects': [{'n': 'destinations'}]},
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.001, 55.001],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Payment type changed to card, complete far from point B
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.1, 55.1],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            True,
            ['customer_care_point_b_cash', 'proactivity_chat'],
        ),
        # Payment didn't change
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            LONG_RIDE_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.1, 55.1],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # No destinations
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {'sp': 1.2},
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.1, 55.1],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Empty destinations
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {'sp': 1.2, 'destinations': []},
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.1, 55.1],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Completed at point B
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.0, 55.0],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Many destinations, complete at point B
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [
                            {'geopoint': [35.5, 55.5]},
                            {'geopoint': [35.0, 55.0]},
                        ],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'p': {
                                    'taxi_status': 'complete',
                                    'geopoint': [35.0, 55.0],
                                },
                            },
                        ],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # No geopoint in status_updates
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [{'p': {'taxi_status': 'complete'}}],
                    },
                },
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # Empty status_updates in order_proc
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            CARD_TO_CASH_ORDER,
            {
                '_id': 'some_order_id',
                'order': {
                    'calc': {
                        'distance': 1000,
                        'time': 1800,
                        'allowed_tariffs': {'__park__': {'econom': 500}},
                    },
                    'performer': {'paid_supply': True},
                    'request': {
                        'sp': 1.2,
                        'destinations': [{'geopoint': [35.0, 55.0]}],
                    },
                    'fixed_price': {'paid_supply_price': 150},
                    'cost': 650,
                },
                'order_info': {'statistics': {'status_updates': []}},
                'candidates': [{'tariff_class': 'econom'}],
                'performer': {'candidate_index': 0},
            },
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # No order statistics
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            {
                '_id': 'some_order_id',
                'nz': 'msk',
                'request': {'payment': {'type': 'cash'}},
                'performer': {'taxi_alias': {'id': 'some_alias_id'}},
                'statistics': {},
                'payment_tech': {'type': 'cash'},
            },
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            RUS_TARIFF_SETTINGS,
            True,
            True,
            True,
            True,
            False,
            None,
        ),
        # No zones
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            {'zones': []},
            True,
            True,
            True,
            False,
            False,
            None,
        ),
        # No tariff settings in zone
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            {'zones': [{'zone': 'msk'}]},
            True,
            True,
            True,
            False,
            False,
            None,
        ),
        # No country in tariff settings
        (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
            100,
            DEFAULT_RULES,
            200,
            SHORT_RIDE_ORDER,
            POINT_B_COMPLETE_ORDER_PROC,
            200,
            EMPTY_FEEDBACK,
            {'zones': [{'zone': 'msk', 'tariff_settings': {}}]},
            True,
            True,
            True,
            False,
            False,
            None,
        ),
    ],
)
@pytest.mark.servicetest
async def test_create_chat(
        stq_runner,
        mockserver,
        order_archive_mock,
        expires_at,
        percentage,
        rules,
        archive_api_status,
        order,
        order_proc,
        feedback_status,
        feedback,
        tariff_settings,
        expected_fetch_order,
        expected_fetch_order_proc,
        expected_fetch_tariff,
        expected_fetch_feedback,
        expected_create_chat,
        expected_create_chat_tags,
        taxi_config,
):
    proactivity_settings = {
        'create_chat_delay': 600,
        'create_chat_ttl': 3600,
        'percentage': percentage,
        'short_ride_max_travel_time': 196,
        'short_ride_max_travel_distance': 690,
        'short_ride_cost_to_pre_cost_max_ratio': 0.9,
        'short_ride_calc_distance_to_travel_distance_min_ratio': 2.89,
        'short_ride_calc_time_to_travel_time_min_ratio': 1.5,
        'complete_point_threshold': 300,
    }
    taxi_config.set_values(
        {
            'SUPPORT_PROACTIVITY_SETTINGS': proactivity_settings,
            'SUPPORT_PROACTIVITY_RULES': rules,
        },
    )

    @mockserver.handler('/archive-api/archive/order')
    def mock_order(request):
        assert request.json['id'] == 'some_order_id'
        assert not request.json['lookup_yt']
        if archive_api_status == 200:
            result = bytes(bson.BSON.encode({'doc': order}))
            return mockserver.make_response(result)
        return mockserver.make_response(b'{}', status=archive_api_status)

    if archive_api_status == 200:
        order_archive_mock.set_order_proc(order_proc)

    @mockserver.json_handler(
        '/passenger-feedback/passenger-feedback/v1/retrieve',
    )
    def mock_feedback(request):
        assert request.json['order_id'] == 'some_order_id'
        if feedback_status == 200:
            return feedback
        return mockserver.make_response('{}', status=feedback_status)

    @mockserver.json_handler('/chatterbox/v1/tasks/init/customer_care')
    def mock_customer_care(request):
        assert request.json['order_id'] == 'some_order_id'
        assert request.json['tags'] == expected_create_chat_tags
        return {}

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def mock_taxi_tariff(request):
        assert request.query['zone_names'] == 'msk'
        return tariff_settings

    await stq_runner.support_proactivity_create_chat.call(
        task_id='some_task_id',
        args=['some_order_id', expires_at.strftime('%Y-%m-%dT%H:%M:%SZ')],
    )
    assert mock_order.has_calls == expected_fetch_order
    assert (
        order_archive_mock.order_proc_retrieve.has_calls
        == expected_fetch_order_proc
    )
    assert mock_taxi_tariff.has_calls == expected_fetch_tariff
    assert mock_feedback.has_calls == expected_fetch_feedback
    assert mock_customer_care.has_calls == expected_create_chat
