# flake8: noqa
# pylint: disable=import-error,wildcard-import,R1705
import datetime
import pytest

from tests_eats_proactive_support import utils


@pytest.fixture(name='mock_eats_core_order_support')
def _mock_eats_core_order_support(mockserver):
    @mockserver.json_handler(
        '/eats-core-order-support/internal-api/v1/order-support/meta',
    )
    def mock(request):
        order_nr = request.query.get('order_nr')
        if order_nr == '100000-100000':
            return mockserver.make_response(
                status=200,
                json={
                    'operator': {
                        'login': 'dummy_operator_login',
                        'assigned_at': '2020-04-28T12:00:00+03:00',
                    },
                    'cancellation': {'is_notified_by_operator': True},
                },
            )
        elif order_nr == '100000-100001':
            return mockserver.make_response(
                status=200,
                json={
                    'operator': {
                        'login': 'dummy_operator_login',
                        'assigned_at': '2020-04-28T12:00:00+03:00',
                    },
                    'cancellation': {'is_notified_by_operator': False},
                },
            )
        elif order_nr == '100000-100002':
            return mockserver.make_response(
                status=400,
                json={
                    'code': 'dummy_error_code_400',
                    'message': 'dummy_message_400',
                },
            )
        elif order_nr == '100000-100003':
            return mockserver.make_response(
                status=404,
                json={
                    'code': 'dummy_error_code_404',
                    'message': 'dummy_message_404',
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


async def test_actions_actor_no_db_action(stq_runner, pgsql, testpoint):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = '100000-100000'
    await utils.db_insert_order(pgsql, order_nr, 'cancelled')

    action_id = 1
    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': 'order_cancel',
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1


async def test_actions_actor_no_db_problem(stq_runner, pgsql, testpoint):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = '100000-100000'
    await utils.db_insert_order(pgsql, order_nr, 'cancelled')

    action_type = 'order_cancel'
    no_exist_db_problem_id = 123123
    action_id = await utils.db_insert_action(
        pgsql, no_exist_db_problem_id, order_nr, action_type, {}, 'created',
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


@pytest.mark.parametrize('db_action_state', ['skipped', 'abandoned'])
async def test_actions_actor_db_skipped_abandoned_action(
        stq_runner, pgsql, testpoint, db_action_state,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'success'

    order_nr = '100000-100000'
    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )
    action_type = 'order_cancel'
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, 'order_cancel', {}, db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    db_state = await utils.db_get_action_state(pgsql, action_id)
    assert db_state[0] == db_action_state
    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1


@pytest.mark.parametrize(
    """test_name,order_nr,action_type,action_config_enabled,
    expected_action_result,expected_action_skip_reason,
    expected_result_count,expected_exception_count,mock_times_called,
    expected_db_action_state""",
    [
        (
            'NOT_IMPLEMENTED_ACTION',
            '100000-100000',
            'order_cancel',
            True,
            'failed',
            None,
            1,
            0,
            1,
            'failed',
        ),
        (
            'SKIPPED_ACTION_BY_FILTER',
            '100000-100000',
            'eater_robocall',
            True,
            'success',
            'Operator already notified client about cancelled order.',
            1,
            0,
            1,
            'skipped',
        ),
        (
            'FAILED_FILTER_1',
            '100000-100002',
            'eater_robocall',
            True,
            'success',
            'Operator already notified client about cancelled order.',
            1,
            0,
            1,
            'skipped',
        ),
        (
            'FAILED_FILTER_2',
            '100000-100003',
            'eater_robocall',
            True,
            'success',
            'Operator already notified client about cancelled order.',
            1,
            0,
            1,
            'skipped',
        ),
        (
            'FAILED_FILTER_3',
            '100000-100004',
            'eater_robocall',
            True,
            'success',
            'Operator already notified client about cancelled order.',
            1,
            0,
            3,
            'skipped',
        ),
        (
            'DISABLED_ACTION_BY_CONFIG',
            '100000-100001',
            'eater_robocall',
            False,
            'success',
            'Action is disabled by config.',
            1,
            0,
            0,
            'skipped',
        ),
    ],
)
async def test_actions_actor_filter(
        taxi_config,
        taxi_eats_proactive_support,
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_core_order_support,
        test_name,
        order_nr,
        action_type,
        action_config_enabled,
        expected_action_result,
        expected_action_skip_reason,
        expected_result_count,
        expected_exception_count,
        mock_times_called,
        expected_db_action_state,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    if not action_config_enabled:
        taxi_config.set_values(
            {
                'EATS_PROACTIVE_SUPPORT_ACTIONS_SETTINGS_2': {
                    action_type: {
                        'enabled': action_config_enabled,
                        'max_exec_tries': 3,
                        'max_reschedule_counter': 3,
                        'reschedule_seconds': 10,
                        'ttl_seconds': 600,
                    },
                },
            },
        )
        await taxi_eats_proactive_support.invalidate_caches()

    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, action_type, {}, 'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert await utils.db_get_action_state(pgsql, action_id) == (
        expected_db_action_state,
        expected_action_skip_reason,
    )
    assert mock_eats_core_order_support.times_called == mock_times_called
    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )


@pytest.mark.parametrize(
    """order_nr,action_type,db_action_state,expected_action_result,
    expected_result_count,expected_exception_count,mock_times_called""",
    [
        ('100000-100000', 'eater_robocall', 'processing', 'success', 1, 0, 0),
        ('100000-100000', 'eater_robocall', 'performed', 'success', 1, 0, 0),
    ],
)
async def test_actions_actor_wip_or_performed_action(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_core_order_support,
        order_nr,
        action_type,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
        mock_times_called,
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
    action_id = await utils.db_insert_action(
        pgsql, problem_id, order_nr, action_type, {}, db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert mock_eats_core_order_support.times_called == mock_times_called
    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    """ttl_seconds,sleep_seconds,expected_action_result,
    expected_action_state,expected_result_count""",
    [(100, 150, 'failed', 'abandoned', 1), (200, 150, 'failed', 'failed', 1)],
)
async def test_actions_actor_ttl_action(
        taxi_eats_proactive_support,
        taxi_config,
        testpoint,
        mocked_time,
        pgsql,
        stq_runner,
        ttl_seconds,
        sleep_seconds,
        expected_action_result,
        expected_action_state,
        expected_result_count,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    taxi_config.set_values(
        {
            'EATS_PROACTIVE_SUPPORT_ACTIONS_SETTINGS_2': {
                'eater_robocall': {
                    'enabled': True,
                    'max_exec_tries': 3,
                    'max_reschedule_counter': 3,
                    'reschedule_seconds': 10,
                    'ttl_seconds': ttl_seconds,
                },
            },
        },
    )
    await taxi_eats_proactive_support.invalidate_caches()

    order_nr = '100000-100001'
    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )
    utc_time = mocked_time.now() + datetime.timedelta(hours=3)
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        'eater_robocall',
        {},
        'created',
        str(utc_time),
    )

    mocked_time.sleep(sleep_seconds)
    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': 'eater_robocall',
        },
    )

    db_state = await utils.db_get_action_state(pgsql, action_id)
    assert db_state[0] == expected_action_state
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )
