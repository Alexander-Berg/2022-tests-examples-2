import pytest


@pytest.fixture(name='generate_dashboard_mock')
def _generate_dashboard_mock(patch):
    @patch('dashboards.generator.generator.generate_dashboard')
    def _mock_func(
            config_path,
            user_config=None,
            title=None,
            upload=False,
            includes_dir=None,
            force=False,
            strict_mode=True,
            print_dashboard=False,
    ):
        return {}, 0

    return _mock_func


@pytest.fixture(name='disable_multiprocessing_pool')
def _disable_multiprocessing_pool(patch):
    @patch(
        'dashboards.generated.service.'
        'worker_pool.plugin.WorkerPool.on_startup',
    )
    async def _nothing_on_startup():
        pass

    @patch(
        'dashboards.generated.service.'
        'worker_pool.plugin.WorkerPool.on_shutdown',
    )
    async def _nothing_on_shutdown():
        pass
