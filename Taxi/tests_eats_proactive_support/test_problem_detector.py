# flake8: noqa
# pylint: disable=import-error,wildcard-import
import datetime
import pytest

from tests_eats_proactive_support import utils


PROBLEM_ORDER_CANCELLED = {
    'courier.unable_to_find': {
        'actions': [
            {
                'type': 'eater_robocall',
                'payload': {
                    'delay_sec': 0,
                    'voice_line': 'sorry_no_couriers_available',
                },
            },
            {
                'type': 'eater_notification',
                'payload': {
                    'notification_code': 'order_cancelled.no_couriers',
                    'channels': ['push', 'taxi_push'],
                },
            },
        ],
    },
}

DETECTORS_CONFIG = {
    'order_cancel': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'cancelled'},
        ],
    },
}

CANCELLATION_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_cancellation_detector',
    consumers=['eats_proactive_support/cancellation_detector'],
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


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_ORDER_CANCELLED_2=PROBLEM_ORDER_CANCELLED,
)
@CANCELLATION_EXPERIMENT_ENABLED
@pytest.mark.pgsql(
    'eats_proactive_support',
    files=[
        'fill_info_for_problem_detector.sql',
        'fill_info_for_cancellation_experiment.sql',
    ],
)
@pytest.mark.parametrize(
    """order_nr,event_name,detector_name,expected_db_problems_count,
    expected_db_actions_count,expected_stq_actions""",
    [
        (
            '123',
            'cancelled',
            'order_cancel',
            1,
            2,
            ['eater_robocall', 'eater_notification'],
        ),
        ('123', 'cancelled', 'fake_name', 0, 0, []),
        ('124', 'cancelled', 'order_cancel', 0, 0, []),
        ('125', 'cancelled', 'order_cancel', 0, 0, []),
        ('126', 'cancelled', 'order_cancel', 1, 0, []),
    ],
)
async def test_problem_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        detector_name,
        expected_db_problems_count,
        expected_db_actions_count,
        expected_stq_actions,
):
    if order_nr == '126':
        pgsql['eats_proactive_support'].cursor().execute(
            'INSERT INTO eats_proactive_support.problems '
            '(order_nr, type) VALUES (\'126\', \'order_cancelled\');',
        )
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': detector_name,
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


PROBLEM_ORDER_CANCELLED_WITH_DEFAULT = {
    '__default__': {
        'actions': [
            {
                'type': 'eater_robocall',
                'payload': {
                    'delay_sec': 0,
                    'voice_line': 'sorry_no_couriers_available',
                },
            },
            {
                'type': 'eater_notification',
                'payload': {
                    'notification_code': 'order_cancelled.no_couriers',
                    'channels': ['push', 'taxi_push'],
                },
            },
        ],
    },
}


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_ORDER_CANCELLED_2=PROBLEM_ORDER_CANCELLED_WITH_DEFAULT,
)
@CANCELLATION_EXPERIMENT_ENABLED
@pytest.mark.pgsql(
    'eats_proactive_support',
    files=[
        'fill_info_for_problem_detector.sql',
        'fill_info_for_cancellation_experiment.sql',
    ],
)
async def test_problem_detector_default_config(stq_runner, pgsql, stq):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': '123',
            'event_name': 'cancelled',
            'detector_name': 'order_cancel',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 1)
    assert_db_actions(pgsql['eats_proactive_support'], 2)

    expected_stq_actions = ['eater_robocall', 'eater_notification']
    assert stq.eats_proactive_support_actions.times_called == len(
        expected_stq_actions,
    )
    for _, expected_stq_action in enumerate(expected_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == '123'
        assert action_task['kwargs']['action_type'] == expected_stq_action


def build_cancel_exp_with_phone(phone):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_proactive_support_cancellation_detector',
        consumers=['eats_proactive_support/cancellation_detector'],
        clauses=[
            {
                'enabled': True,
                'extension_method': 'replace',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set': [phone],
                        'arg_name': 'personal_phone_id',
                        'set_elem_type': 'string',
                    },
                },
            },
        ],
        default_value={'enabled': False},
    )


def build_cancel_exp_with_device(device):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_proactive_support_cancellation_detector',
        consumers=['eats_proactive_support/cancellation_detector'],
        clauses=[
            {
                'enabled': True,
                'extension_method': 'replace',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set': [device],
                        'arg_name': 'device_id',
                        'set_elem_type': 'string',
                    },
                },
            },
        ],
        default_value={'enabled': False},
    )


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_ORDER_CANCELLED_2=PROBLEM_ORDER_CANCELLED,
)
@pytest.mark.pgsql(
    'eats_proactive_support',
    files=[
        'fill_info_for_problem_detector.sql',
        'fill_info_for_cancellation_experiment.sql',
    ],
)
@pytest.mark.parametrize(
    ['expected_db_problems_count', 'order_nr'],
    (
        pytest.param(
            1, '123', marks=build_cancel_exp_with_phone('+7-777-777-7777'),
        ),
        pytest.param(
            0, '123', marks=build_cancel_exp_with_phone('+7-888-888-8888'),
        ),
        pytest.param(
            1, '126', marks=build_cancel_exp_with_device('some_device_id'),
        ),
        pytest.param(
            0,
            '126',
            marks=build_cancel_exp_with_device('some_wrong_device_id'),
        ),
    ),
)
async def test_cancellation_experiment(
        stq_runner, pgsql, expected_db_problems_count, order_nr,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id=order_nr,
        kwargs={
            'order_nr': order_nr,
            'event_name': 'cancelled',
            'detector_name': 'order_cancel',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.parametrize(
    """insert_order,db_updated_at_config_enabled, 
    db_updated_at_config_diff_seconds,expected_testpoint_times_called,mock_now""",
    [
        (True, True, 100, 1, '2021-01-01T09:00:00+06:00'),
        (True, True, 100, 1, '2021-01-01T12:00:00+03:00'),
        (False, True, 100, 0, '2021-01-01T12:00:00+03:00'),
        (True, False, 100, 0, '2021-01-01T12:00:00+03:00'),
        (True, True, 200, 0, '2021-01-01T12:00:00+03:00'),
    ],
)
async def test_problem_detector_no_new_events_in_db_since(
        taxi_eats_proactive_support,
        taxi_eats_proactive_support_monitor,
        taxi_config,
        testpoint,
        mocked_time,
        pgsql,
        stq_runner,
        insert_order,
        db_updated_at_config_enabled,
        db_updated_at_config_diff_seconds,
        expected_testpoint_times_called,
        mock_now,
):
    order_nr = '123'
    event_name = 'cancelled'
    detector_name = 'order_cancel'
    mocked_time.set(datetime.datetime.fromisoformat(mock_now))

    @testpoint('eats-proactive-support-NoNewEventsInPeriod')
    def _is_new_events_since_testpoint(data):
        pass

    if insert_order:
        await utils.db_insert_order(
            pgsql, order_nr, 'cancelled', str(mocked_time.now()),
        )

    sleep_seconds = 150
    mocked_time.sleep(sleep_seconds)
    taxi_config.set_values(
        {
            'EATS_PROACTIVE_SUPPORT_DISABLE_DETECTORS_BY_NO_EVENTS': {
                'enabled': db_updated_at_config_enabled,
                'period_since_no_updates_seconds': (
                    db_updated_at_config_diff_seconds
                ),
            },
        },
    )
    await taxi_eats_proactive_support.invalidate_caches()

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': detector_name,
        },
    )

    metrics = await taxi_eats_proactive_support_monitor.get_metric(
        'period_since_no_db_updates',
    )
    assert (
        abs(metrics['period_since_no_db_updates_seconds'] - sleep_seconds)
        <= 1e-06
    )

    assert (
        _is_new_events_since_testpoint.times_called
        == expected_testpoint_times_called
    )
