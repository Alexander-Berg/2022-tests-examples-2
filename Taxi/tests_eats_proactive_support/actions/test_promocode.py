# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import json
import pytest

from tests_eats_proactive_support import utils

CORE_PROMOCODE_URL = '/eats-core-promocode/internal-api/v1/promocodes/create'
PROBLEM_TYPE = 'lateness'


@pytest.fixture(name='mock_eats_core_promocode')
def _mock_eats_core_promocode(mockserver):
    @mockserver.json_handler(CORE_PROMOCODE_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json={'id': 'dummy_external_id', 'code': 'dummy_code'},
        )

    return mock


@pytest.fixture(name='mock_eats_core_promocode_400')
def _mock_eats_core_promocode_400(mockserver):
    @mockserver.json_handler(CORE_PROMOCODE_URL)
    def mock(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'dummy_error_code_400',
                'message': 'dummy_message_400',
            },
        )

    return mock


@pytest.fixture(name='mock_eats_core_promocode_500')
def _mock_eats_core_promocode_500(mockserver):
    @mockserver.json_handler(CORE_PROMOCODE_URL)
    def mock(request):
        return mockserver.make_response(
            status=500,
            json={
                'code': 'dummy_error_code_500',
                'message': 'dummy_message_500',
            },
        )

    return mock


async def test_actions_promocode_success(
        stq_runner, pgsql, testpoint, mock_eats_core_promocode, load_json,
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

    action_type = 'promocode'
    action_payload = json.dumps(
        {'country': 'ru', 'max_value': '100', 'rate': '10'},
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

    assert mock_eats_core_promocode.times_called == 1
    assert mock_eats_core_promocode.next_call()['request'].json == load_json(
        'expected_promocode_request.json',
    )


async def test_actions_promocode_core_400(
        stq_runner, pgsql, testpoint, mock_eats_core_promocode_400, load_json,
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

    action_type = 'promocode'
    action_payload = json.dumps(
        {'country': 'ru', 'max_value': '100', 'rate': '10'},
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

    assert mock_eats_core_promocode_400.times_called == 1
    assert mock_eats_core_promocode_400.next_call()[
        'request'
    ].json == load_json('expected_promocode_request.json')


async def test_actions_promocode_core_500(
        stq_runner, pgsql, testpoint, mock_eats_core_promocode_500, load_json,
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

    action_type = 'promocode'
    action_payload = json.dumps(
        {'country': 'ru', 'max_value': '100', 'rate': '10'},
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

    assert mock_eats_core_promocode_500.times_called == 2
    assert mock_eats_core_promocode_500.next_call()[
        'request'
    ].json == load_json('expected_promocode_request.json')


async def test_actions_promocode_wrong_action_payload(
        stq_runner, pgsql, testpoint, mock_eats_core_promocode,
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
    action_type = 'promocode'
    action_payload = json.dumps(
        {'wrong_country': 'ru', 'max_value': '100', 'rate': '10'},
    )
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

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1

    assert mock_eats_core_promocode.times_called == 0
