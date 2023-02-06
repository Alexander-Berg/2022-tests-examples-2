import copy
import json
from typing import List

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_business_alerts_plugins import *  # noqa: F403 F401

from tests_eats_retail_business_alerts import models
from tests_eats_retail_business_alerts import (
    sql_adaptor,
)  # pylint: disable=C5521
from tests_eats_retail_business_alerts import utils


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_retail_business_alerts,
        taxi_eats_retail_business_alerts_monitor,
        testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_retail_business_alerts.run_distlock_task
            if is_distlock
            else taxi_eats_retail_business_alerts.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_retail_business_alerts-') :]
        )

        should_fail = False

        @testpoint(
            f'eats-retail-business-alerts_{periodic_short_name}::failure-injector',  # noqa: E501
        )
        def _fail(param):
            return {'inject': should_fail}

        @testpoint(
            f'eats-retail-business-alerts_periodic-data::use-current-epoch',
        )
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_retail_business_alerts.tests_control(
            reset_metrics=True,
        )

        await periodic_runner(periodic_name)
        assert _fail.has_calls

        metrics = await taxi_eats_retail_business_alerts_monitor.get_metrics()
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
        except taxi_eats_retail_business_alerts.PeriodicTaskFailed:
            pass
        assert _fail.has_calls

        metrics = await taxi_eats_retail_business_alerts_monitor.get_metrics()
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


@pytest.fixture(name='push_lb_message')
async def _push_lb_message(taxi_eats_retail_business_alerts):
    async def _do(topic_name, consumer_name, cookie, data):
        response = await taxi_eats_retail_business_alerts.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': consumer_name,
                    'data': data,
                    'topic': topic_name,
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200

    return _do


@pytest.fixture(name='assert_objects_equal')
def _assert_objects_equal():
    def do_assert(lhs: models.BaseObject, rhs: models.BaseObject):
        assert utils.recursive_dict(lhs) == utils.recursive_dict(rhs)

    return do_assert


@pytest.fixture(name='assert_objects_equal_without')
def _assert_objects_equal_without(assert_objects_equal):
    def do_assert(
            changed_object: models.BaseObject,
            expected_object: models.BaseObject,
            fields_to_reset: List[str],
    ):
        lhs = copy.deepcopy(changed_object)
        rhs = copy.deepcopy(expected_object)
        for field in fields_to_reset:
            lhs.reset_field_recursive(field)
            rhs.reset_field_recursive(field)
        assert_objects_equal(lhs, rhs)

    return do_assert


@pytest.fixture(name='assert_objects_lists_equal')
def _assert_objects_lists_equal():
    def do_assert(lhs: List[models.BaseObject], rhs: List[models.BaseObject]):
        lhs_sorted = [utils.recursive_dict(i) for i in sorted(lhs)]
        rhs_sorted = [utils.recursive_dict(i) for i in sorted(rhs)]
        assert lhs_sorted == rhs_sorted

    return do_assert
