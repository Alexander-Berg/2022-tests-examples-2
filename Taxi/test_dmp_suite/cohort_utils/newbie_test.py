import json
import pytest
import itertools

from connection import greenplum as gp
from dmp_suite import datetime_utils as dtu
from dmp_suite.file_utils import from_same_directory
from dmp_suite.greenplum.table import \
    Boolean, Int, String, Date, Datetime, GPTable, MonthPartitionScale
from dmp_suite.greenplum.task.transformations import snapshot
from dmp_suite.scales import WeekScale
from dmp_suite.cohort_utils import (
    NewbieGPTable,
    EventSelectQuery,
    EventSourceTable,
    NewbieSqlTaskSource,
    GeoRoot,
    GeoNodeType,
)
from dmp_suite.task.cli import StartEndDate
from dmp_suite.task.execution import run_task
from test_dmp_suite.greenplum import utils
from .impl import gp_table_to_dict, recreate_and_fill


class DMOrder(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='dm_order'))
    __partition_scale__ = MonthPartitionScale('utc_order_dt', start='2020-06-01', end='2020-08-01')

    utc_order_dt = Date()
    utc_order_dttm = Datetime()
    user_phone_pd_id = String()
    brand = String()
    order_tariff = String()
    app_platform = String()
    country = String()
    city = String()
    tariff_zone = String()
    success_order_flg = Boolean()


class VDimFullGeoHierarchy(GPTable):
    __layout__ = utils.TestLayout(utils.random_name(prefix='v_dim_full_geo_hierarchy'))

    tariff_zone = String()
    node_id = String()
    root_node_id = String()
    node_type = String()
    node_depth = Int()


def format_data(gp_table):
    actual_newbie_data = gp_table_to_dict(gp_table)
    for row in actual_newbie_data:
        row['msk_cohort_dt'] = dtu.format_date(row['msk_cohort_dt'])
        row['msk_first_event_dttm'] = dtu.format_datetime(row['msk_first_event_dttm'])
    return sorted(
        actual_newbie_data,
        key=lambda row: (row['user_phone_pd_id'], row['brand'], row['country'], row['city'], row['node_id'])
    )


USER_DEFINED_QUERY = """SELECT
    utc_order_dttm,
    user_phone_pd_id,
    brand,
    order_tariff AS tariff,
    app_platform,
    country,
    city,
    tariff_zone
FROM {event_table}
WHERE success_order_flg"""


def generate_test_case():
    case_grid = itertools.product(
        (
            ({'node_id': String}, {}, ()),
            ({'node_id': String}, {'tariff': String}, ()),
            ({}, {'node_id': String}, ()),
            ({}, {'tariff': String, 'node_id': String}, ('tariff',)),
            ({'tariff': String}, {'node_id': String}, ()),
        ),
        (
            ([GeoRoot.basic], 'tariff_zone'),
            ([GeoRoot.basic, GeoRoot.finance], 'tariff_zone')
        )
    )
    for (mono_attr_type_dict, poly_attr_type_dict, poly_attr_w_total_list), \
        (geo_hierarchy_roots, tariff_zone_field) in case_grid:
        yield mono_attr_type_dict, poly_attr_type_dict, poly_attr_w_total_list, \
              geo_hierarchy_roots, tariff_zone_field


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'mono_attr_type_dict, poly_attr_type_dict, poly_attr_w_total_list, geo_hierarchy_roots, tariff_zone_field',
    generate_test_case(),
)
def test_correct_query_build(
    mono_attr_type_dict, poly_attr_type_dict, poly_attr_w_total_list,
    geo_hierarchy_roots, tariff_zone_field
):
    TestCohortNewbieTable = type(
        'TestCohortNewbieTable',
        (NewbieGPTable,),
        {
            '__layout__': utils.TestLayout(name=utils.random_name(prefix='newbie')),
            '__cohort_scale__': WeekScale,
            '__cohort_unit_key__': ['user_phone_pd_id'],
            '__cohort_mono_attrs__': [f for f in mono_attr_type_dict.keys()],
            '__cohort_poly_attrs__': [f for f in poly_attr_type_dict.keys()],
            '__cohort_poly_attrs_w_total__': poly_attr_w_total_list,

            'user_phone_pd_id': String(),
            **{k: v() for k, v in mono_attr_type_dict.items()},
            **{k: v() for k, v in poly_attr_type_dict.items()},
        }
    )

    with gp.connection.transaction():
        gp.connection.drop_table(TestCohortNewbieTable)
        gp.connection.create_table(TestCohortNewbieTable)

    with open(from_same_directory(__file__, 'data/dm_order_data.json')) as f:
        dm_order_data = json.load(f)
    recreate_and_fill(DMOrder, dm_order_data)

    with open(from_same_directory(__file__, 'data/v_dim_full_geo_hierarchy.json')) as f:
        v_dim_full_geo_hierarchy = json.load(f)
    recreate_and_fill(VDimFullGeoHierarchy, v_dim_full_geo_hierarchy)

    source = NewbieSqlTaskSource(
        newbie_table=TestCohortNewbieTable,
        event_query=EventSelectQuery(
            USER_DEFINED_QUERY,
            event_dttm_field='utc_order_dttm',
            tariff_zone_field=tariff_zone_field,
        ).add_sources(
            event_table=EventSourceTable(
                DMOrder,
                columns=[
                    DMOrder.utc_order_dt,
                    DMOrder.utc_order_dttm,
                    DMOrder.user_phone_pd_id,
                    DMOrder.brand,
                    DMOrder.order_tariff,
                    DMOrder.app_platform,
                    DMOrder.country,
                    DMOrder.city,
                    DMOrder.tariff_zone,
                    DMOrder.success_order_flg,
                ]
            )
        )
    ).with_geo(
        geo_table=VDimFullGeoHierarchy,
        geo_root_list=geo_hierarchy_roots,
    )

    task = snapshot(
        name='test_newbie_increment',
        source=source,
        target=TestCohortNewbieTable
    ).arguments(
        period=StartEndDate(None, datetime_type='datetime')
    )
    run_task(task, ['--start_date', '2020-06-01', '--end_date', '2020-07-30'])


# Разные значения параметров геоиерархий не влияют в данном случае на результат.
@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'geo_node_type_list, geo_node_id_list, geo_node_depth',
    itertools.product(
        (None, [GeoNodeType.agglomeration]),
        (None, ['br_moscow', 'br_torzgok', 'br_tver', 'br_pskov', 'br_dubna', 'br_kaluga', 'br_tbilisi']),
        (None, 3)
    )
)
def test_correct_calc_newbie(geo_node_type_list, geo_node_id_list, geo_node_depth):
    class TestCohortNewbieTable(NewbieGPTable):
        __layout__ = utils.TestLayout(name=utils.random_name(prefix='newbie'))

        user_phone_pd_id = String()
        brand = String()
        tariff = String()
        app_platform = String()
        country = String()
        city = String()
        node_id = String()

        __cohort_scale__ = WeekScale
        __cohort_unit_key__ = [user_phone_pd_id, brand]
        __cohort_mono_attrs__ = [tariff, app_platform]
        __cohort_poly_attrs__ = [country, city, node_id]
        __cohort_poly_attrs_w_total__ = [country]

    with open(from_same_directory(__file__, 'data/dm_order_data.json')) as f:
        dm_order_data = json.load(f)
    recreate_and_fill(DMOrder, dm_order_data)

    with open(from_same_directory(__file__, 'data/current_newbie_data.json')) as f:
        current_newbie_data = json.load(f)
    recreate_and_fill(TestCohortNewbieTable, current_newbie_data)

    with open(from_same_directory(__file__, 'data/v_dim_full_geo_hierarchy.json')) as f:
        v_dim_full_geo_hierarchy = json.load(f)
    recreate_and_fill(VDimFullGeoHierarchy, v_dim_full_geo_hierarchy)

    source = NewbieSqlTaskSource(
        newbie_table=TestCohortNewbieTable,
        event_query=EventSelectQuery(
            USER_DEFINED_QUERY,
            event_dttm_field='utc_order_dttm',
            tariff_zone_field='tariff_zone',
        ).add_sources(
            event_table=EventSourceTable(
                DMOrder,
                columns=[
                    DMOrder.utc_order_dt,
                    DMOrder.utc_order_dttm,
                    DMOrder.user_phone_pd_id,
                    DMOrder.brand,
                    DMOrder.order_tariff,
                    DMOrder.app_platform,
                    DMOrder.country,
                    DMOrder.city,
                    DMOrder.tariff_zone,
                    DMOrder.success_order_flg,
                ]
            )
        )
    ).with_geo(
        geo_table=VDimFullGeoHierarchy,
        geo_root_list=[GeoRoot.basic, GeoRoot.finance],
        geo_node_type_list=geo_node_type_list,
        geo_node_id_list=geo_node_id_list,
        geo_node_depth=geo_node_depth
    )

    task = snapshot(
        name='test_newbie_increment',
        source=source,
        target=TestCohortNewbieTable
    ).arguments(
        period=StartEndDate(None)
    )
    run_task(task, ['--start_date', '2020-07-01', '--end_date', '2020-07-08'])

    with open(from_same_directory(__file__, 'data/expected_newbie_data.json')) as f:
        expected_newbie_data = json.load(f)

    actual_newbie_data = format_data(
        TestCohortNewbieTable
    )

    expected_data = sorted(expected_newbie_data, key=lambda d: sorted(d.items()))
    actual_data = sorted(actual_newbie_data, key=lambda d: sorted(d.items()))

    assert actual_data == expected_data
