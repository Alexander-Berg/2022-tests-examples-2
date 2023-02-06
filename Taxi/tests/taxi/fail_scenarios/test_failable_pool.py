import datetime

from asyncpg import exceptions as asyncpg_exceptions
import pytest

from taxi import config as config_module
from taxi.fail_scenarios import fail_scenarios
from taxi.fail_scenarios import failable_pool


@pytest.mark.now('2019-07-19T12:00:00+0300')
@pytest.mark.parametrize(
    ('do_fail', 'should_raise'),
    [pytest.param(False, False), pytest.param(True, True)],
)
async def test_failable_pool(do_fail, should_raise, db, stub, patch):
    class Config(config_module.Config):
        FAIL_SCENARIOS_MANAGER_CONFIG = [
            {
                'enabled': do_fail,
                'desc': 'for tests',
                'start_hour': 0,
                'end_hour': 23,
                'only_weekdays': False,
                'type': 'postgres_unavailable',
                'times_per_day': 1,
                'min_duration_seconds': datetime.timedelta(hours=23).seconds,
                'max_duration_seconds': datetime.timedelta(hours=23).seconds,
                'metric_name': 'integration_auth_fail_scenario_active',
            },
        ]

    async def _mock_send_metric(*args):
        pass

    def _mock_acquire(*args, **kwargs):
        return True

    config = Config(db)
    context = stub(
        config=config, client_solomon=stub(push_data=_mock_send_metric),
    )
    fail_manager = fail_scenarios.FailScenariosManager(
        config_name='FAIL_SCENARIOS_MANAGER_CONFIG',
        context=context,
        app_name='test_app',
    )
    await fail_manager.refresh_cache()

    pool = stub(acquire=_mock_acquire)

    fail_pool = failable_pool.FailablePool(pool, fail_manager)
    if should_raise:
        with pytest.raises(asyncpg_exceptions.PostgresError):
            assert fail_pool.acquire()
    else:
        assert fail_pool.acquire()
