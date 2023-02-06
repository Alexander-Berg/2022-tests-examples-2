# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from tests_eats_proactive_support import utils

TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'
CARGO_POINTS_ETA_URL = '/cargo-claims/api/integration/v1/claims/points-eta'

DETECTORS_CONFIG = {
    'courier_delay': {
        'events_settings': [
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'courier_delay_to_customer',
            },
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'courier_delay_to_restaurant',
            },
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'courier_delay_to_taken',
            },
        ],
    },
}

MAP_CARGO_ALIAS_TO_CLIENT_ID = {'111': {'client_id': '123'}}

PROBLEM_COURIER_DELAY = {
    'courier_delay_to_customer': {
        'payload': {'hidden_comment_key': 'comment_key'},
        'type': 'summon_support',
    },
    'courier_delay_to_restaurant': {
        'payload': {'hidden_comment_key': 'comment_key'},
        'type': 'summon_support',
    },
    'courier_delay_to_taken': {
        'payload': {'hidden_comment_key': 'comment_key'},
        'type': 'summon_support',
    },
}

TRACKING_RESPONSE = {
    'order_nr': '123',
    'claim_id': '123',
    'claim_alias': '111',
}

COURIER_DETECTORS_ENABLED = {
    'courier_not_assigned_enabled': True,
    'courier_delay_enabled': True,
}

SUPPORT_MISC_METADATA = {
    'eater_id': 'eater1',
    'eater_decency': 'good',
    'is_first_order': False,
    'is_blocked_user': False,
    'order_status': 'order_taken',
    'order_type': 'native',
    'delivery_type': 'our_delivery',
    'delivery_class': 'ultima',
    'is_fast_food': False,
    'app_type': 'eats',
    'country_code': 'RU',
    'country_label': 'Россия',
    'city_label': 'Москва',
    'order_created_at': '2021-01-01T09:00:00+06:00',
    'order_promised_at': '2021-01-01T09:00:00+06:00',
    'is_surge': False,
    'is_promocode_used': False,
    'persons_count': 1,
    'payment_method': 'taxi_payment',
    'order_total_amount': 123.9,
    'place_id': '123',
    'place_name': 'Lala',
    'is_sent_to_restapp': True,
    'is_sent_to_integration': True,
    'integration_type': 'native',
    # stupid time
    'courier_arrived_to_place_actual_time': '2021-01-01T09:00:00+06:00',
    'order_taken_actual_time': '2021-01-01T09:00:00+06:00',
}

SUPPORT_MISC_METADATA_FOR_ACTION = {
    'eater_id': 'eater1',
    'eater_decency': 'good',
    'is_first_order': False,
    'is_blocked_user': False,
    'order_status': 'order_taken',
    'order_type': 'native',
    'delivery_type': 'our_delivery',
    'delivery_class': 'ultima',
    'is_fast_food': False,
    'app_type': 'eats',
    'country_code': 'RU',
    'country_label': 'Россия',
    'city_label': 'Москва',
    'order_created_at': '2021-01-01T09:00:00+06:00',
    'order_promised_at': '2021-01-01T09:00:00+06:00',
    'is_surge': False,
    'is_promocode_used': False,
    'persons_count': 1,
    'payment_method': 'taxi_payment',
    'order_total_amount': 123.9,
    'place_id': '123',
    'place_name': 'Lala',
    'is_sent_to_restapp': True,
    'is_sent_to_integration': True,
    'integration_type': 'native',
    # no order_taken_actual_time
    # no courier_arrived_to_place_actual_time
}


def generate_points_eta_response(
        status='pending',
        type_str='destination',
        eta='2020-04-28T12:20:00+03:00',
        point_id=1,
):
    return {
        'id': 'temp_id',
        'route_points': [
            {
                'id': point_id + 10,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': 'return',
                'visit_order': 4,
                'visit_status': 'arrived',
                'visited_at': {'expected': '2019-04-28T12:20:00+03:00'},
            },
            {
                'id': point_id - 1,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': 'source',
                'visit_order': 2,
                'visit_status': 'visited',
                'visited_at': {'actual': '2019-04-28T10:20:00+03:00'},
            },
            {
                'id': point_id,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': type_str,
                'visit_order': 3,
                'visit_status': status,
                'visited_at': {'expected': eta},
            },
        ],
    }


@pytest.fixture(name='mock_eats_orders_tracking')
def _mock_eats_orders_tracking(mockserver):
    @mockserver.json_handler(TRACKING_URL)
    def mock(request):
        order_nr = request.query['order_nr']
        mock_response = {
            'order_nr': order_nr,
            'claim_id': order_nr,
            'claim_alias': '111',
        }
        return mockserver.make_response(status=200, json=mock_response)

    return mock


@pytest.fixture(name='mock_cargo_performer')
def _mock_cargo_performer(mockserver):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'code': 200,
                'body': {
                    'car_info': {
                        'model': 'car_model_1',
                        'number': 'car_number_1',
                    },
                    'eats_profile_id': '123',
                    'name': 'Kostya',
                    'first_name': 'some first name',
                    'legal_name': 'park_name_1',
                    'driver_id': 'driver_id1',
                    'park_id': 'park_id1',
                    'taxi_alias_id': 'order_alias_id_1',
                },
            },
        )

    return mock


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


def assert_single_db_action_payload(psql, expected_action_payload):
    cursor = psql.cursor()
    cursor.execute('SELECT payload FROM eats_proactive_support.actions;')
    db_action_payload = cursor.fetchall()
    assert len(db_action_payload) == 1
    assert db_action_payload[0][0] == expected_action_payload


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_COURIER_DETECTORS_FEAT_FLAGS=COURIER_DETECTORS_ENABLED,
)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """expected_tracking_response, expected_performed_response,
    tracking_times_called, performer_times_called""",
    [
        (
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            None,
            1,
            0,
        ),
        (
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            None,
            1,
            0,
        ),
        (
            {'code': 200, 'body': TRACKING_RESPONSE},
            {'code': 404, 'body': {'code': 'db_error', 'message': 'message'}},
            1,
            1,
        ),
        (
            {'code': 200, 'body': TRACKING_RESPONSE},
            {
                'code': 500,
                'body': {
                    'code': 500,
                    'body': {'code': '500', 'message': 'message'},
                },
            },
            1,
            3,
        ),
    ],
)
async def test_courier_delay_no_courier(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        expected_tracking_response,
        expected_performed_response,
        tracking_times_called,
        performer_times_called,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_tracking(request):
        return mockserver.make_response(
            status=expected_tracking_response['code'],
            json=expected_tracking_response['body'],
        )

    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_performer(request):
        return mockserver.make_response(
            status=expected_performed_response['code'],
            json=expected_performed_response['body'],
        )

    kwargs = {
        'order_nr': '123',
        'event_name': 'courier_delay_to_restaurant',
        'detector_name': 'courier_delay',
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_tracking.times_called == tracking_times_called
    assert mock_performer.times_called == performer_times_called
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_DELAY_1=PROBLEM_COURIER_DELAY,
    EATS_PROACTIVE_SUPPORT_COURIER_DETECTORS_FEAT_FLAGS=COURIER_DETECTORS_ENABLED,
)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_support_misc_response,expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            {'code': 200, 'body': SUPPORT_MISC_METADATA_FOR_ACTION},
            1,
            1,
            ['summon_support'],
        ),
        ('123', {'code': 200, 'body': SUPPORT_MISC_METADATA}, 0, 0, []),
        (
            '123',
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            0,
            0,
            [],
        ),
        ('unknown_order', None, 0, 0, []),
    ],
)
async def test_courier_delay_detector_to_restaurant(
        stq_runner,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_performer,
        mockserver,
        order_nr,
        expected_support_misc_response,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
):
    @mockserver.json_handler('/eats-support-misc/v1/client-task-metadata')
    def _mock_support_misc(request):
        return mockserver.make_response(
            status=expected_support_misc_response['code'],
            json=expected_support_misc_response['body'],
        )

    kwargs = {
        'order_nr': order_nr,
        'event_name': 'courier_delay_to_restaurant',
        'detector_name': 'courier_delay',
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_db_actions_count,
    )

    assert stq.eats_proactive_support_actions.times_called == len(
        expected_stq_actions,
    )
    for _, expected_stq_action in enumerate(expected_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert action_task['kwargs']['action_type'] == expected_stq_action


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_DELAY_1=PROBLEM_COURIER_DELAY,
    EATS_PROACTIVE_SUPPORT_COURIER_DETECTORS_FEAT_FLAGS=COURIER_DETECTORS_ENABLED,
)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_points_eta_response,expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            {
                'code': 200,
                'body': generate_points_eta_response(
                    eta='2020-04-28T12:50:00+03:00',
                ),
            },
            1,
            1,
            ['summon_support'],
        ),
        (
            '123',
            {'code': 200, 'body': generate_points_eta_response(eta=None)},
            0,
            0,
            [],
        ),
        (
            '123',
            {
                'code': 200,
                'body': generate_points_eta_response(
                    eta='2020-04-28T11:50:10+03:00',
                ),
            },
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            0,
            0,
            [],
        ),
        ('unknown_order', None, 0, 0, []),
    ],
)
async def test_courier_delay_detector_to_customer(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        mock_eats_orders_tracking,
        mock_cargo_performer,
        order_nr,
        expected_points_eta_response,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def _mock_cargo_eta(request):
        return mockserver.make_response(
            status=expected_points_eta_response['code'],
            json=expected_points_eta_response['body'],
        )

    kwargs = {
        'order_nr': order_nr,
        'event_name': 'courier_delay_to_customer',
        'detector_name': 'courier_delay',
        'max_allowed_arrival_to_customer_eta_sec': 30,
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_db_actions_count,
    )

    assert stq.eats_proactive_support_actions.times_called == len(
        expected_stq_actions,
    )
    for _, expected_stq_action in enumerate(expected_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert action_task['kwargs']['action_type'] == expected_stq_action


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_DELAY_1=PROBLEM_COURIER_DELAY,
    EATS_PROACTIVE_SUPPORT_COURIER_DETECTORS_FEAT_FLAGS=COURIER_DETECTORS_ENABLED,
)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_support_misc_response,expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            {'code': 200, 'body': SUPPORT_MISC_METADATA_FOR_ACTION},
            1,
            1,
            ['summon_support'],
        ),
        ('123', {'code': 200, 'body': SUPPORT_MISC_METADATA}, 0, 0, []),
        (
            '123',
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            0,
            0,
            [],
        ),
        ('unknown_order', None, 0, 0, []),
    ],
)
async def test_courier_delay_detector_taken(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        mock_eats_orders_tracking,
        mock_cargo_performer,
        order_nr,
        expected_support_misc_response,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
):
    @mockserver.json_handler('/eats-support-misc/v1/client-task-metadata')
    def _mock_support_misc(request):
        return mockserver.make_response(
            status=expected_support_misc_response['code'],
            json=expected_support_misc_response['body'],
        )

    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def _mock_cargo_eta(request):
        return mockserver.make_response(
            status=200, json=generate_points_eta_response(),
        )

    kwargs = {
        'order_nr': order_nr,
        'event_name': 'courier_delay_to_taken',
        'detector_name': 'courier_delay',
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_db_actions_count,
    )

    assert stq.eats_proactive_support_actions.times_called == len(
        expected_stq_actions,
    )
    for _, expected_stq_action in enumerate(expected_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert action_task['kwargs']['action_type'] == expected_stq_action
