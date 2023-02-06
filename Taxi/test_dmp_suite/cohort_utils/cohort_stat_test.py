import itertools
import json

import pytest

from connection import greenplum as gp
from dmp_suite import datetime_utils as dtu
from dmp_suite.cohort_utils import (
    CohortSqlTaskSource,
    EventSourceTable,
    EventSelectQuery,
    CohortGPTable,
    CohortMonthPartitionScale,
    NewbieGPTable,
)
from dmp_suite.file_utils import from_same_directory
from dmp_suite.greenplum.table import \
    Int, String, Datetime, GPTable, ExternalGPLayout, ExternalGPLocation, MonthPartitionScale
from dmp_suite.table import OdsLayout
from dmp_suite.greenplum.task.transformations import replace_by_key
from dmp_suite.scales import WeekScale
from dmp_suite.task import cli
from dmp_suite.task.execution import run_task

from .impl import gp_table_to_dict, compare_expected_actual, recreate_and_fill


class TestDemandSession(GPTable):
    __layout__ = OdsLayout(source='query_test', name='demand_session', prefix_key='taxi')
    __partition_scale__ = MonthPartitionScale('utc_session_dttm', start='2020-05-01', end='2020-11-01')

    utc_session_dttm = Datetime()
    user_phone_pd_id = String()
    success_order_cnt = Int()
    break_reason = String()
    city = String()


def _format_actual_data(gp_table):
    actual_cohort_stat_data = gp_table_to_dict(gp_table)

    for row in actual_cohort_stat_data:
        row['msk_cohort_dt'] = dtu.format_date(row['msk_cohort_dt'])
        row['msk_life_period_dt'] = dtu.format_date(row['msk_life_period_dt'])
    return sorted(
        actual_cohort_stat_data,
        key=lambda row: (
            row['msk_cohort_dt'], row['msk_life_period_dt'], row['city'], row['app_platform'], row['session_city']
        )
    )


EVENT_CALC_USER_DEFINED_QUERY = """SELECT 
    utc_session_dttm,
    user_phone_pd_id,
    success_order_cnt,
    break_reason,
    city AS session_city
    FROM {event_table}"""


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'mono_attr_type_dict, dimensions, measure_dict',
    itertools.product(
        ({}, {'app_platform': String, 'city': String}),
        (({}, []), ({'session_city': String}, []), ({'session_city': String}, ['session_city'])),
        ({}, {'demand_session_cnt': Int})
    )
)
def test_correct_query_build(mono_attr_type_dict, dimensions, measure_dict):
    dimension_dict, total_dimension_list = dimensions
    try:
        TestNewbieTable = type(
            'TestNewbieTable',
            (NewbieGPTable,),
            {
                '__layout__': OdsLayout(source='query_test', name='newbie', prefix_key='taxi'),
                '__cohort_scale__': WeekScale,
                '__cohort_unit_key__': ['user_phone_pd_id'],
                '__cohort_mono_attrs__': [f for f in mono_attr_type_dict.keys()],

                'user_phone_pd_id': String(),
                **{k: v() for k, v in mono_attr_type_dict.items()},
            }
        )

        TestCohortStatTable = type(
            'TestCohortStatTable',
            (CohortGPTable,),
            {
                '__layout__': OdsLayout(source='query_test', name='cohort_stat', prefix_key='taxi'),
                '__partition_scale__': CohortMonthPartitionScale('2020-05-01'),
                '__newbie__': TestNewbieTable,

                **{k: v() for k, v in mono_attr_type_dict.items()},
                **{k: v() for k, v in dimension_dict.items()},
                **{k: v() for k, v in measure_dict.items()},
                '__dimensions__': dimension_dict.keys(),
                '__dimensions_w_total__': total_dimension_list,
                '__measures__': measure_dict.keys(),
            }
        )

        with open(from_same_directory(__file__, 'data/demand_session.json')) as f:
            demand_session_data = json.load(f)
        recreate_and_fill(TestDemandSession, demand_session_data)

        with open(from_same_directory(__file__, 'data/newbie_data.json')) as f:
            current_newbie_data = json.load(f)
        recreate_and_fill(TestNewbieTable, current_newbie_data)

        with gp.connection.transaction():
            gp.connection.drop_table(TestCohortStatTable)

        event_query = EventSelectQuery(
            query=EVENT_CALC_USER_DEFINED_QUERY,
            event_dttm_field='utc_session_dttm',
        ).add_sources(
            event_table=TestDemandSession,
        )

        source = CohortSqlTaskSource(
            cohort_table=TestCohortStatTable,
            event_query=event_query,
            measure_calc_dict={
                "demand_session_cnt": "SUM(GREATEST(1, success_order_cnt))"
            } if measure_dict else {},
            fields_for_measure=('success_order_cnt',) if measure_dict else ()
        )

        task = replace_by_key(
            name='test_cohort_stat_increment',
            source=source,
            target=TestCohortStatTable
        ).arguments(
            period=cli.Period(dtu.Period('2020-07-15', '2020-07-30'))
        )
        run_task(task)
    finally:
        with gp.connection.transaction():
            for table in (TestDemandSession, TestNewbieTable, TestCohortStatTable):
                gp.connection.drop_table(table)


@pytest.mark.slow('gp')
def test_correct_calc_cohort():
    class TestNewbieTable(NewbieGPTable):
        __layout__ = OdsLayout(source='query_test', name='newbie', prefix_key='taxi')

        user_phone_pd_id = String()
        app_platform = String()
        city = String()

        __cohort_scale__ = WeekScale
        __cohort_unit_key__ = [user_phone_pd_id]
        __cohort_mono_attrs__ = [app_platform, city]


    class TestCohortStatTable(CohortGPTable):
        __partition_scale__ = CohortMonthPartitionScale('2020-05-01')
        __layout__ = OdsLayout(source='query_test', name='cohort_stat', prefix_key='taxi')

        app_platform = String()
        city = String()

        session_city = String()
        demand_session_cnt = Int()
        demand_session_wo_geo_break_cnt = Int()

        __newbie__ = TestNewbieTable
        __dimensions__ = [session_city]
        __measures__ = [demand_session_cnt, demand_session_wo_geo_break_cnt]


    with open(from_same_directory(__file__, 'data/demand_session.json')) as f:
        demand_session_data = json.load(f)
    recreate_and_fill(TestDemandSession, demand_session_data)

    with open(from_same_directory(__file__, 'data/newbie_data.json')) as f:
        current_newbie_data = json.load(f)
    recreate_and_fill(TestNewbieTable, current_newbie_data)

    with gp.connection.transaction():
        gp.connection.drop_table(TestCohortStatTable)

    event_query = EventSelectQuery(
        query=EVENT_CALC_USER_DEFINED_QUERY,
        event_dttm_field='utc_session_dttm',
    ).add_sources(
        event_table=EventSourceTable(
            TestDemandSession,
            columns=[
                TestDemandSession.utc_session_dttm,
                TestDemandSession.user_phone_pd_id,
                TestDemandSession.success_order_cnt,
                TestDemandSession.break_reason,
                TestDemandSession.city,
            ],
        )
    )

    source = CohortSqlTaskSource(
        cohort_table=TestCohortStatTable,
        event_query=event_query,
        measure_calc_dict={
            "demand_session_cnt": "SUM(GREATEST(1, success_order_cnt))",
            "demand_session_wo_geo_break_cnt": "SUM(GREATEST(1, success_order_cnt)) FILTER (WHERE break_reason != 'geo')"
        },
        fields_for_measure=('success_order_cnt', 'break_reason')
    )

    task = replace_by_key(
        name='test_cohort_stat_increment',
        source=source,
        target=TestCohortStatTable
    ).arguments(
        period=cli.Period(dtu.Period('2020-07-15', '2020-07-30'))
    )
    run_task(task)

    with open(from_same_directory(__file__, 'data/expected_cohort_stat_data.json')) as f:
        expected_cohort_stat_data = json.load(f)

    actual_cohort_stat_data = _format_actual_data(TestCohortStatTable)

    compare_expected_actual(expected_cohort_stat_data, actual_cohort_stat_data)

    with gp.connection.transaction():
        for table in (TestDemandSession, TestNewbieTable, TestCohortStatTable):
            gp.connection.drop_table(table)
