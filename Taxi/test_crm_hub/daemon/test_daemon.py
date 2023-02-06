from crm_hub.generated.custom_unit import run_cron


async def test_run_daemon(patch, cron_context):
    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._worker_function')
    async def _worker(*args, **kwargs):
        pass

    @patch('crm_hub.daemon.schedule.get_task_from_scheduler')
    async def _get_task(*args, **kwargs):
        return 1, None

    await run_cron.main(['crm_hub.daemon.run_daemon', '-t', '0'])


async def test_run_daemon_v2(patch, cron_context):
    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._worker_function')
    async def _worker(*args, **kwargs):
        pass

    @patch('crm_hub.daemon.schedule.get_task_from_scheduler_v2')
    async def _get_task(*args, **kwargs):
        return 1, None

    await run_cron.main(['crm_hub.daemon.run_daemon_v2', '-t', '0'])
