import datetime

import pytest

from taxi.stq.async_worker_ng import TaskInfo

from taxi_driver_metrics.stq.client import task as client_task


_EXAMPLE_DATA = {
    'eta': '2021-07-15T15:34:33.605726896+0000',
    'kwargs': {'log_extra': {'_link': '5689bdbce1ee45009a7447b0c68cd46f'}},
    'task_id': (
        'multioffer_order_event/68ea827b26503c8c931c3f20095d323a'
        '/1a520f74-27b2-4e99-8f7b-f3698aae74ed'
    ),
    'args': [
        {
            'zone': 'moscow',
            'timestamp': datetime.datetime(2021, 7, 21, 13, 31, 59, 418000),
            'candidate': {
                'tags': [
                    'high_activity',
                    'low_skips_of_trips',
                    'query_rule_tag_default',
                    'activity_85',
                    'medmask_off',
                    'cmpl',
                    'activity_95',
                    'OrderCompleteTagPushv2',
                    '2orders',
                    'bronze',
                ],
                'tariff_class': 'business',
                'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                'udid': '5b055e5de6c22ea265443a80',
                'driver_id': '123_bd90cbb670c74ab1a2a42347fb91537c',
                'time_to_a': 20,
                'driver_metrics': {
                    'activity_prediction': {
                        'w': -3,
                        't': -3,
                        'n': -7,
                        's': -3,
                        'r': -7,
                        'c': 14,
                        'p': -7,
                        'a': -6,
                        'o': -7,
                    },
                    'activity_blocking': {
                        'activity_threshold': 50,
                        'duration_sec': 800,
                    },
                    'type': 'dm_service',
                    'id': '60f8218f8039160046a1d0ef',
                    'activity': 97,
                    'dispatch': 'short',
                    'properties': [
                        'candidates_meta_missing',
                        'dispatch_short',
                    ],
                },
                'license': '9e8a9b2459a3444bac18a6d9e6f8f70d',
                'distance_to_a': 76,
            },
            'handler': 'seen_timeout',
            'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        },
        {
            'zone': 'moscow',
            'timestamp': datetime.datetime(2021, 7, 21, 13, 31, 59, 418000),
            'candidate': {
                'tariff_class': 'business',
                'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                'udid': '5b055d74e6c22ea2654346b2',
                'driver_id': '652df00dd486463983bb45e854d7009b',
                'time_to_a': 20,
                'driver_metrics': {
                    'activity_prediction': {
                        'w': -3,
                        't': -3,
                        'n': -7,
                        's': -3,
                        'r': -7,
                        'c': 14,
                        'p': -7,
                        'a': -6,
                        'o': -7,
                    },
                    'activity_blocking': {
                        'activity_threshold': 50,
                        'duration_sec': 200,
                    },
                    'type': 'dm_service',
                    'id': '60f8218f537f3200476f1692',
                    'activity': 86,
                    'dispatch': 'short',
                    'properties': [
                        'candidates_meta_missing',
                        'dispatch_short',
                    ],
                },
                'license': '9e667981a7d0484cb3e4a4b021f0bd82',
                'distance_to_a': 76,
            },
            'handler': 'seen_timeout',
            'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        },
        {
            'zone': 'moscow',
            'timestamp': datetime.datetime(2021, 7, 21, 13, 31, 59, 418000),
            'candidate': {
                'tags': [
                    'OrderCompleteTagPushv2',
                    'activity_85',
                    'query_rule_tag_default',
                    'medmask_off',
                    'high_activity',
                    '2orders',
                ],
                'tariff_class': 'business',
                'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                'udid': '5b0560b9e6c22ea26546d715',
                'driver_id': '254c87f934034086845511623f3e1585',
                'time_to_a': 177,
                'driver_metrics': {
                    'activity_prediction': {
                        'w': -3,
                        't': -3,
                        'n': -7,
                        's': -3,
                        'r': -7,
                        'c': 14,
                        'p': -7,
                        'a': -6,
                        'o': -7,
                    },
                    'activity_blocking': {
                        'activity_threshold': 50,
                        'duration_sec': 200,
                    },
                    'type': 'dm_service',
                    'id': '60f8218f537f320046118721',
                    'activity': 100,
                    'dispatch': 'short',
                    'properties': [
                        'candidates_meta_missing',
                        'dispatch_short',
                    ],
                },
                'license': '41d594aef10248b2924f0756399717a3',
                'distance_to_a': 569,
            },
            'handler': 'seen_timeout',
            'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        },
        {
            'zone': 'moscow',
            'timestamp': datetime.datetime(2021, 7, 21, 13, 31, 59, 418000),
            'candidate': {
                'tags': [
                    '2orders',
                    'HadOrdersLast30Days',
                    'OrderCompleteTagPush',
                    'cmpl',
                    'activity_95',
                    'activity_85',
                    'OrderCompleteTagPushv2',
                    'medmask_off',
                    'high_activity',
                ],
                'tariff_class': 'business',
                'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                'udid': '5b056131e6c22ea2654757be',
                'driver_id': '5dc516691fc44b389d5d269284251fba',
                'time_to_a': 192,
                'driver_metrics': {
                    'activity_prediction': {
                        'w': -3,
                        't': -3,
                        'n': -7,
                        's': -3,
                        'r': -7,
                        'c': 14,
                        'p': -7,
                        'a': -6,
                        'o': -7,
                    },
                    'activity_blocking': {
                        'activity_threshold': 50,
                        'duration_sec': 200,
                    },
                    'type': 'dm_service',
                    'id': '60f8218f8039160047dd7eda',
                    'activity': 91,
                    'dispatch': 'short',
                    'properties': [
                        'candidates_meta_missing',
                        'dispatch_short',
                    ],
                },
                'license': '5ed42dd660844519b9284841fd7a7d0a',
                'distance_to_a': 958,
            },
            'handler': 'seen_timeout',
            'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        },
        {
            'zone': 'moscow',
            'timestamp': datetime.datetime(2021, 7, 21, 13, 31, 59, 418000),
            'candidate': {
                'tags': [
                    'query_rule_tag_default',
                    'OrderCompleteTagPushv2',
                    'medmask_off',
                    'high_activity',
                    'HadOrdersLast30Days',
                    '2orders',
                ],
                'tariff_class': 'business',
                'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                'udid': '5b0560b9e6c22ea26546d6b4',
                'driver_id': '123_3b78535f5259456c9b05bc2075803af8',
                'time_to_a': 340,
                'driver_metrics': {
                    'activity_prediction': {
                        'w': -3,
                        't': -3,
                        'n': -7,
                        's': -3,
                        'r': -7,
                        'c': 14,
                        'p': -7,
                        'a': -6,
                        'o': -7,
                    },
                    'activity_blocking': {
                        'activity_threshold': 50,
                        'duration_sec': 200,
                    },
                    'type': 'dm_service',
                    'id': '60f8218f8039160046a1d0ee',
                    'activity': 63,
                    'dispatch': 'short',
                    'properties': [
                        'candidates_meta_missing',
                        'dispatch_short',
                    ],
                },
                'license': '33530dfa825b4be7ae8c293dcc5598f8',
                'distance_to_a': 969,
            },
            'handler': 'seen_timeout',
            'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        },
    ],
}


@pytest.mark.filldb()
@pytest.mark.now('2021-07-15T15:34:33Z')
@pytest.mark.config(
    DRIVER_METRICS_TAG_LIST_TO_STORE={
        'driver': ['medmask_off', 'gena'],
        'rider': ['t2'],
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': True}},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': False}},
            ),
        ),
    ],
)
async def test_multioffer_task_client(
        stq3_context, stq, dms_mockserver, order_core_mock,
):
    await client_task.task(
        stq3_context,
        TaskInfo(
            id=_EXAMPLE_DATA['task_id'],
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        *_EXAMPLE_DATA['args'],
    )
    assert dms_mockserver.event_new.times_called == 5
    event_new_call = dms_mockserver.event_new.next_call()['request'].json
    event_new_call['descriptor'].pop('tags')  # tags are random sorted
    assert event_new_call == {
        'created': '2021-07-21T13:31:59.418000+00:00',
        'descriptor': {'type': 'seen_timeout'},
        'extra_data': {
            'activity_value': 97,
            'dispatch_id': '60f8218f8039160046a1d0ef',
            'distance_to_a': 76,
            'driver_id': '123_bd90cbb670c74ab1a2a42347fb91537c',
            'dtags': ['medmask_off'],
            'rtags': [],
            'sp': None,
            'sp_alpha': None,
            'tariff_class': 'business',
            'time_to_a': 20,
            'replace_activity_with_priority': False,
            'calculate_priority': False,
        },
        'idempotency_token': (
            'o/68ea827b26503c8c931c3f20095d323a/'
            '1a520f74-27b2-4e99-8f7b-f3698aae74ed/'
            '5b055e5de6c22ea265443a80'
        ),
        'order_id': '5b9f3c7bc56f385ab574f07427828fba',
        'park_driver_profile_id': (
            'a3608f8f7ee84e0b9c21862beef7e48d'
            '_bd90cbb670c74ab1a2a42347fb91537c'
        ),
        'tariff_zone': 'moscow',
        'type': 'multioffer_order',
        'unique_driver_id': '5b055e5de6c22ea265443a80',
    }
