# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import json
import pytest

from tests_eats_proactive_support import utils

DRIVER_PROFILE_RETRIEVE_URL = '/driver-profiles/v1/driver/profiles/retrieve'
PROBLEM_TYPE = 'courier_idle'
COURIER_ROBOCALL_TYPE = 'courier_robocall'
PHONE_ID = '12345'
DEFAULT_PARK_ID = '123'
DEFAULT_DRIVER_ID = '345'
DEFAULT_ORDER_NR = '100000-100000'


@pytest.fixture(name='mock_eats_robocall')
def _mock_eats_robocall(mockserver):
    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def mock(request):
        return mockserver.make_response(
            status=200, json={'call_id': 'dummy_external_task_id'},
        )

    return mock


@pytest.fixture(name='mock_driver_profile_retrieve')
def _mock_driver_profile_retrieve(mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_RETRIEVE_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': (
                            DEFAULT_PARK_ID + '_' + DEFAULT_PARK_ID
                        ),
                        'data': {'phone_pd_ids': [{'pd_id': PHONE_ID}]},
                    },
                ],
            },
        )

    return mock


@pytest.mark.parametrize(
    """db_action_state,expected_action_result,	
    expected_result_count,expected_exception_count, 	
    expected_driver_profile_called, expected_robocall_called, robocall_code, robocall_response""",
    [
        (
            'created',
            'success',
            1,
            0,
            1,
            1,
            200,
            {'call_id': 'dummy_external_task_id'},
        ),  # greenflow
        (
            'created',
            'failed',
            1,
            0,
            1,
            1,
            400,
            {'code': 'dummy_error_code_400', 'message': 'dummy_message_400'},
        ),  # 400_from_robocall
        (
            'created',
            'need_retry',
            1,
            0,
            1,
            1,
            500,
            {'code': 'dummy_error_code_500', 'message': 'dummy_message_500'},
        ),  # 500_from_robocall
    ],
    ids=['greenflow', '400_from_robocall', '500_from_robocall'],
)
async def test_actions_courier_robocall_greenflow_and_robocall_errors(
        stq_runner,
        pgsql,
        testpoint,
        mock_driver_profile_retrieve,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
        expected_driver_profile_called,
        expected_robocall_called,
        robocall_code,
        robocall_response,
        mockserver,
):
    order_nr = DEFAULT_ORDER_NR

    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def _mock_eats_robocall(request):
        return mockserver.make_response(
            status=robocall_code, json=robocall_response,
        )

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(
        pgsql,
        order_nr,
        'cancelled',
        park_id=DEFAULT_PARK_ID,
        driver_id=DEFAULT_DRIVER_ID,
    )
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_type = 'courier_robocall'
    voice_line = 'dummy_voice_line'
    action_payload = json.dumps({'delay_sec': 0, 'voice_line': voice_line})
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        action_type,
        action_payload,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )

    assert (
        mock_driver_profile_retrieve.times_called
        == expected_driver_profile_called
    )

    assert _mock_eats_robocall.times_called == expected_robocall_called
    real_robocall_request = _mock_eats_robocall.next_call()['request'].json
    assert real_robocall_request['context']['order_nr'] == order_nr
    assert real_robocall_request['scenario_name'] == voice_line
    assert real_robocall_request['personal_phone_id'] == PHONE_ID


@pytest.mark.parametrize(
    """park_driver_id, db_action_state,expected_action_result,
    expected_result_count,expected_exception_count, 
    expected_driver_profile_called, expected_communication_called,
    driver_profile_code""",
    [
        (
            '124',
            'created',
            'failed',
            1,
            0,
            1,
            0,
            400,
        ),  # 400_from_driver_profile
        (
            '126',
            'created',
            'need_retry',
            1,
            0,
            3,
            0,
            500,
        ),  # 500_from_driver_profile
    ],
    ids=['404_from_driver_profile', '500_from_driver_profile'],
)
async def test_actions_courier_robocall_driver_profiles_errors(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_robocall,
        park_driver_id,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
        expected_driver_profile_called,
        expected_communication_called,
        driver_profile_code,
        mockserver,
):
    order_nr = DEFAULT_ORDER_NR

    @mockserver.json_handler(DRIVER_PROFILE_RETRIEVE_URL)
    def mock_driver_profile_retrieve(request):
        return mockserver.make_response(status=driver_profile_code, json={})

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(
        pgsql,
        order_nr,
        'cancelled',
        park_id=DEFAULT_PARK_ID,
        driver_id=DEFAULT_DRIVER_ID,
    )
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_type = 'courier_robocall'
    voice_line = 'dummy_voice_line'
    action_payload = json.dumps({'delay_sec': 0, 'voice_line': voice_line})
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        action_type,
        action_payload,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )

    assert (
        mock_driver_profile_retrieve.times_called
        == expected_driver_profile_called
    )
    assert mock_eats_robocall.times_called == expected_communication_called


async def test_courier_robocall_wrong_action_payloads(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_robocall,
        mock_driver_profile_retrieve,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = DEFAULT_ORDER_NR
    await utils.db_insert_order(
        pgsql,
        order_nr,
        'taken',
        park_id=DEFAULT_PARK_ID,
        driver_id=DEFAULT_DRIVER_ID,
    )
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_type = COURIER_ROBOCALL_TYPE
    voice_line = 'dummy_voice_line'
    action_payload = json.dumps(
        {'delay_sec': 0, 'wrong_voice_line': voice_line},
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, action_type, action_payload, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_driver_profile_retrieve.times_called == 0
    assert mock_eats_robocall.times_called == 0
