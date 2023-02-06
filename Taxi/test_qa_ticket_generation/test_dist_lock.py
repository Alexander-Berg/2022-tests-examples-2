import datetime

from aiohttp import web
import pytest

from testsuite.utils import callinfo

from tests_callcenter_stats.test_qa_ticket_generation import params
from tests_callcenter_stats.test_qa_ticket_generation import utils


def qa_ticket_gen_settings(enabled=True, operators_filter=None):
    return {
        'enabled': enabled,
        'min_tickets_per_operator': 3,
        'required_calls_lookup_rules': params.DEFAULT_LOOKUP_RULES,
        'operators_filter': operators_filter or {},
        'tracker_queue': 'CALLS',
        'tracker_auth_secret_name': 'secret',
        'tracker_summary_format': 'QA ticket',
        'tracker_ticket_fields': {},
    }


def settings(
        enabled=True,
        launch_time='00:00',
        boundary_time=None,
        stq_task_creation_delay=0,
        settings_ids=('rus',),
        settings_values=(qa_ticket_gen_settings(),),
):
    return {
        'enabled': enabled,
        'launch_time': launch_time,
        'boundary_time': boundary_time,
        'stq_task_creation_delay': stq_task_creation_delay,
        'settings_map': {
            key: value for key, value in zip(settings_ids, settings_values)
        },
    }


@pytest.mark.parametrize(
    [
        'expected_launch_time_point',
        'expected_boundary_time_point',
        'expected_agent_ids',
    ],
    (
        pytest.param(
            '2020-07-08T01:00:00+00:00',
            '2020-07-08T01:00:00+00:00',
            ['111', '222'],
            marks=[
                pytest.mark.now('2020-07-07T16:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='04:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T01:00:00+00:00',
            '2020-07-08T01:00:00+00:00',
            ['111', '222'],
            marks=[
                pytest.mark.now('2020-07-07T22:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='04:00', boundary_time='04:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T01:00:00+00:00',
            '2020-07-08T00:59:00+00:00',
            ['111', '222'],
            marks=[
                pytest.mark.now('2020-07-07T22:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='04:00', boundary_time='03:59'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T01:00:00+00:00',
            '2020-07-07T01:01:00+00:00',
            ['111'],
            marks=[
                pytest.mark.now('2020-07-07T22:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='04:00', boundary_time='04:01'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-06T21:00:00+00:00',
            '2020-07-06T21:00:00+00:00',
            ['111'],
            marks=[
                pytest.mark.now('2020-07-05T21:00:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='00:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-09T03:09:00+00:00',
            '2020-07-09T03:09:00+00:00',
            [],
            marks=[
                pytest.mark.now('2020-07-08T16:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='06:09'),
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_create_stq_task(
        taxi_callcenter_stats,
        stq,
        testpoint,
        set_now,
        expected_launch_time_point,
        expected_boundary_time_point,
        expected_agent_ids,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == expected_launch_time_point
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == len(expected_agent_ids)
        assert (
            result['data']['boundary_time_point']
            == expected_boundary_time_point
        )

    assert stq.operator_qa_ticket_generation.times_called == len(
        expected_agent_ids,
    )
    expected_boundary_time_point = ''.join(
        expected_boundary_time_point.rsplit(':', 1),
    )
    for _ in expected_agent_ids:
        stq_call = stq.operator_qa_ticket_generation.next_call()
        assert stq_call['kwargs']['agent_id'] in expected_agent_ids
        assert (
            utils.to_datetime(stq_call['kwargs']['time_range_from'])
            == utils.to_datetime(expected_boundary_time_point)
            - datetime.timedelta(days=1)
        )
        assert (
            stq_call['kwargs']['time_range_to'] == expected_boundary_time_point
        )
        assert stq_call['kwargs']['settings_id'] == 'rus'


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@utils.mark_qa_ticket_gen_settings(settings())
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_stq_fail(taxi_callcenter_stats, testpoint, mockserver, set_now):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def stq_agent_queue(request, queue_name):
        body = request.json
        assert body['kwargs']['time_range_from'] == '2020-07-06T21:00:00+0000'
        assert body['kwargs']['time_range_to'] == '2020-07-07T21:00:00+0000'
        assert body['kwargs']['settings_id'] == 'rus'
        if body['kwargs']['agent_id'] == '222':
            return web.Response(status=500)
        return web.Response(status=201, body='{}')

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == 1
        assert (
            result['data']['boundary_time_point']
            == '2020-07-07T21:00:00+00:00'
        )

    assert stq_agent_queue.times_called >= 2


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@utils.mark_qa_ticket_gen_settings(
    settings(enabled=False, boundary_time='invalid_boundary_time'),
)
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_disabled(taxi_callcenter_stats, stq, testpoint, set_now):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_sleep.wait_call(timeout=0.5)
        await set_now('2020-07-07T20:59:00+00:00')
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_wake_up.wait_call(timeout=0.5)
        await set_now('2020-07-07T21:00:00+00:00')
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_finished.wait_call(timeout=0.5)

    assert not stq.operator_qa_ticket_generation.times_called


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@utils.mark_qa_ticket_gen_settings(settings())
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_disable_while_sleeping(
        taxi_callcenter_stats, stq, testpoint, taxi_config, set_now,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        taxi_config.set_values(
            dict(
                CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(
                    enabled=False,
                ),
            ),
        )
        await taxi_callcenter_stats.invalidate_caches()
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_sleep.wait_call(timeout=0.5)
        await set_now(utils.pre_time_point(launch_time_point['data']))
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_wake_up.wait_call(timeout=0.5)
        await set_now(launch_time_point['data'])
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handle_dist_lock_finished.wait_call(timeout=0.5)

    assert not handle_dist_lock_sleep.times_called
    assert not handle_dist_lock_finished.times_called
    assert not stq.operator_qa_ticket_generation.times_called


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.parametrize(
    ['expected_stq_args'],
    (
        pytest.param(
            [('111', 'rus'), ('222', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(settings_values=(qa_ticket_gen_settings(),)),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(enabled=False),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(settings_ids=(), settings_values=()),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'rus'), ('222', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': [
                                        'krasnodar_cc',
                                        'volgograd_cc',
                                        'other_cc',
                                    ],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['volgograd_cc'],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('222', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['krasnodar_cc'],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={'callcenter_ids': []},
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'volgograd'), ('222', 'krasnodar')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_ids=('krasnodar', 'volgograd'),
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['krasnodar_cc'],
                                },
                            ),
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['volgograd_cc'],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'all'), ('222', 'all'), ('111', 'volgograd')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_ids=('all', 'volgograd'),
                        settings_values=(
                            qa_ticket_gen_settings(),
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['volgograd_cc'],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_1.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(settings()),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_2.sql'],
                ),
            ],
        ),
        pytest.param(
            [('111', 'rus')],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        settings_values=(
                            qa_ticket_gen_settings(
                                operators_filter={
                                    'callcenter_ids': ['volgograd_cc'],
                                },
                            ),
                        ),
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_stats', files=['call_history_2.sql'],
                ),
            ],
        ),
    ),
)
async def test_operators_filter(
        taxi_callcenter_stats, stq, testpoint, set_now, expected_stq_args,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == len(expected_stq_args)
        assert (
            result['data']['boundary_time_point']
            == '2020-07-07T21:00:00+00:00'
        )

    assert stq.operator_qa_ticket_generation.times_called == len(
        expected_stq_args,
    )
    for _ in expected_stq_args:
        stq_call = stq.operator_qa_ticket_generation.next_call()
        assert (
            stq_call['kwargs']['agent_id'],
            stq_call['kwargs']['settings_id'],
        ) in expected_stq_args


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.parametrize(
    ['expected_etas'],
    (
        pytest.param(
            [
                datetime.datetime(2020, 7, 7, 21, 00, 0),
                datetime.datetime(2020, 7, 7, 21, 00, 0),
            ],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(stq_task_creation_delay=0),
                ),
            ],
        ),
        pytest.param(
            [
                datetime.datetime(2020, 7, 7, 21, 00, 1, 234000),
                datetime.datetime(2020, 7, 7, 21, 00, 2, 468000),
            ],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(stq_task_creation_delay=1234),
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_stq_eta(
        taxi_callcenter_stats, stq, testpoint, set_now, expected_etas,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == len(expected_etas)
        assert (
            result['data']['boundary_time_point']
            == '2020-07-07T21:00:00+00:00'
        )

    assert stq.operator_qa_ticket_generation.times_called == len(expected_etas)
    for expected_eta in expected_etas:
        stq_call = stq.operator_qa_ticket_generation.next_call()
        assert stq_call['eta'] == expected_eta


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@utils.mark_qa_ticket_gen_settings(settings())
@pytest.mark.parametrize(
    [
        'new_settings',
        'expected_launch_time_point',
        'expected_boundary_time_point',
    ],
    (
        (
            settings(launch_time='04:00'),
            '2020-07-08T01:00:00+00:00',
            '2020-07-08T01:00:00+00:00',
        ),
        (
            settings(launch_time='21:00'),
            '2020-07-07T18:00:00+00:00',
            '2020-07-07T18:00:00+00:00',
        ),
        (
            settings(launch_time='16:00'),
            '2020-07-08T13:00:00+00:00',
            '2020-07-08T13:00:00+00:00',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_launch_time_change_while_sleeping(
        taxi_callcenter_stats,
        stq,
        testpoint,
        taxi_config,
        set_now,
        new_settings,
        expected_launch_time_point,
        expected_boundary_time_point,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        taxi_config.set_values(
            {
                'CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP': (
                    new_settings
                ),
            },
        )
        await taxi_callcenter_stats.invalidate_caches()

        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == expected_launch_time_point
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == 2
        assert (
            result['data']['boundary_time_point']
            == expected_boundary_time_point
        )

    assert not handle_dist_lock_finished.times_called
    assert stq.operator_qa_ticket_generation.times_called == 2
