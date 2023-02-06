# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest


DETECTORS_CONFIG = {
    'finish_ultima_support': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'finished'},
        ],
    },
}


FINISH_ULTIMA_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_finish_ultima_support_detector',
    consumers=['eats_proactive_support/finish_ultima_support_detector'],
    is_config=True,
    default_value={'enabled': True},
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
@FINISH_ULTIMA_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,event_name,
    expected_stq_actions_count""",
    [
        ('123', 'finished', 1),
        # 126 - not ultima
        ('126', 'finished', 0),
    ],
)
async def test_finish_ultima_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        expected_stq_actions_count,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': 'finish_ultima_support',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_stq_actions_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_stq_actions_count,
    )

    assert (
        stq.eats_proactive_support_actions.times_called
        == expected_stq_actions_count
    )
    assert stq.eats_proactive_support_detections.times_called == 0
