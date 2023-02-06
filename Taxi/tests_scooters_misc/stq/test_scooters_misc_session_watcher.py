# flake8: noqa: E501

import datetime
import uuid
import time

import pytest
from tests_plugins import utils

NOW = datetime.datetime.now()
TARIFF_TO_OFFER_TYPE_MAPPING = {
    'scooters_minutes': 'standart_offer',
    'b2b_tariff': 'standart_offer',
    'scooter_fixpoint': 'fix_point',
}
AUTH_INFO = {
    'yandex_uid': 'YANDEX_UID',
    'taxi_phone_id': 'PHONE_ID',
    'taxi_user_id': 'USER_ID',
}


def build_test_case(
        idle_minutes,
        expected_push,
        expect_session_drop,
        description,
        tag='old_state_riding',
        tariff='scooters_minutes',
        receive_idle_time=True,
        sent_notifications=None,
        current_offer_state=None,
):
    return pytest.param(
        tag,
        tariff,
        idle_minutes * 60,
        receive_idle_time,
        expect_session_drop,
        sent_notifications or [],
        expected_push,
        current_offer_state or {},
        id=description,
    )


@pytest.mark.parametrize(
    'tag, tariff, idle_time, receive_idle_time, expect_session_drop, sent_notifications, expected_push, current_offer_state',
    [
        build_test_case(
            idle_minutes=5,
            expected_push=None,
            expect_session_drop=False,
            description='5 idle min -> no actions',
        ),
        build_test_case(
            idle_minutes=15,
            expected_push='warning_push',
            expect_session_drop=False,
            description='15 idle min -> warning push',
        ),
        build_test_case(
            idle_minutes=15,
            expected_push=None,
            expect_session_drop=False,
            sent_notifications=['warning_push'],
            description='15 idle min & warning push sent -> no actions',
        ),
        build_test_case(
            idle_minutes=25,
            expected_push='session_drop_push',
            expect_session_drop=True,
            sent_notifications=['warning_push'],
            description='25 idle min -> session drop + final push',
        ),
        build_test_case(
            idle_minutes=25,
            expected_push=None,
            expect_session_drop=False,
            tariff='b2b_tariff',
            receive_idle_time=False,
            description='25 idle min & unknown tariff -> no actions (no rule in config)',
        ),
        build_test_case(
            idle_minutes=25,
            expected_push=None,
            expect_session_drop=False,
            tag='old_state_parking',
            receive_idle_time=False,
            description='25 idle min & unknown tag -> no actions (no rule in config)',
        ),
        build_test_case(
            idle_minutes=0,
            expected_push=None,
            expect_session_drop=False,
            tariff='scooter_fixpoint',
            receive_idle_time=True,
            current_offer_state={'remaining_time': 3 * 60},
            description='3 min left in fix -> no push',
        ),
        build_test_case(
            idle_minutes=0,
            expected_push='fix_will_end_soon_push',
            expect_session_drop=False,
            tariff='scooter_fixpoint',
            receive_idle_time=False,
            current_offer_state={'remaining_time': 1 * 60},
            description='1 min left in fix -> fix_will_end_soon push',
        ),
        build_test_case(
            idle_minutes=0,
            expected_push='fix_is_over_push',
            expect_session_drop=False,
            tariff='scooter_fixpoint',
            receive_idle_time=False,
            sent_notifications=['fix_will_end_soon_push'],
            current_offer_state={'remaining_time': 0},
            description='0 min left in fix -> fix_is_over push',
        ),
        build_test_case(
            idle_minutes=5,
            expected_push=None,
            expect_session_drop=False,
            tariff='scooter_fixpoint',
            receive_idle_time=True,
            sent_notifications=['fix_will_end_soon_push', 'fix_is_over_push'],
            current_offer_state={'remaining_time': 0},
            description='5 idle minutes after fix finish -> no action',
        ),
        build_test_case(
            idle_minutes=15,
            expected_push='warning_push',
            expect_session_drop=False,
            tariff='scooter_fixpoint',
            receive_idle_time=True,
            sent_notifications=['fix_will_end_soon_push', 'fix_is_over_push'],
            current_offer_state={'remaining_time': 0},
            description='15 idle minutes after fix finish -> warning_push',
        ),
        build_test_case(
            idle_minutes=25,
            expected_push='session_drop_push',
            expect_session_drop=True,
            tariff='scooter_fixpoint',
            receive_idle_time=True,
            sent_notifications=[
                'fix_will_end_soon_push',
                'fix_is_over_push',
                'warning_push',
            ],
            current_offer_state={'remaining_time': 0},
            description='25 idle min after fix finish -> session drop + final push',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_scooters_session_watcher.json')
async def test_session_watcher(
        testpoint,
        stq_runner,
        mockserver,
        mocked_time,
        tag,
        tariff,
        idle_time,
        receive_idle_time,
        expect_session_drop,
        sent_notifications,
        expected_push,
        current_offer_state,
        generate_uuid,
):
    mocked_time.set(NOW)
    session_id = generate_uuid
    object_id = generate_uuid
    user_id = generate_uuid
    tag_id = generate_uuid

    @testpoint('scooters_misc_session_watcher')
    def stq_testpoint(_):
        pass

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def car_telematics_state_mock(_):
        return {
            'sensors': [
                {
                    'id': 2103,
                    'name': 'mileage',
                    'since': int(utils.timestamp(NOW)) - idle_time,
                    'updated': 1636628400,
                    'value': 199.8,
                },
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/user/tag_add')
    def user_tag_add_mock(request):
        assert request.json == {
            'tag_name': expected_push,
            'object_ids': [user_id],
        }
        return {
            'tagged_objects': [
                {'tag_id': [generate_uuid], 'object_id': user_id},
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/drop')
    def sessions_drop_mock(request):
        assert request.headers['UserIdDelegation'] == user_id
        assert request.headers['AllowIncorrectPosition'] == '1'
        assert request.query['user_choice'] == 'accept'
        assert request.query['session_id'] == session_id
        assert request.query['evolution_mode'] == 'ignore_telematic'
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def car_tag_add_mock(request):
        assert request.json == {
            'tag_name': 'lock_command_tag',
            'object_ids': [object_id],
        }
        return {
            'tagged_objects': [
                {'tag_id': [generate_uuid], 'object_id': object_id},
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def sessions_current_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'segment': {
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': tariff,
                            'type': TARIFF_TO_OFFER_TYPE_MAPPING[tariff],
                        },
                        'current_offer_state': current_offer_state,
                    },
                    'current_performing': tag,
                },
                'meta': {
                    'instance_id': tag_id,
                    'session_id': session_id,
                    'user_id': user_id,
                    'object_id': object_id,
                },
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag/history')
    def car_tags_history_mock(request):
        assert request.query == {'car_id': object_id, 'tag_id': tag_id}
        return {
            'records': [
                {
                    'tag_id': tag_id,
                    'tag_details': {'tag': tag, 'performer': user_id},
                    'object_id': object_id,
                    'timestamp': (int(utils.timestamp(NOW)) - idle_time),
                    'action': 'evolve',
                },
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/billing/payment/info')
    def payment_info_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'current': [
                {'last_status_update': int(time.time()), 'task_status': 'ok'},
            ],
        }

    await stq_runner.scooters_misc_session_watcher.call(
        task_id='session_watcher',
        kwargs={
            'session_id': session_id,
            'auth_info': AUTH_INFO,
            'state': {'sent_notifications': sent_notifications},
        },
    )

    assert stq_testpoint.times_called == 1
    assert sessions_current_mock.times_called == 1
    assert payment_info_mock.times_called == 1

    assert car_tags_history_mock.times_called == int(receive_idle_time)
    assert car_telematics_state_mock.times_called == int(receive_idle_time)

    assert sessions_drop_mock.times_called == int(expect_session_drop)
    assert car_tag_add_mock.times_called == int(expect_session_drop)
    assert user_tag_add_mock.times_called == int(expected_push is not None)


@pytest.mark.experiments3(filename='exp3_scooters_session_watcher.json')
@pytest.mark.parametrize(
    'last_payment_status_prev, last_payment_status_curr, expected_event',
    [
        pytest.param(
            'ok', 'no_funds', 'last_payment_failed', id='last payment failed',
        ),
        pytest.param(
            'no_funds',
            'ok',
            'last_payment_succeeded',
            id='last payment succeeded',
        ),
        pytest.param('ok', 'ok', None, id='ok -> ok -> no event'),
        pytest.param(
            'no_funds',
            'no_funds',
            None,
            id='no_funds -> no_funds -> no event',
        ),
        pytest.param(
            None, 'no_funds', None, id='None -> no_funds -> no event',
        ),
    ],
)
async def test_payment_event(
        stq_runner,
        generate_uuid,
        mockserver,
        testpoint,
        last_payment_status_prev,
        last_payment_status_curr,
        expected_event,
):
    session_id = generate_uuid
    scooter_id = generate_uuid

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def sessions_current_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'segment': {
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': 'scooters_minutes',
                            'type': 'standart_offer',
                        },
                        'current_offer_state': {},
                    },
                    'current_performing': 'old_state_riding',
                },
                'meta': {
                    'instance_id': generate_uuid,
                    'session_id': session_id,
                    'user_id': generate_uuid,
                    'object_id': scooter_id,
                },
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/billing/payment/info')
    def payment_info_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'current': [
                {
                    'last_status_update': int(time.time()),
                    'task_status': last_payment_status_curr,
                },
            ],
        }

    @testpoint('check-payment-event')
    def event_testpoint(data):
        assert data == {'type': expected_event, 'scooter_id': scooter_id}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag/history')
    def _car_tag_history_mock(_):
        # does not matter in this test
        pass

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def _car_telematics_state_mock(_):
        # does not matter in this test
        pass

    await stq_runner.scooters_misc_session_watcher.call(
        task_id='session_watcher',
        kwargs={
            'session_id': session_id,
            'auth_info': AUTH_INFO,
            'state': {
                'sent_notifications': [],  # no matter here
                'last_payment_status': last_payment_status_prev,
            },
        },
    )

    assert sessions_current_mock.times_called == 1
    assert payment_info_mock.times_called == 1
    assert event_testpoint.times_called == int(expected_event is not None)


@pytest.mark.parametrize(
    'accelerator_pedal, last_payment_status, expected_event',
    [
        pytest.param(
            1, 'no_funds', 'last_payment_failed', id='last payment failed',
        ),
        pytest.param(
            0, 'ok', 'last_payment_succeeded', id='last payment succeeded',
        ),
        pytest.param(
            0, 'no_funds', None, id='acc disabled & no_funds -> no event',
        ),
        pytest.param(1, 'ok', None, id='acc enabled & ok -> no event'),
        pytest.param(None, 'ok', None, id='no acc info -> no event'),
        pytest.param(1, None, None, id='no payment info -> no event'),
    ],
)
async def test_telematics_based_payment_event(
        stq_runner,
        generate_uuid,
        mockserver,
        testpoint,
        load_json,
        experiments3,
        accelerator_pedal,
        last_payment_status,
        expected_event,
):
    session_id = generate_uuid
    scooter_id = generate_uuid

    config = load_json('exp3_scooters_session_watcher.json')['configs'][0]
    config['default_value'].update({'use_only_actual_payment_status': True})
    experiments3.add_config(**config)

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def sessions_current_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'segment': {
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': 'scooters_minutes',
                            'type': 'standart_offer',
                        },
                        'current_offer_state': {},
                    },
                    'current_performing': 'old_state_riding',
                },
                'meta': {
                    'instance_id': generate_uuid,
                    'session_id': session_id,
                    'user_id': generate_uuid,
                    'object_id': scooter_id,
                },
            },
            'car': {
                'model_id': 'ninebot',
                'number': '1234',
                'telematics': {'accelerator_pedal': accelerator_pedal},
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/billing/payment/info')
    def payment_info_mock(request):
        assert request.query == {'session_id': session_id}
        return {
            'current': [
                {
                    'last_status_update': int(time.time()),
                    'task_status': last_payment_status,
                },
            ],
        }

    @testpoint('check-payment-event')
    def event_testpoint(data):
        assert data == {'type': expected_event, 'scooter_id': scooter_id}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag/history')
    def _car_tag_history_mock(_):
        # does not matter in this test
        pass

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def _car_telematics_state_mock(_):
        # does not matter in this test
        pass

    await stq_runner.scooters_misc_session_watcher.call(
        task_id='session_watcher',
        kwargs={
            'session_id': session_id,
            'auth_info': AUTH_INFO,
            'state': {'sent_notifications': []},  # no matter here
        },
    )

    assert sessions_current_mock.times_called == 1
    assert payment_info_mock.times_called == 1
    assert event_testpoint.times_called == int(expected_event is not None)
