import pytest

from crm_hub.generated.custom_unit import run_cron


@pytest.mark.parametrize(
    'action_type, action_class, reports',
    [
        ('check_crm_policy', 'PolicyAction', True),
        ('send_to_channel', 'SendAction', True),
        ('send_to_log', 'LogAction', True),
        ('idle', 'WaitAction', False),
        ('sending_finished', 'StopAction', True),
    ],
)
@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
async def test_actions(mockserver, patch, action_type, action_class, reports):
    @mockserver.json_handler('/crm-scheduler/v1/get_task_list')
    async def _scheduler_action(request):
        return mockserver.make_response(
            json={
                'task_type': action_type,
                'task_list': [
                    {
                        'id': 1337,
                        'time_delay_ms': 0,
                        'sending_id': '00000000000000000000000000000001',
                        'task_properties': [],
                    },
                ],
                'sending_finished_info': {
                    'id': 0,
                    'sending_id': '00000000000000000000000000000001',
                    'successfull': True,
                    'error': 'some error message',
                    'error_detail': [],
                },
            },
            status=200,
        )

    @mockserver.json_handler('/crm-scheduler/v1/report_task_ended')
    async def _scheduler_notify(request):
        assert reports
        return mockserver.make_response(status=200, json={})

    @patch(f'crm_hub.logic.schedule.action.{action_class}._do_action')
    async def _action(*args, **kwargs):
        pass

    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    await run_cron.main(['crm_hub.daemon.run_daemon', '-t', '0'])

    assert len(_action.calls) == 1


@pytest.mark.parametrize(
    'action_type, action_class, reports',
    [
        ('filter_step', 'FilterStep', True),
        ('pipe_step', 'PipeStep', True),
        ('idle', 'WaitStep', False),
        ('sending_finished', 'StopStep', True),
    ],
)
@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
async def test_steps_from_scheduler_v2(
        mockserver, patch, action_type, action_class, reports,
):
    @mockserver.json_handler('/crm-scheduler/v2/get_task_list')
    async def _scheduler_action(request):
        return mockserver.make_response(
            json={
                'task_type': action_type,
                'task_list': [
                    {
                        'id': 1337,
                        'time_delay_ms': 0,
                        'sending_id': '00000000000000000000000000000001',
                        'task_properties': [],
                    },
                ],
                'sending_finished_info': {
                    'id': 0,
                    'sending_id': '00000000000000000000000000000001',
                    'successfull': True,
                    'error': 'some error message',
                    'error_detail': [],
                },
            },
            status=200,
        )

    @mockserver.json_handler('/crm-scheduler/v2/report_task_ended')
    async def _scheduler_notify(request):
        assert reports
        return mockserver.make_response(status=200, json={})

    @patch(f'crm_hub.logic.schedule.steps.{action_class}._do_step')
    async def _action(*args, **kwargs):
        pass

    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    await run_cron.main(['crm_hub.daemon.run_daemon_v2', '-t', '0'])

    assert len(_action.calls) == 1
