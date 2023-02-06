import dataclasses
import typing as tp

import pytest

from abt.services.compute import query_builder as qbm
from abt.utils import exceptions


@dataclasses.dataclass(frozen=True)
class Field:
    field: str
    agg: tp.Optional[str] = None
    alias: tp.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class WhereClause:
    field: str
    value: tp.Any
    op: qbm.WhereOps  # pylint: disable=invalid-name


@dataclasses.dataclass(frozen=True)
class Param:
    fields: tp.Optional[tp.List[Field]]
    from_: tp.Optional[str]
    where_clauses: tp.Optional[tp.List[WhereClause]]
    group_by_fields: tp.Optional[tp.List[str]]
    order_by_fields: tp.Optional[tp.List[str]]
    expecting_error: bool
    expected_query: tp.Optional[str]


@pytest.mark.parametrize(
    'param',
    [
        pytest.param(
            Param(
                fields=[
                    Field(field='test_field'),
                    Field(
                        field='test_field_two', agg='sum', alias='test_alias',
                    ),
                ],
                from_='//home/testsuite/precomputes',
                where_clauses=[
                    WhereClause(
                        field='test_field',
                        value='test_value',
                        op=qbm.WhereOps.EQ,
                    ),
                    WhereClause(
                        field='test_field_two', value=45, op=qbm.WhereOps.EQ,
                    ),
                    WhereClause(
                        field='test_field_three',
                        value=['one', 'two'],
                        op=qbm.WhereOps.IN,
                    ),
                ],
                group_by_fields=['group_by_field', 'group_by_field_two'],
                order_by_fields=['order_by_field', 'order_by_field_two'],
                expecting_error=False,
                expected_query=(
                    '-- testsuite/test\n'
                    'SELECT `test_field`,sum(`test_field_two`) AS test_alias '
                    'FROM `//home/testsuite/precomputes` '
                    'PREWHERE `test_field` = \'test_value\' '
                    'AND `test_field_two` = 45 '
                    'AND `test_field_three` IN (\'one\',\'two\') '
                    'GROUP BY `group_by_field`,`group_by_field_two` '
                    'ORDER BY `order_by_field`,`order_by_field_two`'
                ),
            ),
            id='Query with all parts',
        ),
        pytest.param(
            Param(
                fields=[],
                from_='//home/testsuite/precomputes',
                where_clauses=None,
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=True,
                expected_query=None,
            ),
            id='No fields specified -> expecting error',
        ),
        pytest.param(
            Param(
                fields=[Field(field='test_field')],
                from_=None,
                where_clauses=None,
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=True,
                expected_query=None,
            ),
            id='No from specified -> expecting error',
        ),
        pytest.param(
            Param(
                fields=[Field(field='test_field')],
                from_='//home/testsuite/precomputes',
                where_clauses=None,
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=False,
                expected_query=(
                    '-- testsuite/test\n'
                    'SELECT `test_field` '
                    'FROM `//home/testsuite/precomputes`'
                ),
            ),
            id='Query without where',
        ),
        pytest.param(
            Param(
                fields=[Field(field='test_field')],
                from_='//home/testsuite/precomputes',
                where_clauses=[
                    WhereClause(
                        field='test_field', value=56, op=qbm.WhereOps.IN,
                    ),
                ],
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=True,
                expected_query=None,
            ),
            id='Use non-iterable value for IN clause',
        ),
        pytest.param(
            Param(
                fields=[Field(field='test_field')],
                from_='//home/testsuite/precomputes',
                where_clauses=[
                    WhereClause(
                        field='test_field',
                        value=[1, 2, 3],
                        op=qbm.WhereOps.IN,
                    ),
                ],
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=False,
                expected_query=(
                    '-- testsuite/test\n'
                    'SELECT `test_field` '
                    'FROM `//home/testsuite/precomputes` '
                    'PREWHERE `test_field` IN (1,2,3)'
                ),
            ),
            id='Use list of ints for IN clause',
        ),
        pytest.param(
            Param(
                fields=[Field(field='test_field')],
                from_='//home/testsuite/precomputes',
                where_clauses=[
                    WhereClause(
                        field='test_field', value=None, op=qbm.WhereOps.IS,
                    ),
                ],
                group_by_fields=None,
                order_by_fields=None,
                expecting_error=False,
                expected_query=(
                    '-- testsuite/test\n'
                    'SELECT `test_field` '
                    'FROM `//home/testsuite/precomputes` '
                    'PREWHERE `test_field` IS NULL'
                ),
            ),
            id='Use IS NULL',
        ),
    ],
)
def test_query_builder(param):
    builder = qbm.QueryBuilder('test')

    if param.fields:
        for field in param.fields:
            builder.add_field(
                qbm.FieldBuilder(
                    field=field.field, agg=field.agg, alias=field.alias,
                ),
            )

    if param.from_:
        builder.add_from(qbm.YPathBuilder(param.from_))

    if param.where_clauses:
        for clause in param.where_clauses:
            builder.add_prewhere(
                qbm.WhereClauseBuilder(
                    field=clause.field, value=clause.value, op=clause.op,
                ),
            )

    if param.group_by_fields:
        builder.group_by(*param.group_by_fields)

    if param.order_by_fields:
        builder.order_by(*param.order_by_fields)

    if param.expecting_error:
        with pytest.raises(exceptions.QueryBuildingError):
            builder.build()
    else:
        assert builder.build() == param.expected_query


@dataclasses.dataclass(frozen=True)
class YPathParams:
    table_path: str
    revision_id: tp.Optional[int] = None


@pytest.mark.parametrize(
    'ypath_params,expected_ypath',
    [
        pytest.param(
            YPathParams(table_path='//home/testsuite/precomputes'),
            '//home/testsuite/precomputes',
            id='without ypath range',
        ),
        pytest.param(
            YPathParams(
                table_path='//home/testsuite/precomputes', revision_id=10,
            ),
            '//home/testsuite/precomputes[10]',
            id='with revision_id',
        ),
    ],
)
def test_ypath_builder(ypath_params, expected_ypath):
    builder = qbm.YPathBuilder(
        ypath_params.table_path, revision_id=ypath_params.revision_id,
    )
    assert builder.build() == expected_ypath
