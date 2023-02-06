import datetime as dt

import pytest
import pytz

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_products_autodisable_plugins import *  # noqa: F403 F401


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
        taxi_eats_retail_products_autodisable,
        taxi_eats_retail_products_autodisable_monitor,
        testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_retail_products_autodisable.run_distlock_task
            if is_distlock
            else taxi_eats_retail_products_autodisable.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_retail_products_autodisable-') :]
        )

        should_fail = False

        @testpoint(
            f'eats-retail-products-autodisable_{periodic_short_name}::fail',
        )
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(
            f'eats-retail-products-autodisable_periodic-data::use-current-epoch',  # noqa: E501 pylint: disable=line-too-long
        )
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_retail_products_autodisable.tests_control(
            reset_metrics=True,
        )

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = (
            await taxi_eats_retail_products_autodisable_monitor.get_metrics()
        )
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
        except taxi_eats_retail_products_autodisable.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = (
            await taxi_eats_retail_products_autodisable_monitor.get_metrics()
        )
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


@pytest.fixture(name='enable_periodic_in_config')
def _enable_periodic_in_config(update_taxi_config):
    def do_enable_periodic_in_config(periodic_name):
        update_taxi_config(
            'EATS_RETAIL_PRODUCTS_AUTODISABLE_PERIODICS',
            {periodic_name: {'is_enabled': True, 'period_in_sec': 10800}},
        )

    return do_enable_periodic_in_config
