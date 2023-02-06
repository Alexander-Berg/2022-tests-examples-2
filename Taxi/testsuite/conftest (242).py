import copy
import datetime as dt

from psycopg2 import extras
import pytest
import pytz

# root conftest for service eats-nomenclature-collector
pytest_plugins = ['eats_nomenclature_collector_plugins.pytest_plugins']


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_nomenclature_collector'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture(name='to_utc_datetime')
def _to_utc_datetime():
    def do_to_utc_datetime(stamp):
        if not isinstance(stamp, dt.datetime):
            stamp = dt.datetime.fromisoformat(stamp)
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
        return stamp

    return do_to_utc_datetime


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_nomenclature_collector.run_distlock_task
            if is_distlock
            else taxi_eats_nomenclature_collector.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_nomenclature_collector-') :]
        )

        should_fail = False

        @testpoint(f'eats-nomenclature-collector_{periodic_short_name}::fail')
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(
            f'eats-nomenclature-collector_periodic-data::use-current-epoch',
        )
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_nomenclature_collector.tests_control(
            reset_metrics=True,
        )

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 1
        assert data['oks'] == 1
        assert data['fails'] == 0
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

        should_fail = True
        try:
            await periodic_runner(periodic_name)
        except taxi_eats_nomenclature_collector.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


@pytest.fixture
def stq_call_forward(stq_runner):
    async def impl(stq_next_call, expect_fail=False):
        await getattr(stq_runner, stq_next_call['queue']).call(
            task_id=stq_next_call['id'],
            args=stq_next_call['args'],
            kwargs=stq_next_call['kwargs'],
            expect_fail=expect_fail,
        )

    return impl


@pytest.fixture
def stq_enqueue_and_call(stq_runner):
    async def impl(queue, **kwargs):
        if 'reschedule_counter' in kwargs:
            if 'exec_tries' not in kwargs:
                kwargs['exec_tries'] = kwargs['reschedule_counter']
            # exec_tries = reschedule_count + error_count
            assert kwargs['exec_tries'] >= kwargs['reschedule_counter']

        await getattr(stq_runner, queue).call(**kwargs)

    return impl


@pytest.fixture
def update_taxi_config(taxi_config):
    """
    Updates only specified keys in the config, without touching other keys.
    E.g. if original config is `{ a: 1, b: 2}`, then value `{ b: 3, c: 4}`
    will set the config to `{ a: 1, b: 3, c: 4}`.
    """

    def impl(config_name, config_value):
        updated_config = copy.deepcopy(taxi_config.get(config_name))
        updated_config.update(config_value)
        taxi_config.set(**{config_name: updated_config})

    return impl
