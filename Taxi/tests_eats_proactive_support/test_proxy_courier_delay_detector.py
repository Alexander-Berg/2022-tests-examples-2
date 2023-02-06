# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from tests_eats_proactive_support import utils

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
    'courier_arrived_to_place_planned_time': '2021-01-01T09:00:00+06:00',
    'order_taken_planned_time': '2021-01-01T09:00:00+06:00',
    'courier_arrived_to_customer_planned_time': '2021-01-01T09:00:00+06:00',
}

DETECTORS_CONFIG = {
    'proxy_courier_delay': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'confirmed'},
            {'enabled': True, 'delay_sec': 0, 'order_event': 'taken'},
        ],
    },
}


COURIER_DELAY_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_proxy_courier_delay_detector',
    consumers=['eats_proactive_support/proxy_courier_delay_detector'],
    is_config=True,
    default_value={
        'enabled': True,
        'payload': {
            'delta_taken_trigger_sec': 30,
            'launch_before_arrival_to_customer_sec': 600,
            'delta_arrival_to_restaurant_trigger_sec': 0,
            'max_allowed_arrival_to_customer_eta_sec': 30,
        },
    },
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


@pytest.fixture(name='mock_eats_support_misc')
def _mock_eats_support_misc(mockserver):
    @mockserver.json_handler('/eats-support-misc/v1/client-task-metadata')
    def mock(request):
        return mockserver.make_response(status=200, json=SUPPORT_MISC_METADATA)

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@COURIER_DELAY_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,event_name,expected_eats_support_misc,
    expected_stq_detections_count,expected_stq_detections_kwargs""",
    [
        (
            '123',
            'confirmed',
            1,
            2,
            [
                {
                    'order_nr': '123',
                    'detector_name': 'courier_delay',
                    'event_name': 'courier_delay_to_restaurant',
                },
                {
                    'order_nr': '123',
                    'detector_name': 'courier_delay',
                    'event_name': 'courier_delay_to_taken',
                },
            ],
        ),
        (
            '123',
            'taken',
            1,
            1,
            [
                {
                    'order_nr': '123',
                    'detector_name': 'courier_delay',
                    'event_name': 'courier_delay_to_customer',
                    'max_allowed_arrival_to_customer_eta_sec': 30,
                },
            ],
        ),
    ],
)
async def test_proxy_courier_delay_detector(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        event_name,
        expected_eats_support_misc,
        expected_stq_detections_count,
        expected_stq_detections_kwargs,
        mock_eats_support_misc,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': event_name,
            'detector_name': 'proxy_courier_delay',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_support_misc.times_called == expected_eats_support_misc
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


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@COURIER_DELAY_EXPERIMENT_ENABLED
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """support_misc_response, support_misc_code, exp_times_called""",
    [
        ({'code': 'code_400', 'message': 'message_400'}, 400, 1),
        ({'code': 'code_500', 'message': 'message_500'}, 500, 3),
    ],
)
async def test_proxy_courier_delay_detector_support_misc_errors(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        support_misc_response,
        support_misc_code,
        exp_times_called,
):
    @mockserver.json_handler('/eats-support-misc/v1/client-task-metadata')
    def mock_support_misc(request):
        return mockserver.make_response(
            status=support_misc_code, json=support_misc_response,
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': '123',
            'event_name': 'taken',
            'detector_name': 'proxy_courier_delay',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_support_misc.times_called == exp_times_called
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0
