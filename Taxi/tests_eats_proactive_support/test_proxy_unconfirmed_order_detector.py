# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import pytest

from tests_eats_proactive_support import utils

CATALOG_STORAGE_RESPONSE = {
    'places': [
        {
            'place_id': 40,
            'created_at': '2021-01-01T09:00:00+06:00',
            'updated_at': '2021-01-01T09:00:00+06:00',
            'place': {
                'slug': 'some_slug',
                'enabled': True,
                'name': 'some_name',
                'revision': 1,
                'type': 'native',
                'business': 'restaurant',
                'launched_at': '2021-01-01T09:00:00+06:00',
                'payment_methods': ['cash', 'payture', 'taxi'],
                'gallery': [{'type': 'image', 'url': 'some_url', 'weight': 1}],
                'brand': {
                    'id': 100,
                    'slug': 'some_slug',
                    'name': 'some_brand',
                    'picture_scale_type': 'aspect_fit',
                },
                'address': {'city': 'Moscow', 'short': 'some_address'},
                'country': {
                    'id': 1,
                    'name': 'Russia',
                    'code': 'RU',
                    'currency': {'sign': 'RUB', 'code': 'RUB'},
                },
                'categories': [{'id': 1, 'name': 'some_name'}],
                'quick_filters': {
                    'general': [{'id': 1, 'slug': 'some_slug'}],
                    'wizard': [{'id': 1, 'slug': 'some_slug'}],
                },
                'region': {'id': 1, 'geobase_ids': [1], 'time_zone': 'UTC'},
                'location': {'geo_point': [52.569089, 39.60258]},
                'rating': {'users': 5.0, 'admin': 5.0, 'count': 1},
                'price_category': {'id': 1, 'name': 'some_name', 'value': 5.0},
                'extra_info': {},
                'features': {
                    'ignore_surge': False,
                    'supports_preordering': False,
                    'fast_food': False,
                },
                'timing': {
                    'preparation': 60.0,
                    'extra_preparation': 60.0,
                    'average_preparation': 60.0,
                },
                'sorting': {'weight': 5, 'popular': 5},
                'assembly_cost': 1,
            },
        },
    ],
}

DETECTORS_CONFIG = {
    'proxy_unconfirmed_order': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'ready_to_send'},
            {'enabled': True, 'delay_sec': 0, 'order_event': 'sent'},
        ],
    },
}

PROBLEM_UNCONFIRMED_ORDER = {
    'cancellation_action_default': {
        'type': 'order_cancel',
        'payload': {
            'cancel_reason': 'place.auto.not_sent',
            'caller': 'system',
        },
    },
    'cancellation_action_order_sent_long_ago': {
        'type': 'order_cancel',
        'payload': {
            'cancel_reason': 'place.auto.not_confirmed',
            'caller': 'system',
        },
    },
    'cancellation_action_order_sent_timeout_sec': 600,
    'place_robocall_action': {
        'type': 'place_robocall',
        'payload': {'delay_sec': 0, 'voice_line': 'dummy_voice_line'},
    },
    'summon_support_action': {
        'type': 'summon_support',
        'payload': {'hidden_comment_key': 'comment_key'},
    },
}

UNCONFIRMED_ORDER_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_proxy_unconfirmed_order_detector',
    consumers=['eats_proactive_support/proxy_unconfirmed_order_detector'],
    default_value={'enabled': False},
    clauses=[
        {
            'enabled': True,
            'extension_method': 'replace',
            'value': {
                'enabled': True,
                'payload': {
                    'cancellation_delay_sec': 1,
                    'place_robocall_delays_sec': [300, 600, 900],
                },
            },
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'personal_phone_id',
                                'set_elem_type': 'string',
                                'set': ['+7-777-777-7777'],
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'arg_name': 'brand_id',
                                'arg_type': 'string',
                                'value': '100',
                            },
                            'type': 'eq',
                        },
                        {'init': {'arg_name': 'is_vip'}, 'type': 'bool'},
                        {
                            'init': {
                                'arg_name': 'device_id',
                                'arg_type': 'string',
                                'value': 'some_device_id',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
        },
    ],
)


def assert_db_problems(psql, expected_db_problems_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.problems;')
    db_problems = cursor.fetchall()
    assert len(db_problems) == expected_db_problems_count


def assert_db_actions(psql, expected_db_actions_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.actions;')
    db_actions = cursor.fetchall()
    assert len(db_actions) == expected_db_actions_count


@pytest.fixture(name='mock_eats_tags')
def _mock_eats_tags(mockserver):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def mock(request):
        personal_phone_id = request.json['match'][0]['value']
        if personal_phone_id == '+7-777-777-7777':
            return mockserver.make_response(
                status=200, json={'tags': ['vip_eater']},
            )

        return mockserver.make_response(
            status=500, json={'code': 'code_500', 'message': 'message_500'},
        )

    return mock


@pytest.fixture(name='mock_eats_catalog_storage')
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/places/list',
    )
    def mock(request):
        place_id = request.json['place_ids'][0]
        if place_id == 40:
            return mockserver.make_response(
                status=200, json=CATALOG_STORAGE_RESPONSE,
            )

        return mockserver.make_response(
            status=500, json={'code': 'code_500', 'message': 'message_500'},
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_UNCONFIRMED_ORDER=PROBLEM_UNCONFIRMED_ORDER,
)
@UNCONFIRMED_ORDER_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,event_name,expected_eats_catalog_storage_count,
    expected_eats_tags_count,expected_stq_detections_count,
    expected_stq_detections_kwargs""",
    [
        (
            '123',
            'ready_to_send',
            1,
            1,
            1,
            [
                {
                    'order_nr': '123',
                    'detector_name': 'unconfirmed_order',
                    'event_name': 'unconfirmed_order',
                    'unconfirmed_order_action_type': 'order_cancellation',
                },
            ],
        ),
        (
            '123',
            'sent',
            1,
            1,
            3,
            [
                {
                    'order_nr': '123',
                    'detector_name': 'unconfirmed_order',
                    'event_name': 'unconfirmed_order',
                    'unconfirmed_order_action_type': 'place_robocall',
                    'unconfirmed_order_place_robocall_iteration': 0,
                },
                {
                    'order_nr': '123',
                    'detector_name': 'unconfirmed_order',
                    'event_name': 'unconfirmed_order',
                    'unconfirmed_order_action_type': 'place_robocall',
                    'unconfirmed_order_place_robocall_iteration': 1,
                },
                {
                    'order_nr': '123',
                    'detector_name': 'unconfirmed_order',
                    'event_name': 'unconfirmed_order',
                    'unconfirmed_order_action_type': 'place_robocall',
                    'unconfirmed_order_place_robocall_iteration': 2,
                },
            ],
        ),
        ('124', 'ready_to_send', 1, 0, 0, None),
        ('124', 'sent', 1, 0, 0, None),
        ('125', 'ready_to_send', 1, 1, 0, None),
        ('125', 'sent', 1, 1, 0, None),
        ('126', 'ready_to_send', 0, 0, 0, None),
        ('126', 'sent', 0, 0, 0, None),
        ('127', 'ready_to_send', 1, 1, 0, None),
        ('127', 'sent', 1, 1, 0, None),
    ],
)
async def test_proxy_unconfirmed_order_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        expected_eats_catalog_storage_count,
        expected_eats_tags_count,
        expected_stq_detections_count,
        expected_stq_detections_kwargs,
        mock_eats_catalog_storage,
        mock_eats_tags,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': 'proxy_unconfirmed_order',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert (
        mock_eats_catalog_storage.times_called
        == expected_eats_catalog_storage_count
    )
    assert mock_eats_tags.times_called == expected_eats_tags_count
    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )

    if expected_stq_detections_kwargs is not None:
        for expected_kwargs in expected_stq_detections_kwargs:
            task = stq.eats_proactive_support_detections.next_call()
            assert task['queue'] == 'eats_proactive_support_detections'

            kwargs = task['kwargs']
            if 'log_extra' in kwargs:
                del kwargs['log_extra']

            assert kwargs == expected_kwargs
