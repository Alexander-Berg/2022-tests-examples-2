# pylint: disable=invalid-name,abstract-method

import pytest

from crm_admin.quicksegment import pipeline as pl
from crm_admin.quicksegment import select_expr_parser
from crm_admin.quicksegment import sqlike_parser


def parse_sqlike(query):
    return sqlike_parser.parse(query)


def parse_col_expr(query):
    return select_expr_parser.parse(query)


def test_read():
    t = pl.Read('path', 'alias')
    clause = t.generate_sql(None)
    assert clause == 'from alias'


@pytest.mark.parametrize('join', ['left outer join', 'inner join'])
def test_join(join):
    right_task = pl.Read('left_path', 'left_alias')
    t = pl.Join(join, 'left', 'right', right_task, [('lkey', 'rkey')])
    clause = t.generate_sql('<head>')

    assert (
        clause.split()
        == f"""
        <head> {join} (
            from left_alias
        ) as right on left.lkey = right.__right__rkey
    """.split()
    )


@pytest.mark.parametrize('join', ['left outer join', 'inner join'])
def test_join_by_other_table_column(join):
    right_task = pl.Read('left_path', 'left_alias')
    t = pl.Join(join, 'left', 'right', right_task, [('other.lkey', 'rkey')])
    clause = t.generate_sql('<head>')

    assert (
        clause.split()
        == f"""
        <head> {join} (
            from left_alias
        ) as right on other.__other__lkey = right.__right__rkey
    """.split()
    )


@pytest.mark.parametrize('clause_type', ['where', 'having'])
def test_select(clause_type):
    t = pl.Select(
        'base_table', clause_type, 'clause_id', parse_sqlike('table.col > 0'),
    )
    clause = t.generate_sql('<head>')
    assert clause == f'<head> {clause_type} __table__col > 0'


@pytest.mark.parametrize('clause_type', ['where', 'having'])
def test_select_same_table(clause_type):
    t = pl.Select(
        'table', clause_type, 'clause_id', parse_sqlike('table.col > 0'),
    )
    clause = t.generate_sql('<head>')
    assert clause == f'<head> {clause_type} table.col > 0'


def test_groupby():
    t = pl.GroupBy('table', ['a', 'b', 'subtable.c'])
    clause = t.generate_sql('<head>')
    assert clause == '<head> group by a,b,subtable.__subtable__c'


@pytest.mark.parametrize('is_root', [True, False])
def test_project(is_root):
    def parse(expr, pass_through=False):
        col_expr = parse_col_expr(expr)
        col_expr.pass_through = pass_through
        return col_expr

    t = pl.Project(
        'table_a',
        [
            parse_col_expr('table_a.val as a'),
            parse('table_b.val1 as val1', pass_through=False),
            parse('table_b.val2 as val2', pass_through=True),
            parse_col_expr('fn(table_b.val) as fn'),
            parse_col_expr('table_a.obj->field as obj1'),
            parse_col_expr('table_b.obj->field as obj2'),
        ],
        is_root=is_root,
    )
    clause = t.generate_sql('<tail>')
    if is_root:
        assert clause == (
            'select '
            '__table_b__obj.field as obj2, '
            '__table_b__val1 as val1, '
            '__table_b__val2 as val2, '
            'fn(__table_b__val) as fn, '
            'obj.field as obj1, '
            'val as a '
            '<tail>'
        )
    else:
        assert clause == (
            'select '
            '__table_b__obj.field as __table_a__obj2, '
            '__table_b__val1 as __table_a__val1, '
            '__table_b__val2, '
            'fn(__table_b__val) as __table_a__fn, '
            'obj.field as __table_a__obj1, '
            'val as __table_a__a '
            '<tail>'
        )


@pytest.mark.parametrize('is_root', [True, False])
def test_project_star(is_root):
    t = pl.Project(
        'table_a',
        [parse_col_expr('*'), parse_col_expr('table_a.*')],
        is_root=is_root,
    )
    clause = t.generate_sql('<tail>')
    assert clause == 'select *, table_a.* <tail>'


def test_project_default():
    t = pl.Project('table_a', [])
    clause = t.generate_sql('<tail>')
    assert clause == 'select * <tail>'


def test_read_from_subquery():
    t = pl.Read(
        path=None,
        alias='alias',
        subquery=pl.Pipeline(
            [
                pl.Read('path', 'alias'),
                pl.Project('alias', [parse_col_expr('*')]),
            ],
        ),
    )
    clause = t.generate_sql(None)
    assert clause == 'from (select * from alias) as alias'


def test_pipeline():
    class Task(pl.Task):
        def __init__(self, name):
            self.name = name

        def generate_sql(self, arg):
            return ' '.join([arg, self.name])

    t = pl.Pipeline([Task('a'), Task('b'), Task('c')])
    assert t.generate_sql('<input>') == '<input> a b c'
