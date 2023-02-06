# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import json
import pytest

from tests_eats_proactive_support import utils


@pytest.fixture(name='mock_eats_core_cancel_order')
def _mock_eats_core_cancel_order(mockserver):
    @mockserver.json_handler(
        '/eats-core-cancel-order/internal-api/v1/cancel-order',
    )
    def mock(request):
        order_nr = request.json['order_nr']
        if order_nr == '100000-100000':
            return mockserver.make_response(
                status=200, json={'is_cancelled': True},
            )
        elif order_nr == '100000-100001':
            return mockserver.make_response(
                status=200, json={'is_cancelled': False},
            )
        elif order_nr == '100000-100003':
            return mockserver.make_response(
                status=400,
                json={
                    'code': 'dummy_error_code_400',
                    'message': 'dummy_message_400',
                },
            )
        return mockserver.make_response(
            status=500,
            json={
                'code': 'dummy_error_code_500',
                'message': 'dummy_message_500',
            },
        )

    return mock


@pytest.mark.parametrize(
    """order_nr,db_action_state,expected_action_result,
    expected_result_count,expected_exception_count""",
    [
        ('100000-100000', 'created', 'success', 1, 0),
        ('100000-100001', 'created', 'failed', 1, 0),
        ('100000-100003', 'created', 'failed', 1, 0),
        ('100000-100005', 'created', 'need_retry', 1, 0),
    ],
)
async def test_actions_order_cancel(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_core_cancel_order,
        order_nr,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    action_type = 'order_cancel'
    action_payload = json.dumps(
        {'cancel_reason': 'dummy_reason', 'caller': 'system'},
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

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )
