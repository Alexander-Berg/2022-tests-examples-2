# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from tests_eats_proactive_support import utils


DETECTORS_CONFIG = {
    'proxy_courier_not_assigned': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'confirmed'},
        ],
    },
}


COURIER_NOT_ASSIGNED_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_proxy_courier_not_assigned_detector',
    consumers=['eats_proactive_support/proxy_courier_not_assigned_detector'],
    is_config=True,
    default_value={'enabled': True, 'payload': {'ultima_delays_sec': 30}},
    clauses=[],
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
@COURIER_NOT_ASSIGNED_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,event_name,
    expected_stq_detections_count,expected_stq_detections_kwargs""",
    [
        (
            '123',
            'confirmed',
            1,
            [
                {
                    'order_nr': '123',
                    'detector_name': 'courier_not_assigned',
                    'event_name': 'courier_not_assigned',
                },
            ],
        ),
    ],
)
async def test_proxy_courier_not_assigned_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        expected_stq_detections_count,
        expected_stq_detections_kwargs,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': 'proxy_courier_not_assigned',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

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
