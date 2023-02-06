import datetime

import mock
import pytest

import dmp_suite.greenplum.utils
from connection.greenplum import get_connection
from dmp_suite import greenplum as gp
from dmp_suite.greenplum import table as gp_table
from dmp_suite.greenplum.maintenance.profiler import analyzer, statements_parser
from dmp_suite.greenplum.task import transformations
from dmp_suite.task import cli
from dmp_suite.task.args import use_period_arg
from test_dmp_suite.greenplum.maintenance.profiler import plan_fixture


class TestTable(gp.GPEtlTable):
    __layout__ = gp_table.ExternalGPLayout('test_schema', 'test_entity')


SQL = """
DROP TABLE IF EXISTS test_analyze_task;
DROP TABLE IF EXISTS test_analyze_task_2;
CREATE TEMPORARY TABLE test_analyze_task as VALUES (1, %(start)s, %(end)s)
DISTRIBUTED RANDOMLY ;
create temporary table test_analyze_task_2 AS values (1, 2, 3);
"""

EXPECTED_SQL = """
DROP TABLE IF EXISTS test_analyze_task;
DROP TABLE IF EXISTS test_analyze_task_2;
CREATE TEMPORARY TABLE test_analyze_task as VALUES (1, '2021-11-14T00:00:00'::timestamp, '2021-11-23T23:59:59.999999'::timestamp)
DISTRIBUTED RANDOMLY ;
create temporary table test_analyze_task_2 AS values (1, 2, 3);
"""


def get_task(query=SQL):
    return transformations.snapshot(
        name='test_analyze_task_source',
        source=transformations.SqlTaskSource.from_string(
            query
        ).add_params(
            start=use_period_arg().start,
            end=use_period_arg().end
        ),
        target=TestTable,
    ).arguments(
        period=cli.StartEndDate.prev_n_days(days=10)
    )


@pytest.mark.slow('gp')
@mock.patch(
    'dmp_suite.datetime_utils.utcnow',
    mock.MagicMock(return_value=datetime.datetime(2021, 11, 24, 0, 1)),
)
def test_query_builder():
    query = analyzer.get_executable_query_string(get_task())
    assert query == EXPECTED_SQL


@pytest.mark.slow('gp')
def test_split_and_strip_query():
    query = analyzer.get_executable_query_string(get_task())
    statements = tuple(dmp_suite.greenplum.utils.split_and_strip_query(query))
    assert len(statements) == 4
    assert str(statements[0].token_first(skip_cm=True)) == 'DROP'
    assert str(statements[1].token_first(skip_cm=True)) == 'DROP'
    assert str(statements[2].token_first(skip_cm=True)) == 'CREATE'
    assert str(statements[3].token_first(skip_cm=True)) == 'create'

    assert statements[2].get_type() == 'CREATE'
    assert statements[3].get_type() == 'CREATE'


@pytest.mark.slow('gp')
def test_analyze_task_source_raw():
    result = analyzer.analyze_task_source(get_task(), get_connection(), True)
    assert len(result) == 4

    assert all(map(lambda x: not x.raw_result, result[:2]))
    assert all(map(lambda x: x.raw_result, result[2:]))

    assert result[2].raw_result.startswith('Result')
    assert result[3].raw_result.startswith('Result')


@pytest.mark.slow('gp')
def test_analyze_task_source_json():
    result = analyzer.analyze_task_source(get_task(), get_connection(), False)
    assert len(result) == 4

    assert all(map(lambda x: not x.raw_result, result[:2]))
    assert all(map(lambda x: x.raw_result, result[2:]))

    assert isinstance(result[2].raw_result, dict)
    assert isinstance(result[3].raw_result, dict)


@pytest.mark.parametrize(
    "query, expected",
    [
        ("create temporary table test_analyze_task_2 AS values (1, 2, 3);", True),
        ("CREATE TABLE array_int (vector  int[][]);", False),
        ("CREATE TYPE compfoo AS (f1 int, f2 text);", False),
        ("DROP TABLE IF EXISTS test_analyze_task;", False),
        ("SELECT 1;", False),
        ("UPDATE films SET kind = 'Dramatic' WHERE kind = 'Drama';", True),
        ("INSERT INTO films VALUES ('UA502', 105, '1971-07-13');", True),
        ("WITH tab AS (bla bla) INSERT INTO foo (bla) SELECT * FROM tab;", True),  # CTE
    ]
)
def test_is_analyze_compatible(query, expected):
    statement = tuple(dmp_suite.greenplum.utils.split_and_strip_query(query))[0]
    assert analyzer._is_analyze_compatible(statement) == expected


@pytest.mark.slow
def test_analyze_task_source_metrics():
    query = """
    DROP TABLE IF EXISTS test_analyze_task;
    CREATE TEMPORARY TABLE test_analyze_task as VALUES (1, %(start)s, %(end)s)
    DISTRIBUTED RANDOMLY ;
    """
    result = analyzer.analyze_task_source(get_task(query), get_connection(), False)

    assert not result[0].metrics
    assert result[1].metrics
    assert result[1].metrics.operation_count == 5
    assert result[1].metrics.slice_count == 2
    assert result[1].metrics.execution_time > 1.0
    assert result[1].metrics.actual_rows
    assert result[1].metrics.actual_rows.max >= result[1].metrics.actual_rows.min
    assert result[1].metrics.memory_used
    assert result[1].metrics.memory_used.max >= result[1].metrics.memory_used.min
    assert result[1].metrics.spill_size is None


@pytest.mark.parametrize(
    "query, expected",
    [
        ("create temporary table test_analyze_task_2 AS values (1, 2, 3);", 'TEMPORARY TABLE test_analyze_task_2 ...'),
        ("CREATE TABLE array_int (vector  int[][]);", 'TABLE array_int ...'),
        ("CREATE TABLE array_int (vector  int[][]) DISTRIBUTED RANDOMLY;", 'TABLE array_int ... DISTRIBUTED RANDOMLY'),
        ("CREATE TABLE array_int (vector  int[][]) DISTRIBUTED BY (ticket_from);",
         'TABLE array_int ... DISTRIBUTED BY (ticket_from)'),
        ("CREATE TYPE compfoo AS (f1 int, f2 text);", 'TYPE compfoo ...'),
        ("DROP TABLE IF EXISTS test_analyze_task;", ''),
        ("SELECT 1;", ''),
        ("UPDATE films SET kind = 'Dramatic' WHERE kind = 'Drama';", 'films ...'),
        ("INSERT INTO films VALUES ('UA502', 105, '1971-07-13');", 'INTO films ...'),
    ]
)
def test_get_statement_extras(query, expected):
    statement = tuple(dmp_suite.greenplum.utils.split_and_strip_query(query))[0]
    assert statements_parser.get_statement_extras(statement) == expected


def test_build_metrics():

    metrics = analyzer._build_metrics(plan_fixture.PLAN_RESULT_DICT)

    assert metrics
    assert metrics.operation_count == 10
    assert metrics.slice_count == 3
    assert metrics.execution_time == 6573.675
    assert metrics.actual_rows.total == 1016
    assert metrics.actual_rows.min == 1016
    assert metrics.actual_rows.max == 29898112
    assert metrics.memory_used.min == 21821312
    assert metrics.memory_used.max == 3086083200
    assert metrics.spill_size.min == 2691456
    assert metrics.spill_size.max == 2691456
