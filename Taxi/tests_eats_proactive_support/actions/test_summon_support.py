# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import json
import pytest

from tests_eats_proactive_support import utils

SUPPORT_MESSAGE_URL = '/eats-support-misc/v1/message-for-support'
PROBLEM_TYPE = 'start_ultima_support'
ACTION_TYPE = 'summon_support'
EXTERNAL_ID = 'some_id'


@pytest.fixture(name='mock_support_message')
def _mock_support_message(mockserver):
    @mockserver.json_handler(SUPPORT_MESSAGE_URL)
    def mock(request):
        return mockserver.make_response(status=200, json={'id': EXTERNAL_ID})

    return mock


@pytest.fixture(name='mock_support_message_400')
def _mock_support_message_400(mockserver):
    @mockserver.json_handler(SUPPORT_MESSAGE_URL)
    def mock(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'dummy_error_code_400',
                'message': 'dummy_message_400',
            },
        )

    return mock


@pytest.fixture(name='mock_support_message_500')
def _mock_support_message_500(mockserver):
    @mockserver.json_handler(SUPPORT_MESSAGE_URL)
    def mock(request):
        return mockserver.make_response(
            status=500,
            json={
                'code': 'dummy_error_code_500',
                'message': 'dummy_message_500',
            },
        )

    return mock


async def db_get_action_ext_id(pgsql, action_id):
    cursor = pgsql['eats_proactive_support'].cursor()
    cursor.execute(
        f"""SELECT external_id FROM eats_proactive_support.actions
            WHERE id = '{action_id}';""",
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    else:
        return None


async def test_actions_summon_support_success(
        stq_runner, pgsql, testpoint, mock_support_message,
):
    order_nr = '100000-100000'

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'success'

    await utils.db_insert_order(pgsql, order_nr, 'finished')
    await utils.db_insert_order_sensitive_data(pgsql, order_nr)
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_payload = json.dumps(
        {'hidden_comment_key': 'comment_key', 'message_key': 'message_key'},
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, ACTION_TYPE, action_payload, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    result_ext_id = await db_get_action_ext_id(pgsql, action_id)
    assert result_ext_id == EXTERNAL_ID

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_support_message.times_called == 1


async def test_actions_summon_support_400(
        stq_runner, pgsql, testpoint, mock_support_message_400,
):
    order_nr = '100000-100001'

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    await utils.db_insert_order(pgsql, order_nr, 'finished')
    await utils.db_insert_order_sensitive_data(pgsql, order_nr)
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_payload = json.dumps(
        {'hidden_comment_key': 'comment_key', 'message_key': 'message_key'},
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, ACTION_TYPE, action_payload, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_support_message_400.times_called == 1


async def test_actions_summon_support_500(
        stq_runner, pgsql, testpoint, mock_support_message_500,
):
    order_nr = '100000-100003'

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'need_retry'

    await utils.db_insert_order(pgsql, order_nr, 'finished')
    await utils.db_insert_order_sensitive_data(pgsql, order_nr)
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_payload = json.dumps(
        {'hidden_comment_key': 'comment_key', 'message_key': 'message_key'},
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, ACTION_TYPE, action_payload, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_support_message_500.times_called == 3


async def test_actions_summon_support_no_order(
        stq_runner, pgsql, testpoint, mock_support_message,
):
    order_nr = '100000-100003'

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    # await utils.db_insert_order(pgsql, order_nr, 'finished')
    # await utils.db_insert_order_sensitive_data(pgsql, order_nr)
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_payload = json.dumps(
        {'hidden_comment_key': 'comment_key', 'message_key': 'message_key'},
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, ACTION_TYPE, action_payload, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_support_message.times_called == 0


async def test_actions_summon_support_wrong_action_payload(
        stq_runner, pgsql, testpoint, mock_support_message,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = '100000-200000'
    await utils.db_insert_order(pgsql, order_nr, 'finished')
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    db_action_state = 'created'
    action_payload = json.dumps(
        {
            'wrong_hidden_comment_key': 'comment_key',
            'message_key': 'message_key',
        },
    )
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        ACTION_TYPE,
        action_payload,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_support_message.times_called == 0
