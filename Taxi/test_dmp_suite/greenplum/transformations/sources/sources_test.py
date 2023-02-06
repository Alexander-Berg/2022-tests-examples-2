from functools import partial

import pytest
from mock import mock
from psycopg2.sql import SQL, Literal

from connection import greenplum as gp
from dmp_suite.greenplum import Int
from dmp_suite.greenplum.connection import EtlConnection
from dmp_suite.greenplum.transformations import Transformation
from dmp_suite.greenplum.transformations.sources import (
    SqlSource,
    ExternalSource,
)
from test_dmp_suite.greenplum.utils import GreenplumTestTable, external_gp_layout


class DummyTable(GreenplumTestTable):
    __layout__ = external_gp_layout()
    a = Int()


class MockTransformation(Transformation):
    def __init__(self, source, expected_data, connection=None):
        super().__init__(source, DummyTable, connection=connection)
        self.expected_data = expected_data

    def run(self):
        self.source.prepare(self)
        with self.connection.transaction():
            with self.source.source_table(self) as src:
                sql = 'select * from {table}'.format(table=src)
                actual = [dict(row) for row in gp.connection.query(sql)]
                sort = partial(sorted, key=lambda d: d['a'])
                assert sort(actual) == sort(self.expected_data)


@pytest.mark.slow('gp')
def test_sql_source():
    source = (
        SqlSource.from_string(
            'create temporary table result_table on commit drop as {select}'
        )
        .add_sql(select=SQL("select 1 as a"))
    )
    transformation = MockTransformation(source, [dict(a=1)])
    transformation.run()


@pytest.mark.slow('gp')
def test_sql_source_split_sql():
    connection = mock.Mock(spec=EtlConnection, wraps=gp.get_connection())
    source = (
        SqlSource.from_string(
            """
            create temporary table result_table on commit drop as {select};
            create temporary table one_more_result_table on commit drop as {select};
            """
        ).add_sql(
            select=SQL("select 1 as a")
        ).split_query()
    )
    transformation = MockTransformation(source, [dict(a=1)], connection=connection)
    transformation.run()

    expected = [
        ('transaction', (), {}),
        ('transaction', (), {}),
        ('execute', ('create temporary table result_table on commit drop as select 1 as a;',), {}),
        ('execute', ('create temporary table one_more_result_table on commit drop as select 1 as a;',), {}),
    ]

    result = [(name, args, kwargs) for name, args, kwargs in connection.mock_calls]

    assert result == expected


@pytest.mark.slow('gp')
def test_sql_source_pre_sql():
    source = (
        SqlSource.from_string(
            'create temporary table result_table on commit drop as\n'
            '{select}\n'
            'union all\n'
            'select * from temp_table'
        )
        .add_sql(select=SQL("select 1 as a"))
        .add_pre_sql_statement(
            'create temporary table temp_table on commit drop as select 2 as a'
        )
    )
    transformation = MockTransformation(source, [dict(a=1), dict(a=2)])
    transformation.run()


@pytest.mark.slow('gp')
def test_sql_source_multi_pre_sql():
    source = (
        SqlSource.from_string(
            'create temporary table result_table on commit drop as\n'
            '{select}\n'
            'union all\n'
            'select * from temp_table_1\n'
            'union all\n'
            'select * from temp_table_2'
        )
        .add_sql(select=SQL("select 1 as a"))
        .add_pre_sql_statement(
            'create temporary table temp_table_1 on commit drop as '
            'select 2 as a'
        )
        .add_pre_sql_statement(
            'create temporary table temp_table_2 on commit drop as '
            'select 3 as a'
        )
    )
    transformation = MockTransformation(
        source,
        [dict(a=1), dict(a=2), dict(a=3)],
    )
    transformation.run()


@pytest.mark.slow('gp')
@pytest.mark.parametrize('sql', [
    'create temporary table temp_table on commit drop as select 1 as a;',
    SQL('create temporary table temp_table on commit drop as select 1 as a;'),
    SQL(
        'create temporary table temp_table on commit drop as select {val} as a;'
    ).format(
        val=Literal(1),
    ),
])
def test_sql_source_different_type_pre_sql(sql):
    query = (
        'create temporary table result_table on commit drop as\n'
        'select * from temp_table\n'
    )
    source = SqlSource.from_string(query).add_pre_sql_statement(sql)
    transformation = MockTransformation(source, [dict(a=1)])
    transformation.run()

    expected_executable_sql = gp.connection.build_executable_string(
        (SQL(sql) if isinstance(sql, str) else sql) + SQL('\n') + SQL(query)
    )
    assert expected_executable_sql == source.executable_query_string


@pytest.mark.slow('gp')
def test_external_source():
    source = ExternalSource([dict(a=1), dict(a=10)])
    transformation = MockTransformation(source, [dict(a=1), dict(a=10)])
    transformation.run()

    extractors = dict(a=lambda d: d['b'])
    source = ExternalSource([dict(b=1), dict(b=10)], extractors=extractors)
    transformation = MockTransformation(source, [dict(a=1), dict(a=10)])
    transformation.run()
