import pytest

from connection import greenplum as gp
from dmp_suite.dq_metrics.query_helper import (
    add_placeholders_to_query_string,
    build_union_all_query,
    build_names_list_query,
    build_names_var_list_query,
    build_metric_value_clause_list_query,
)
from dmp_suite.dq_metrics.query_builder import _Metric
from .query_data import (
    metric_kwargs_min,
    metric_kwargs_inc,
    metric_kwargs_inc_2,
)


@pytest.mark.parametrize(
    "table_names_list, additional_queries, expected",
    [
        ([], [], ""),
        (["table1", ], [], "{table1}"),
        (["table1", "table2", "table3"], [], "{table1}\n{table2}\n{table3}"),
        ([], ["select 1;"], "select 1;"),
        ([], ["select 1;", "select 2;", "select 3;"], "select 1;\nselect 2;\nselect 3;"),
        (
            ["table1", "table2", "table3"],
            ["select 1;", "select 2;", "select 3;"],
            "{table1}\n{table2}\n{table3}\nselect 1;\nselect 2;\nselect 3;",
        ),
    ]
)
def test_add_placeholders_to_query_string(table_names_list, additional_queries, expected):

    assert add_placeholders_to_query_string(table_names_list, *additional_queries).strip() == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "table_names_list, expected",
    [
        ([], ""),
        (
            ["table1"],
            """
            CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS (
                SELECT * FROM "table1"
                )
            DISTRIBUTED RANDOMLY;
            ANALYZE result_table;
            """
         ),
        (
                ["table1", "table2", "table3"],
                """
                CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS (
                    SELECT * FROM "table1"
                    UNION ALL
                    SELECT * FROM "table2"
                    UNION ALL
                    SELECT * FROM "table3"
                    )
                DISTRIBUTED RANDOMLY;
                ANALYZE result_table;
                """
        ),
    ],
)
def test_build_union_all_query(table_names_list, expected):

    with gp.connection.cursor() as cur:
        actual = build_union_all_query(table_names_list).as_string(cur)

    actual = actual.replace(" ", "").replace("\n", "")
    expected = expected.replace(" ", "").replace("\n", "")

    assert actual == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "names_list, add_new_line, expected",
    [
        ([], False, ""),
        (["metric1"], False, "metric1"),
        (["metric1", "metric2", "metric3"], False, "metric1, metric2, metric3"),
        (["metric1", "metric2", "metric3"], True, "metric1\n, metric2\n, metric3"),
    ],
)
def test_build_names_list_query(names_list, add_new_line, expected):

    with gp.connection.cursor() as cur:
        actual = build_names_list_query(names_list, add_new_line).as_string(cur).strip()

    assert actual == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "names_list, add_new_line, expected",
    [
        ([], False, ""),
        (["metric1"], False, "'metric1'"),
        (["metric1", "metric2", "metric3"], False, "'metric1', 'metric2', 'metric3'"),
        (["metric1", "metric2", "metric3"], True, "'metric1'\n, 'metric2'\n, 'metric3'"),
    ],
)
def test_build_names_var_list_query(names_list, add_new_line, expected):

    with gp.connection.cursor() as cur:
        actual = build_names_var_list_query(names_list, add_new_line).as_string(cur).strip()

    assert actual == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "metrics_kwargs_list, expected",
    [
        ([], ""),
        ([metric_kwargs_min], "SUM ( \"some_attribute_1\") AS metric_some_attribute_1"),
        (
            [metric_kwargs_min, metric_kwargs_inc, metric_kwargs_inc_2],
            """
            SUM("some_attribute_1") AS metric_some_attribute_1
            , COUNT("some_attribute_1") AS metric_some_attribute_1
            , SUM(CASE WHEN "some_attribute_1" IS NULL THEN 1 ELSE 0 END) AS some_metric_name
            """,
        ),
    ],
)
def test_build_metric_value_clause_list_query(metrics_kwargs_list, expected):

    metrics_list = [_Metric(**metric_kwargs) for metric_kwargs in metrics_kwargs_list]
    with gp.connection.cursor() as cur:
        actual = build_metric_value_clause_list_query(metrics_list).as_string(cur).strip()

    actual = actual.replace(" ", "").replace("\n", "")
    expected = expected.replace(" ", "").replace("\n", "")

    assert actual == expected
