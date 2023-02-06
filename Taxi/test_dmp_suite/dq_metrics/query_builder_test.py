import pytest
from psycopg2 import sql

from connection import greenplum as gp
from dmp_suite.task.args import use_arg
from dmp_suite.exceptions import ConfigError
from dmp_suite.dq_metrics.query_builder import _Metric, _PluralMetric, QueryBuilder
from .query_data import (
    SomeTable,
    RepDqMetricsLog,
    metric_kwargs_min,
    metric_kwargs_old,
    metric_kwargs_inc,
    metric_kwargs_snp,
    metric_kwargs_inc_2,
    metric_kwargs_twice_old,
    metric_kwargs_twice_inc,
    metric_kwargs_twice_snp,
    plural_metric_kwargs_ok,
    plural_metric_kwargs_not_ok,
)


@pytest.mark.slow
@pytest.mark.parametrize(
    "metric_kwargs",
    [
        metric_kwargs_min,
        metric_kwargs_old,
        metric_kwargs_inc,
        metric_kwargs_snp,
        metric_kwargs_inc_2,
        metric_kwargs_twice_old,
        metric_kwargs_twice_inc,
        metric_kwargs_twice_snp,
    ]
)
def test__metric(metric_kwargs):
    """
    ввиду искаверканной логики определения путей расположения таблицы (спасибо, неотключаемая рандомизация),
    можем проверить только то, что запрос принципиально создается, некоторые его куски соответствуют ожиданиям
    """

    metric = _Metric(**metric_kwargs)
    metric.build_query(metric_kwargs.get("source_table"), metric_kwargs.get("dttm_column"))

    with gp.connection.cursor() as cur:
        full_query_string = metric.query.as_string(cur)

    assert type(metric.query) is sql.Composed
    assert all([query_part in full_query_string for query_part in metric_kwargs.get("expected_sql")])


@pytest.mark.slow
@pytest.mark.parametrize(
    "plural_metric_kwargs, raise_exception",
    [
        (plural_metric_kwargs_ok, False),
        (plural_metric_kwargs_not_ok, True),
    ]
)
def test__plural_metric(plural_metric_kwargs, raise_exception):
    """
    ввиду искаверканной логики определения путей расположения таблицы (спасибо, неотключаемая рандомизация),
    можем проверить только то, что запрос принципиально создается, некоторые его куски соответствуют ожиданиям
    """

    if raise_exception:
        with pytest.raises(ConfigError):
            _PluralMetric(
                source_metrics=plural_metric_kwargs.get("source_metrics"),
                mandatory_similarity_attributes=plural_metric_kwargs.get("mandatory_similarity_attributes"),
            )
        return

    plural_metric = _PluralMetric(
        source_metrics=plural_metric_kwargs.get("source_metrics"),
        mandatory_similarity_attributes=plural_metric_kwargs.get("mandatory_similarity_attributes"),
    )
    plural_metric.build_query(
        plural_metric_kwargs.get("source_table"),
        plural_metric_kwargs.get("dttm_column"),
    )

    with gp.connection.cursor() as cur:
        full_query_string = plural_metric.query.as_string(cur)

    assert type(plural_metric.query) is sql.Composed
    assert all([query_part in full_query_string for query_part in plural_metric_kwargs.get("expected_sql")])


@pytest.mark.slow
def test_query_builder():
    """
    ввиду искаверканной логики определения путей расположения таблицы (спасибо, неотключаемая рандомизация),
    можем проверить только то, что запрос принципиально создается, некоторые его куски соответствуют ожиданиям
    """

    t = QueryBuilder(
        source_table=SomeTable,
        target_table=RepDqMetricsLog,
    )
    metrics = [
        t.count(SomeTable.some_attribute_1),
        t.count_not_null(SomeTable.some_attribute_1),
        t.count_null(SomeTable.some_attribute_1),
        t.count_distinct(SomeTable.some_attribute_1),
        t.avg(SomeTable.some_attribute_1),
        t.max(SomeTable.some_attribute_1),
        t.min(SomeTable.some_attribute_1),
        t.sum(SomeTable.some_attribute_1),
        t.custom_metric_value(
            metric_name="avg_speed_kmh",
            metric_value_clause="((SUM(some_attribute_1) * 60 * 60) / SUM(some_attribute_2))::INTEGER",
            additional_where_clause="some_datetime_2 NOTNULL AND some_attribute_4 IS NULL",
        ),
        t.custom_twice_aggregate(
            metric_name="max_duration_sec",
            metric_value_clause="MAX(some_attribute_1)",
            inner_select_clause="some_datetime_2::DATE AS utc_dt, SUM(some_attribute_1) AS metric_value",
            inner_group_by_clause="some_attribute_1, some_datetime_2::DATE",
        ),
    ]

    source = t.sql_task_source \
        .split_query(split_sql=False) \
        .add_params(
            start_date=use_arg("start_date"),
            end_date=use_arg("end_date"),
        ).get_value(
            dict(start_date="2022-01-01", end_date="2022-01-01"), None)
    full_query_string = source.executable_query_string
    expected = [
        b"CREATE TEMPORARY TABLE \"avg_speed_kmh\"",
        b"CREATE TEMPORARY TABLE \"max_duration_sec\"",
        b"CREATE TEMPORARY TABLE \"plural_avg_some_attribute_1\"",
        b"CREATE TEMPORARY TABLE result_table",
    ]

    assert all([query_part in full_query_string for query_part in expected])
