import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_nomenclature_viewer_plugins import *  # noqa: F403 F401

from tests_eats_nomenclature_viewer import sql_adaptor  # pylint: disable=C5521


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_nomenclature_viewer,
        taxi_eats_nomenclature_viewer_monitor,
        testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_nomenclature_viewer.run_distlock_task
            if is_distlock
            else taxi_eats_nomenclature_viewer.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_nomenclature_viewer-') :]
        )

        should_fail = False

        @testpoint(
            f'eats-nomenclature-viewer_{periodic_short_name}::failure-injector',  # noqa: E501
        )
        def _fail(param):
            return {'inject': should_fail}

        @testpoint(
            f'eats-nomenclature-viewer_periodic-data::use-current-epoch',
        )
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_nomenclature_viewer.tests_control(reset_metrics=True)

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_viewer_monitor.get_metrics()
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
        except taxi_eats_nomenclature_viewer.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = await taxi_eats_nomenclature_viewer_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


@pytest.fixture
def sql(pg_cursor):
    return sql_adaptor.SqlAdaptor(pg_cursor)
