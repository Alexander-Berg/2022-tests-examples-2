# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from tests_eats_proactive_support import utils

TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'

DETECTORS_CONFIG = {
    'courier_not_assigned': {
        'events_settings': [
            {
                'delay_sec': 0,
                'enabled': True,
                'max_exec_tries': 2,
                'order_event': 'courier_not_assigned',
            },
        ],
    },
}

MAP_CARGO_ALIAS_TO_CLIENT_ID = {'111': {'client_id': '123'}}

PROBLEM_COURIER_NOT_ASSIGNED = {
    'summon_support_action': {
        'payload': {'hidden_comment_key': 'comment_key'},
        'type': 'summon_support',
    },
}

COURIER_DETECTORS_ENABLED = {
    'courier_not_assigned_enabled': True,
    'courier_delay_enabled': True,
}

TRACKING_RESPONSE = {
    'order_nr': '123',
    'claim_id': '123',
    'claim_alias': '111',
}


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
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_NOT_ASSIGNED_1=PROBLEM_COURIER_NOT_ASSIGNED,
    EATS_PROACTIVE_SUPPORT_COURIER_DETECTORS_FEAT_FLAGS=COURIER_DETECTORS_ENABLED,
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_tracking_response,
    expected_performed_response,tracking_times_called,
    performer_times_called, expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            {'code': 200, 'body': TRACKING_RESPONSE},
            {
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
            1,
            1,
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            None,
            1,
            0,
            1,
            1,
            ['summon_support'],
        ),
        (
            '123',
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            None,
            1,
            0,
            0,
            0,
            [],
        ),
        (
            '123',
            {'code': 200, 'body': TRACKING_RESPONSE},
            {'code': 404, 'body': {'code': 'db_error', 'message': 'message'}},
            1,
            1,
            1,
            1,
            ['summon_support'],
        ),
        (
            '123',
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
            0,
            0,
            [],
        ),
        ('unknown_order', None, None, 0, 0, 0, 0, []),
    ],
)
async def test_courier_not_assigned(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        order_nr,
        expected_tracking_response,
        expected_performed_response,
        tracking_times_called,
        performer_times_called,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
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
        'order_nr': order_nr,
        'event_name': 'courier_not_assigned',
        'detector_name': 'courier_not_assigned',
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

    assert mock_tracking.times_called == tracking_times_called
    assert mock_performer.times_called == performer_times_called
    assert stq.eats_proactive_support_actions.times_called == len(
        expected_stq_actions,
    )
    for _, expected_stq_action in enumerate(expected_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert action_task['kwargs']['action_type'] == expected_stq_action
