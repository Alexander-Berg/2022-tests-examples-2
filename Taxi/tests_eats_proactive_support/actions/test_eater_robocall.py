# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import json
import pytest

from tests_eats_proactive_support import utils


@pytest.fixture(name='mock_eats_robocall')
def _mock_eats_robocall(mockserver):
    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def mock(request):
        order_nr = request.json['context']['order_nr']
        if order_nr == '100000-100004':
            return mockserver.make_response(
                status=200, json={'call_id': 'dummy_external_task_id_2'},
            )
        if order_nr == '100000-100005':
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
        ('100000-100004', 'created', 'success', 1, 0),
        ('100000-100005', 'created', 'failed', 1, 0),
        ('100000-100006', 'created', 'need_retry', 1, 0),
    ],
)
async def test_actions_eater_robocall(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_robocall,
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
    await utils.db_insert_order_sensitive_data(pgsql, order_nr)
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    action_type = 'eater_robocall'
    action_payload = json.dumps(
        {'delay_sec': 0, 'voice_line': 'dummy_voice_line'},
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


@pytest.mark.experiments3(filename='gift_phone_exp.json')
@pytest.mark.parametrize(
    """order_nr,db_action_state,expected_action_result,
    expected_result_count, expected_exception_count""",
    [('100000-100004', 'created', 'success', 1, 0)],
)
async def test_actions_eater_robocall_gift_phone(
        stq_runner,
        pgsql,
        testpoint,
        mockserver,
        mock_eats_robocall,
        order_nr,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
):
    @mockserver.json_handler(
        '/eats-core-orders/internal-api/v1/order/100000-100004/metainfo',
    )
    def _eda_core_order_metainfo_(request):
        return {
            'order_nr': '100000-100004',
            'location_latitude': 55.754638,
            'location_longitude': 37.621642,
            'is_asap': False,
            'place_id': '305715',
            'region_id': '1',
            'order_meta_information': {
                'meta_information': {
                    'decimal_price': True,
                    'gift_by_phone': {
                        'name': 'Валя',
                        'type': 'gift_by_phone',
                        'phone_number': '+71234445566',
                    },
                },
            },
        }

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        assert request.json['value'] == '+71234445566'
        assert request.json['validate'] is True
        return {'id': 'phone_id', 'value': '+71234445566'}

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(pgsql, order_nr, 'lateness')

    action_type = 'eater_robocall'
    action_payload = json.dumps(
        {'delay_sec': 0, 'voice_line': 'dummy_voice_line'},
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

    assert _eda_core_order_metainfo_.times_called == 1
    assert _phones_store.times_called == 1

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )
    assert mock_eats_robocall.times_called == 1


async def test_actions_eater_robocall_wrong_action_payload(
        stq_runner, pgsql, testpoint, mock_eats_robocall,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = '100000-200000'
    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    db_action_state = 'created'
    action_type = 'eater_robocall'
    action_payload = json.dumps(
        {'delay_sec': 0, 'wrong_voice_line': 'dummy_voice_line'},
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
