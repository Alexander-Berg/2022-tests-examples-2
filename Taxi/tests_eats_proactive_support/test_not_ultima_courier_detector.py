# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from tests_eats_proactive_support import utils

DETECTORS_CONFIG = {
    'not_ultima_courier': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'taken'},
        ],
    },
}

TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'
MATCH_PROFILES_URL = '/driver-tags/v1/drivers/match/profile'

MAP_CARGO_ALIAS_TO_CLIENT_ID = {'111': {'client_id': '123'}}

PROBLEM_NOT_ULTIMA_COURIER = {
    'payload': {'hidden_comment_key': 'comment_key'},
    'type': 'summon_support',
}

TRACKING_RESPONSE = {
    'order_nr': '123',
    'claim_id': '123',
    'claim_alias': '111',
}

PERFORMER_RESPONSE = {
    'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
    'eats_profile_id': '123',
    'name': 'Kostya',
    'first_name': 'some first name',
    'legal_name': 'park_name_1',
    'driver_id': 'driver_id1',
    'park_id': 'park_id1',
    'taxi_alias_id': 'order_alias_id_1',
}


NOT_ULTIMA_COURIER_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_not_ultima_courier_detector',
    consumers=['eats_proactive_support/not_ultima_courier_detector'],
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


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_PROBLEM_NOT_ULTIMA_COURIER_1=PROBLEM_NOT_ULTIMA_COURIER,
)
@NOT_ULTIMA_COURIER_EXPERIMENT_ENABLED
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_not_ultima_courier_detector_problem(
        stq_runner, pgsql, stq, mockserver,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_performer(request):
        return mockserver.make_response(status=200, json=PERFORMER_RESPONSE)

    @mockserver.json_handler(MATCH_PROFILES_URL)
    def mock_tags(request):
        return mockserver.make_response(status=200, json={'tags': []})

    kwargs = {
        'order_nr': '123',
        'event_name': 'taken',
        'detector_name': 'not_ultima_courier',
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(pgsql['eats_proactive_support'], 1)
    assert_db_actions(pgsql['eats_proactive_support'], 1)

    assert mock_tracking.times_called == 1
    assert mock_performer.times_called == 1
    assert mock_tags.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 1

    action_task = stq.eats_proactive_support_actions.next_call()
    assert action_task['queue'] == 'eats_proactive_support_actions'
    assert action_task['kwargs']['order_nr'] == '123'
    assert action_task['kwargs']['action_type'] == 'summon_support'


@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG,
    EATS_PROACTIVE_SUPPORT_PROBLEM_NOT_ULTIMA_COURIER_1=PROBLEM_NOT_ULTIMA_COURIER,
)
@NOT_ULTIMA_COURIER_EXPERIMENT_ENABLED
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,
    expected_tracking_response, expected_performed_response, expected_tags_response,
    tracking_times_called, performer_times_called, tags_times_called""",
    [
        (
            '123',
            {'code': 200, 'body': TRACKING_RESPONSE},
            {'code': 200, 'body': PERFORMER_RESPONSE},
            {'code': 200, 'body': {'tags': ['eats_courier_is_ultima']}},
            1,
            1,
            1,
        ),
        ('124', None, None, None, 0, 0, 0),  # not ultima
        (
            '123',
            {'code': 400, 'body': {'code': '400', 'message': 'message'}},
            None,
            None,
            1,
            0,
            0,
        ),
        (
            '123',
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            None,
            None,
            1,
            0,
            0,
        ),
        (
            '123',
            {'code': 200, 'body': TRACKING_RESPONSE},
            {'code': 404, 'body': {'code': 'db_error', 'message': 'message'}},
            None,
            1,
            1,
            0,
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
            None,
            1,
            3,
            0,
        ),
        (
            '123',
            {'code': 200, 'body': TRACKING_RESPONSE},
            {'code': 200, 'body': PERFORMER_RESPONSE},
            {'code': 500, 'body': {'code': '500', 'message': 'message'}},
            1,
            1,
            3,
        ),
        ('unknown_order', None, None, None, 0, 0, 0),
    ],
)
async def test_not_ultima_courier_detector_no_problem(
        stq_runner,
        pgsql,
        stq,
        mockserver,
        order_nr,
        expected_tracking_response,
        expected_performed_response,
        expected_tags_response,
        tracking_times_called,
        performer_times_called,
        tags_times_called,
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

    @mockserver.json_handler(MATCH_PROFILES_URL)
    def mock_tags(request):
        return mockserver.make_response(
            status=expected_tags_response['code'],
            json=expected_tags_response['body'],
        )

    kwargs = {
        'order_nr': order_nr,
        'event_name': 'taken',
        'detector_name': 'not_ultima_courier',
    }

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123', kwargs=kwargs,
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_tracking.times_called == tracking_times_called
    assert mock_performer.times_called == performer_times_called
    assert mock_tags.times_called == tags_times_called
    assert stq.eats_proactive_support_actions.times_called == 0
