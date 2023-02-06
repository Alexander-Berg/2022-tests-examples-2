from dmp_suite.table import CdmLayout, RepLayout
from dmp_suite.greenplum import GPTable, Int, String, Datetime, MonthPartitionScale

from dmp_suite.dq_metrics.table import BaseDqMetricsLog
from dmp_suite.dq_metrics.query_helper import SqlFunction
from dmp_suite.dq_metrics.query_templates import (
    COMMON_TMP_TABLE_TEMPLATE__OLD,
    COMMON_TMP_TABLE_TEMPLATE__INC_LOG,
    COMMON_TMP_TABLE_TEMPLATE__SNP_LOG,
    TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__OLD,
    TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__INC_LOG,
    TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__SNP_LOG,
)
from dmp_suite.dq_metrics.query_builder import _Metric


class SomeTable(GPTable):
    __layout__ = CdmLayout(name="some_table", group="supply", prefix_key="taxi")
    __partition_scale__ = MonthPartitionScale("some_datetime_1")

    some_attribute_1 = Int()
    some_attribute_2 = Int()
    some_attribute_3 = Int()
    some_attribute_4 = Int()
    some_datetime_1 = Datetime()
    some_datetime_2 = Datetime()


class OtherTable(GPTable):
    __layout__ = CdmLayout(name="some_table", group="supply", prefix_key="taxi")
    some_attribute_1 = Int()
    some_attribute_2 = Int()
    some_attribute_3 = String()
    some_attribute_4 = String()
    some_attribute_5 = String()
    some_attribute_6 = String()


class RepDqMetricsLog(BaseDqMetricsLog):
    __layout__ = RepLayout(name="dq_metrics_log", group="supply", prefix_key="taxi")
    __partition_scale__ = MonthPartitionScale(
        partition_key="utc_dt",
        start="2016-01-01",
    )


# _Metric testing
metric_kwargs_none = {
    "source_table": None,
    "dttm_column": None,
    "attribute": None,
    "additional_where_clause": None,
    "additional_group_by_clause": None,
    "metric_name": None,
    "query_template": None,
    "prefix": "sum",
    "metric_value_clause": None,
    "sql_function": None,
    "case_when_begin": None,
    "case_when_end": None,
    "inner_select_clause": None,
    "inner_group_by_clause": None,
    "inner_additional_where_clause": None,
}
metric_kwargs_min = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": COMMON_TMP_TABLE_TEMPLATE__INC_LOG,
    "sql_function": SqlFunction.SUM.value,
    "expected_sql": ["CREATE TEMPORARY TABLE \"metric_some_attribute_1\"", ],
}

metric_kwargs_old = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": COMMON_TMP_TABLE_TEMPLATE__OLD,
    "sql_function": SqlFunction.COUNT.value,
    "expected_sql": ["CREATE TEMPORARY TABLE \"metric_some_attribute_1\"", ],
}
metric_kwargs_inc = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": COMMON_TMP_TABLE_TEMPLATE__INC_LOG,
    "sql_function": SqlFunction.COUNT.value,
    "expected_sql": ["CREATE TEMPORARY TABLE \"metric_some_attribute_1\"", ],
}
metric_kwargs_snp = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": COMMON_TMP_TABLE_TEMPLATE__SNP_LOG,
    "sql_function": SqlFunction.COUNT.value,
    "expected_sql": ["CREATE TEMPORARY TABLE \"metric_some_attribute_1\"", ],
}
metric_kwargs_inc_2 = {
    "source_table": SomeTable,
    "dttm_column": "some_datetime_2",
    "attribute": SomeTable.some_attribute_1,
    "additional_where_clause": "some_attribute2 = some_attribute3",
    "additional_group_by_clause": "some_attribute4",
    "metric_name": "some_metric_name",
    "query_template": COMMON_TMP_TABLE_TEMPLATE__INC_LOG,
    "prefix": "sum",
    "sql_function": SqlFunction.SUM.value,
    "case_when_begin": "CASE WHEN",
    "case_when_end": "IS NULL THEN 1 ELSE 0 END",
    "expected_sql": ["CREATE TEMPORARY TABLE \"some_metric_name\"", ],
}
metric_kwargs_twice_old = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__OLD,
    "sql_function": SqlFunction.COUNT.value,
    "metric_name": "max_duration_sec",
    "metric_value_clause": "MAX(metric_value)",
    "inner_select_clause": "utc_valid_from_dttm::DATE AS utc_valid_from_dttm, SUM(duration_sec) AS metric_value",
    "inner_group_by_clause": "executor_profile_sk, utc_valid_from_dttm::DATE",
    "inner_additional_where_clause": "executor_profile_sk == 4",
    "expected_sql": ["CREATE TEMPORARY TABLE \"max_duration_sec\"", ],
}
metric_kwargs_twice_inc = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__INC_LOG,
    "metric_name": "avg_speed_fdwt_kmh",
    "metric_value_clause": "((SUM(distance_km) * 60 * 60) / SUM(duration_sec))::INTEGER",
    "additional_where_clause": "distance_km NOTNULL AND duration_sec NOTNULL "
                               "AND executor_status_code IN ('free', 'driving', 'waiting', 'transporting')",
    "expected_sql": ["CREATE TEMPORARY TABLE \"avg_speed_fdwt_kmh\"", ],
}
metric_kwargs_twice_snp = {
    "source_table": SomeTable,
    "attribute": SomeTable.some_attribute_1,
    "query_template": TWICE_AGGREGATE_TMP_TABLE_TEMPLATE__SNP_LOG,
    "metric_name": "avg_speed_fdwt_kmh",
    "expected_sql": ["CREATE TEMPORARY TABLE \"avg_speed_fdwt_kmh\"", ],
}


# _Plural_metric testing
mandatory_similarity_attributes = [
    "query_template",
    "additional_where_clause",
    "additional_group_by_clause",
    "inner_select_clause",
    "inner_group_by_clause",
    "inner_additional_where_clause",
]
generalizable_metrics = [_Metric(**metric_kwargs_min), _Metric(**metric_kwargs_inc)]
non_generalizable_metrics = [_Metric(**metric_kwargs_min), _Metric(**metric_kwargs_old)]
plural_metric_kwargs_ok = {
    "source_metrics": generalizable_metrics,
    "mandatory_similarity_attributes": mandatory_similarity_attributes,
    "source_table": SomeTable,
    "dttm_column": "some_datetime_2",
    "expected_sql": [
        "CREATE TEMPORARY TABLE \"plural_metric_some_attribute_1\"",
        "ANALYZE \"plural_metric_some_attribute_1\";",
    ],
}
plural_metric_kwargs_not_ok = {
    "source_metrics": non_generalizable_metrics,
    "mandatory_similarity_attributes": mandatory_similarity_attributes,
    "source_table": SomeTable,
    "dttm_column": "some_datetime_2",
}
