# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import pytest

from tests_eats_proactive_support import utils

DETECTORS_CONFIG = {
    'unconfirmed_order': {
        'events_settings': [
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'unconfirmed_order',
            },
        ],
    },
}

ACTION_PAYLOAD_DEFAULT = {
    'cancel_reason': 'place.auto.not_sent',
    'caller': 'system',
}

ACTION_PAYLOAD_LONG_AGO = {
    'cancel_reason': 'place.auto.not_confirmed',
    'caller': 'system',
}

ACTION_PAYLOAD_PLACE_ROBOCALL = {
    'delay_sec': 0,
    'voice_line': 'dummy_voice_line',
}

PROBLEM_UNCONFIRMED_ORDER = {
    'cancellation_action_default': {
        'type': 'order_cancel',
        'payload': ACTION_PAYLOAD_DEFAULT,
    },
    'cancellation_action_order_sent_long_ago': {
        'type': 'order_cancel',
        'payload': ACTION_PAYLOAD_LONG_AGO,
    },
    'cancellation_action_order_sent_timeout_sec': 600,
    'place_robocall_action': {
        'type': 'place_robocall',
        'payload': ACTION_PAYLOAD_PLACE_ROBOCALL,
    },
    'summon_support_action': {
        'type': 'summon_support',
        'payload': {'hidden_comment_key': 'comment_key'},
    },
}

UNCONFIRMED_ORDER_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_unconfirmed_order_detector',
    consumers=['eats_proactive_support/unconfirmed_order_detector'],
    default_value={'enabled': True},
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


def assert_single_db_action_payload(psql, expected_action_payload):
    cursor = psql.cursor()
    cursor.execute('SELECT payload FROM eats_proactive_support.actions;')
    db_action_payload = cursor.fetchall()
    assert len(db_action_payload) == 1
    assert db_action_payload[0][0] == expected_action_payload


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_UNCONFIRMED_ORDER=PROBLEM_UNCONFIRMED_ORDER,
)
@UNCONFIRMED_ORDER_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,event_name,unconfirmed_order_action_type,
    unconfirmed_order_iteration,expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            'unconfirmed_order',
            'order_cancellation',
            None,
            1,
            1,
            ['order_cancel'],
        ),
        (
            '123',
            'unconfirmed_order',
            'place_robocall',
            0,
            1,
            1,
            ['place_robocall'],
        ),
        ('124', 'unconfirmed_order', 'order_cancellation', None, 0, 0, []),
        ('124', 'unconfirmed_order', 'place_robocall', 0, 0, 0, []),
        ('125', 'unconfirmed_order', 'order_cancellation', None, 0, 0, []),
        ('125', 'unconfirmed_order', 'place_robocall', 0, 0, 0, []),
        ('123', 'ready_to_send', 'order_cancellation', None, 0, 0, []),
        ('123', 'ready_to_send', 'place_robocall', 0, 0, 0, []),
    ],
)
async def test_unconfirmed_order_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        unconfirmed_order_action_type,
        unconfirmed_order_iteration,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': 'unconfirmed_order',
            'unconfirmed_order_action_type': unconfirmed_order_action_type,
            'unconfirmed_order_place_robocall_iteration': (
                unconfirmed_order_iteration
            ),
        },
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


@pytest.mark.now('2021-09-09T10:10:00+03:00')
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_UNCONFIRMED_ORDER=PROBLEM_UNCONFIRMED_ORDER,
)
@UNCONFIRMED_ORDER_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    ['order_nr', 'expected_action', 'expected_action_payload'],
    [
        # Event 'sent' was not received
        ('123', True, ACTION_PAYLOAD_DEFAULT),
        ('124', False, {}),
        # Event 'sent' was received at '2021-09-09T09:59:59+03:00'
        ('130', True, ACTION_PAYLOAD_LONG_AGO),
        ('131', False, {}),
        # Event 'sent' was received at '2021-09-09T10:00:01+03:00'
        ('132', True, ACTION_PAYLOAD_DEFAULT),
        ('133', False, {}),
    ],
)
async def test_sent_event(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_action,
        expected_action_payload,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'unconfirmed_order',
            'detector_name': 'unconfirmed_order',
            'unconfirmed_order_action_type': 'order_cancellation',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], 1 if expected_action else 0,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], 1 if expected_action else 0,
    )

    if expected_action:
        assert_single_db_action_payload(
            pgsql['eats_proactive_support'], expected_action_payload,
        )
