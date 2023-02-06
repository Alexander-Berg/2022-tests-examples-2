# pylint: disable=protected-access,invalid-name,redefined-outer-name
# pylint: disable=too-many-lines

import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import select_expr_parser
from crm_admin.quicksegment import sqlike_generator
from crm_admin.quicksegment import sqlike_parser
from crm_admin.quicksegment import variables
import crm_admin.quicksegment.filter_tree as ft
import crm_admin.quicksegment.query_builder as qb
import crm_admin.quicksegment.table_graph as tg


def parse_sqlike(query):
    return sqlike_parser.parse(query)


def parse_col_expr(expr):
    return select_expr_parser.parse(expr)


def gen_sqlike(clause):
    return sqlike_generator.generate(clause)


def flatten(ir):
    yield ir
    for child in ir.children():
        yield from flatten(child)


def qformat(query):
    tokens = query.lower().split()
    tokens = map(lambda t: t.strip(',"\'()'), tokens)
    tokens = filter(bool, tokens)
    return sorted(tokens)


def test_prepare_filters():
    filters = {
        'filters': [
            {'id': 'f1', 'where': parse_sqlike('%{f2} and ${a}')},
            {'id': 'f2', 'where': parse_sqlike('%{f3}')},
            {'id': 'f3', 'where': parse_sqlike('table.a')},
            {
                'id': 'f4',
                'where': parse_sqlike('table.a > 0'),
                'having': parse_sqlike('count(table.b) > 0'),
            },
            {'id': 'f5', 'having': parse_sqlike('count(table.c) > 0')},
        ],
        'targets': ['f1', 'f4', 'f5'],
    }

    clauses = qb.prepare_filters(filters, disabled_filters={})
    assert set(clauses['where']) == {'f1', 'f4'}
    assert set(clauses['having']) == {'f4', 'f5'}

    f1 = flatten(clauses['where']['f1'])
    assert not any(isinstance(o, ft.FilterId) for o in f1)


def test_prepare_filters_some_disabled():
    filters = {
        'filters': [
            {'id': 'f1', 'where': parse_sqlike('%{f2} and ${a}')},
            {'id': 'f2', 'where': parse_sqlike('col is not null')},
            {
                'id': 'f3',
                'where': parse_sqlike('table.a > 0'),
                'having': parse_sqlike('count(table.b) > 0'),
            },
            {'id': 'f4', 'having': parse_sqlike('count(table.c) > 0')},
        ],
        'targets': ['f1', 'f3', 'f4'],
    }
    disabled_filters = {'f2', 'f3'}

    clauses = qb.prepare_filters(filters, disabled_filters=disabled_filters)
    for key in clauses:
        for clause_id, clause in clauses[key].items():
            assert (clause == ft.noop) == (clause_id in disabled_filters)


def test_prepare_filters_with_unknown_names():
    filters = {
        'filters': [{'id': 'f1', 'where': parse_sqlike('%{f2}')}],
        'targets': ['f1'],
    }

    with pytest.raises(error.ValidationError, match='unknown filter id'):
        qb.prepare_filters(filters, disabled_filters={})


def test_derive_anchor_table():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.set_root_table('table_a')
    g.set_anchor_table('table_c')

    # a* <- b <- c*
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')

    clause = parse_sqlike('table_b.col > table_c.col')
    # the base table is "table_b", the anchor is "table_a"
    assert qb.derive_anchor_table(g, 'clause_id', clause) == 'table_a'

    clause = parse_sqlike('table_c.col > 0')
    # the base table is "table_c", the anchor is "table_c"
    assert qb.derive_anchor_table(g, 'clause_id', clause) == 'table_c'


def test_derive_anchor_table_default():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.set_root_table('table_a')

    clause = parse_sqlike('true')
    assert qb.derive_anchor_table(g, 'clause_id', clause) == 'table_a'


def test_derive_anchor_table_ambigous_anchor():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.set_root_table('table_a')
    g.set_anchor_table('table_b')

    # a* <- b* <- d
    # |  <- c  <- |
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_a', 'table_c', 'inner', 'key')
    g.join('table_b', 'table_d', 'inner', 'key')
    g.join('table_c', 'table_d', 'inner', 'key')

    clause = parse_sqlike('table_d.col > 0')
    with pytest.raises(RuntimeError):
        qb.derive_anchor_table(g, 'clause_id', clause)


def test_connect_clauses():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.set_root_table('table_a')
    g.set_anchor_table('table_c')

    # a* <- b <- c*
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')

    clauses = {
        'where': {
            'w_a': parse_sqlike('table_a.col'),
            'w_c': parse_sqlike('table_c.col'),
        },
        'having': {'h_b': parse_sqlike('table_b.col')},
    }
    disabled_filters = {'w_c'}

    assert qb.connect_clauses(g, clauses, disabled_filters) == {
        'where': {'table_a': 'w_a'},
        'having': {'table_a': 'h_b'},
    }


def test_connect_clauses_multiple_subqueries():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.join('table_a', 'table_b', 'left_semi', 'key')
    g.set_root_table('table_a')

    clauses = {
        'where': {
            'f1': parse_sqlike('table_b.col'),
            'f2': parse_sqlike('table_b.col'),
        },
    }

    with pytest.raises(RuntimeError, match='multiple sub-queries'):
        qb.connect_clauses(g, clauses, {})


def test_get_conditions():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.set_root_table('table_a')

    g.table('table_a').set_condition('col > 0')
    g.table('table_c').set_condition('col < 0')

    # a* <- b <- c
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')

    conditions = qb.get_conditions(g)
    assert conditions == {
        'table_a': parse_sqlike('table_a.col > 0'),
        'table_c': parse_sqlike('table_c.col < 0'),
    }


def test_prepare_explicit_projections():
    g = tg.Graph()
    g.add_table('left', None)
    g.add_table('right', None)
    g.set_root_table('left')
    g.join('left', 'right', how='inner', on='key')

    g.table('left').add_column('right.col as col')
    g.table('right').add_column('right.value as col')
    clauses = {'where': {'filt': parse_sqlike('right.col is not null')}}

    projections = qb.prepare_projections(g, clauses)
    expected_left = [parse_col_expr('right.col as col')]
    expected_right = [
        parse_col_expr('right.key as key'),
        parse_col_expr('right.value as col'),
    ]

    def sort_exprs(exprs):
        return sorted(exprs, key=lambda expr: expr.alias)

    assert sort_exprs(projections['right']) == sort_exprs(expected_right)
    assert sort_exprs(projections['left']) == sort_exprs(expected_left)


def test_prepare_projections():
    g = tg.Graph()
    g.add_table('base', None)
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.add_table('table_e', None)
    g.add_table('table_f', None)
    g.add_table('table_g', None)
    g.set_root_table('table_a')
    g.set_anchor_table('table_e')

    g.table('table_a').add_column('col1')
    g.table('table_a').add_column('table_b.value as col2')

    # a* <- b <- c
    # |  <- d <- |
    # |     |
    # |     | <~ e* <- f
    #
    g.join('table_a', 'table_b', 'inner', 'key_a')
    g.join('table_a', 'table_d', 'inner', 'key_a')
    g.join('table_b', 'table_c', 'inner', 'key_b')
    g.join('table_d', 'table_c', 'inner', 'key_d')
    g.join('table_d', 'table_e', 'left_semi', 'key_d')
    g.join('table_e', 'table_f', 'inner', 'key_e')

    projections = qb.prepare_projections(g, {})

    def get_columns(columns):
        def get_column(col_expr):
            if isinstance(col_expr, ft.StarExpr):
                return '*'
            return col_expr.expr.value

        return sorted(map(get_column, columns))

    projections = {
        table: get_columns(cols) for table, cols in projections.items()
    }
    expected = {
        'table_a': ['table_a.col1', 'table_b.value'],
        'table_b': [
            'table_b.key_a',
            'table_b.value',
            'table_c.key_b',
            'table_c.key_d',
        ],
        'table_c': ['table_c.key_b', 'table_c.key_d'],
        'table_d': ['table_c.key_b', 'table_c.key_d', 'table_d.key_a'],
        'table_e': ['table_e.key_d', 'table_f.key_e'],
        'table_f': ['table_f.key_e'],
    }

    assert projections == expected


def test_prepare_projections_with_groupby():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.table('table_b').set_groupby_keys(['key', 'table_c.col'])
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.set_root_table('table_a')

    clauses = {
        'where': {
            'f1': parse_sqlike('table_a.col > 0'),
            'f2': parse_sqlike('table_b.col > 0'),
        },
    }

    projections = qb.prepare_projections(g, clauses)

    def get_columns(table):
        return {col_expr.expr.value for col_expr in projections[table]}

    table_a_cols = get_columns('table_a')
    expected_table_a_cols = set()
    assert table_a_cols == expected_table_a_cols

    table_b_cols = get_columns('table_b')
    expected_table_b_cols = {'table_b.key', 'table_c.col'}
    assert table_b_cols == expected_table_b_cols

    table_c_cols = get_columns('table_c')
    expected_table_c_cols = {'table_c.key', 'table_c.col'}
    assert table_c_cols == expected_table_c_cols


def test_prepare_projections_with_select():
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.set_projection('col3', 'col4')
    g.set_root_table('table_a')

    clauses = {
        'where': {'f': parse_sqlike('table_a.col1 > 0 and table_a.col2 < 0')},
    }

    projections = qb.prepare_projections(g, clauses)

    def get_columns(table):
        return {col_expr.expr.value for col_expr in projections[table]}

    table_a_cols = get_columns('table_a')
    expected_table_a_cols = {'table_a.col3', 'table_a.col4'}
    assert table_a_cols == expected_table_a_cols


def test_prepare_projections_with_select_epxr():
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.add_column('col')
    g.set_root_table('table_a')

    projections = qb.prepare_projections(g, {})

    def get_columns(table):
        return {col_expr.expr.value for col_expr in projections[table]}

    assert get_columns('table_a') == {'table_a.col'}


def test_build_pipelie():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.set_root_table('table_a')
    g.table('table_b').set_groupby_keys(['col'])

    # a* <- b <- c
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')

    clauses = {
        'where': {
            'w_a': parse_sqlike('table_a.col'),
            'w_c': parse_sqlike('table_c.col'),
        },
        'having': {'h_b': parse_sqlike('table_b.col')},
    }
    table_to_clause = {
        'where': {'table_a': 'w_a', 'table_c': 'w_c'},
        'having': {'table_b': 'h_b'},
    }
    projections = {
        'table_a': ['key', 'col'],
        'table_b': ['key', 'col'],
        'table_c': ['key', 'col'],
    }

    pipeline = qb.build_pipeline(
        table_graph=g,
        clauses=clauses,
        table_to_clause=table_to_clause,
        projections=projections,
        conditions={},
    )
    assert pipeline.dict_repr() == {
        'pipeline': [
            {'read': '<table_a>'},
            {
                'inner join': {
                    'pipeline': [
                        {'read': '<table_b>'},
                        {
                            'inner join': {
                                'pipeline': [
                                    {'read': '<table_c>'},
                                    {'where': '<w_c>'},
                                    {'select': '<table_c>'},
                                ],
                            },
                        },
                        {'group by': '<table_b>'},
                        {'having': '<h_b>'},
                        {'select': '<table_b>'},
                    ],
                },
            },
            {'where': '<w_a>'},
            {'select': '<table_a>'},
        ],
    }


def test_build_query():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.table('table_b').set_condition('value > 0')
    g.set_root_table('table_a')
    g.join('table_a', 'table_b', 'inner', 'key')
    g.isolate_subqueries()

    g.table('table_a').add_column('value as a_value')
    g.table('table_a').add_column('table_b.value as b_value')
    g.table('table_b').add_column('table_b.value2 as value2')

    filters = {
        'filters': [
            {
                'id': 'main',
                'where': parse_sqlike('table_a.value < table_b.value'),
            },
        ],
        'targets': ['main'],
        'extra_columns': [
            {
                'if': parse_sqlike('false'),
                'then': parse_col_expr('table_a.extra_column'),
            },
        ],
    }

    tables, query = qb.build_query(g, filters)

    expected = """
            SELECT __table_b__value AS b_value,
               extra_column,
               value AS a_value
          FROM table_a
         INNER JOIN (
                SELECT KEY AS __table_b__key,
                       value AS __table_b__value,
                       value2 AS __table_b__value2
                  FROM (
                      SELECT *
                        FROM table_b
                       WHERE table_b.value > 0
                     ) AS table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         WHERE table_a.value < __table_b__value
    """

    assert qformat(query) == qformat(expected)
    assert {t.name for t in tables} == {'table_a', 'table_b'}


def test_build_query_with_variables():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.table('table_a').add_column('value')
    g.set_root_table('table_a')
    g.join('table_a', 'table_b', 'inner', 'key')
    g.isolate_subqueries()

    filters = {
        'filters': [
            {'id': 'main', 'where': parse_sqlike('table_a.value < ${var}')},
        ],
        'targets': ['main'],
        'extra_columns': [
            {
                'if': parse_sqlike('${extracol}'),
                'then': parse_col_expr('table_a.extra_column_1'),
            },
            {
                'if': parse_sqlike('not ${extracol}'),
                'then': parse_col_expr('table_a.extra_column_2'),
            },
        ],
    }

    vs = variables.Variables({'var': 1, 'extracol': True})
    _, query = qb.build_query(g, filters, vs)

    expected = """
            SELECT value,
                   extra_column_1
          FROM table_a
         INNER JOIN (
                SELECT KEY AS __table_b__key
                  FROM table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         WHERE table_a.value < 1
    """

    assert qformat(query) == qformat(expected)


def test_build_query_projection_variables():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.table('table_a').add_column('col - ${var} as col')
    g.set_root_table('table_a')

    filters = {
        'filters': [{'id': 'main', 'where': parse_sqlike('true')}],
        'targets': ['main'],
        'extra_columns': [],
    }

    vs = variables.Variables({'var': 1, 'extracol': True})
    _, query = qb.build_query(g, filters, vs)

    expected = """
        SELECT col - 1 AS col
          FROM table_a
         WHERE TRUE
    """

    assert qformat(query) == qformat(expected)


def test_build_query_with_yson_columns():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/a')

    g.join('table_a', 'table_b', how='inner', on='key')
    g.table('table_a').add_column('col->key1 as col')
    g.set_root_table('table_a')

    filters = {
        'filters': [
            {'id': 'main', 'where': parse_sqlike('table_b.col->key1 > 0')},
        ],
        'targets': ['main'],
        'extra_columns': [
            {
                'if': parse_sqlike('true'),
                'then': parse_col_expr('table_b.col->key2 as key2'),
            },
        ],
    }

    vs = variables.Variables({'var': 1, 'extracol': True})
    _, query = qb.build_query(g, filters, vs)

    expected = """
        SELECT __table_b__col.key2 AS key2,
               col.key1 AS col
          FROM table_a
         INNER JOIN (
                SELECT col AS __table_b__col,
                       KEY AS __table_b__key
                  FROM table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         WHERE __table_b__col.key1 > 0
    """

    assert qformat(query) == qformat(expected)


def test_build_query_with_optional_joins():
    #
    # a* <-* b
    # |  <-* c
    # |  <-* d
    #
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.add_table('table_c', '//path/to/c')
    g.add_table('table_d', '//path/to/d')

    g.table('table_a').add_column('table_b.col as col')
    g.set_root_table('table_a')

    g.join('table_a', 'table_b', 'inner', 'key').is_optional = True
    g.join('table_a', 'table_c', 'inner', 'key').is_optional = True
    g.join('table_a', 'table_d', 'inner', 'key').is_optional = True

    filters = {
        'filters': [{'id': 'main', 'where': parse_sqlike('table_c.col > 0')}],
        'targets': ['main'],
        'extra_columns': [],
    }

    vs = variables.Variables({})
    _, query = qb.build_query(g, filters, vs)

    # table_b is requred for table_a's projection
    # table_c is used in filters
    # table_d should be absent in the resultant query

    expected = """
        SELECT __table_b__col AS col
          FROM table_a
         INNER JOIN (
                SELECT col AS __table_b__col,
                       KEY AS __table_b__key
                  FROM table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         INNER JOIN (
                SELECT col AS __table_c__col,
                       KEY AS __table_c__key
                  FROM table_c
               ) AS table_c
            ON table_a.key = table_c.__table_c__key
         WHERE __table_c__col > 0
    """

    assert qformat(query) == qformat(expected)


def test_resolve_all_variables():
    clauses = {
        'where': {'clause_a': parse_sqlike('a > ${a}')},
        'having': {'clause_a': parse_sqlike('count(b) > ${b}')},
    }
    vs = variables.Variables({'a': 1, 'b': 2})

    qb.resolve_all_variables(clauses, vs)

    assert clauses['where']['clause_a'] == parse_sqlike('a > 1')
    assert clauses['having']['clause_a'] == parse_sqlike('count(b) > 2')


def test_resolve_all_variables_failure():
    clauses = {
        'where': {'clause_a': parse_sqlike('a > ${a}')},
        'having': {'clause_a': parse_sqlike('count(b) > ${b}')},
    }
    vs = variables.Variables({'a': 1})

    with pytest.raises(RuntimeError, match='undefined variable'):
        qb.resolve_all_variables(clauses, vs)


def test_validate_groupby_clauses():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.join('table_a', 'table_b', 'inner', 'key')
    g.set_root_table('table_a')

    clauses = {'having': {'f': parse_sqlike('count(table_b.col) > 0')}}
    table_to_clause = {'having': {'table_b': 'f'}}

    with pytest.raises(RuntimeError, match='no groupby'):
        qb.connect_clauses(g, clauses, {})
        qb.validate(g, clauses, table_to_clause)


def test_substitute_variables():
    clause = parse_sqlike(
        'a < ${a} or (b > ${b} and c > ${c}[0] and d = ${#c})',
    )

    vs = variables.Variables({'a': 1, 'b': 2, 'c': [3, 4]})
    clause = qb.substitute_variables(clause, vs, True)
    assert gen_sqlike(clause) == '(a < 1) or ((b > 2) and (c > 3) and (d = 2))'


def test_substitute_variable_size_type_error():
    clause = parse_sqlike('a = ${#a}')

    vs = variables.Variables({'a': 1})
    with pytest.raises(error.ValidationError, match='has no len'):
        qb.substitute_variables(clause, vs, True)


def test_resolve_projection_variables():
    projections = {'table': [parse_col_expr('col + ${var} as col')]}
    vs = variables.Variables({'var': 1})

    qb.resolve_projection_variables(projections, vs)

    expected = {'table': [parse_col_expr('col + 1 as col')]}
    assert projections == expected


@pytest.mark.parametrize('strict', [True, False])
def test_substitute_missing_variables(strict):
    clause = parse_sqlike('${a}')
    vs = variables.Variables({})
    if strict:
        with pytest.raises(RuntimeError):
            qb.substitute_variables(clause, vs, strict)
    else:
        assert qb.substitute_variables(clause, vs, strict) == ft.Constant(None)


def test_evaluate_enabled_if_clauses():
    filters = {
        'filters': [
            {'id': 'f1', 'enabled-if': parse_sqlike('${var} is not null')},
            {'id': 'f2', 'enabled-if': parse_sqlike('${var} is null')},
        ],
    }

    vs = variables.Variables({})
    disabled_filters = qb.evaluate_enabled_if_clauses(filters, vs)
    assert filters['filters'][0]['enabled-if'] is False
    assert filters['filters'][1]['enabled-if'] is True
    assert disabled_filters == {'f1'}


def test_evaluate_enabled_if_clauses_failure():
    filters = {'filters': [{'id': 'f1', 'enabled-if': parse_sqlike('${var}')}]}

    vs = variables.Variables({})
    with pytest.raises(RuntimeError, match='could not evaluate'):
        qb.evaluate_enabled_if_clauses(filters, vs)


def test_cut_inacive_joins():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.add_table('table_e', None)
    g.add_table('table_f', None)
    g.add_table('table_g', None)
    g.add_table('table_h', None)
    g.add_table('table_i', None)
    g.set_root_table('table_a')

    # a* <~ b   # no active filter
    # |  <~ c   # is_optional = False
    # |  <~ d   # has an active filter
    # |  <~ e <- f  # `f` has an active filter
    # |  <-* g  # used in projections
    # |  <-* h  # used in filters
    # |  <-* i
    #
    g.join('table_a', 'table_b', 'left_semi', 'key')
    g.join('table_a', 'table_c', 'left_anti', 'key').is_optional = False
    g.join('table_a', 'table_d', 'left_semi', 'key')
    g.join('table_a', 'table_e', 'left_semi', 'key')
    g.join('table_e', 'table_f', 'inner', 'key')
    g.join('table_a', 'table_g', 'inner', 'key').is_optional = True
    g.join('table_a', 'table_h', 'inner', 'key').is_optional = True
    g.join('table_a', 'table_i', 'inner', 'key').is_optional = True

    projections = {'table_a': [parse_col_expr('table_g.col as col')]}

    table_to_clause = {
        'where': {
            'table_a': 'clause_a',
            # 'clause_b' and 'clause_c' are disabled
            'table_d': 'clause_d',
            'table_f': 'clause_f',
        },
    }

    clauses = {
        'where': {
            'clause_a': parse_sqlike('table_h.col > 0'),
            'clause_d': parse_sqlike('table_d.col > 0'),
            'clause_f': parse_sqlike('table_f.col > 0'),
        },
    }

    qb.cut_inactive_joins(g, table_to_clause, clauses, projections)
    assert not g.has_relation('table_a', 'table_b')
    assert g.has_relation('table_a', 'table_c')
    assert g.has_relation('table_a', 'table_e')
    assert g.has_relation('table_a', 'table_d')


def test_configure_parittioned_tables():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)

    filters = {
        'filters': [
            {
                'id': 'f1',
                'history_depth_days': {'table_a': 'varname', 'table_c': 20},
            },
            {'id': 'f2', 'history_depth_days': {'table_d': 100}},
        ],
    }
    disabled_filters = {'f2'}
    qb.configure_paritioned_tables(g, filters, disabled_filters)

    assert g.table('table_a').history_depth_days == ft.Variable('varname')
    assert g.table('table_b').history_depth_days is None
    assert g.table('table_c').history_depth_days == 20
    assert g.table('table_d').history_depth_days is None


def test_substitute_history_depth():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)

    g.table('table_a').set_history_depth_days('varname')
    g.table('table_c').set_history_depth_days(20)

    vs = variables.Variables({'varname': 30})
    qb.substitute_history_depth(g, vs)

    assert g.table('table_a').history_depth_days == vs.get('varname')
    assert g.table('table_b').history_depth_days is None
    assert g.table('table_c').history_depth_days == 20


@pytest.mark.parametrize(
    'is_partitioned, days, error',
    [
        (True, 30, None),
        (False, 30, 'not a partitioned table'),
        (True, None, 'no history depth'),
    ],
)
def test_validate_partitioned_tables(is_partitioned, days, error):
    g = tg.Graph()
    t = g.add_table('table', None)
    t.is_partitioned = is_partitioned
    t.set_history_depth_days(days)
    g.set_root_table('table')

    if error:
        with pytest.raises(RuntimeError, match=error):
            qb._validate_paritioned_tables(g)
    else:
        qb._validate_paritioned_tables(g)


@pytest.mark.parametrize('are_joined', [True, False])
def test_validate_partitioned_tables_cutoff_joins(are_joined):
    g = tg.Graph()
    g.add_table('table_a', None)
    g.set_root_table('table_a')

    t = g.add_table('table_b', None)
    t.is_partitioned = True
    # missing t.history_depth_days

    if are_joined:
        g.join('table_a', 'table_b', 'left_outer', 'key')

    if are_joined:
        with pytest.raises(RuntimeError, match='no history depth'):
            qb._validate_paritioned_tables(g)
    else:
        qb._validate_paritioned_tables(g)


def test_handle_optional_tables():
    g = tg.Graph()
    g.add_table('table_a', None)
    table_b = g.add_table('table_b', None)
    table_c = g.add_table('table_c', None)
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_a', 'table_c', 'inner', 'key')
    g.set_root_table('table_a')

    table_b.is_optional = True
    table_b.path = 'var1'

    table_c.is_optional = True
    table_c.path = 'var2'

    vs = variables.Variables({'var1': 'path/to/table_a'})
    qb.handle_optional_tables(g, vs)

    assert g.has_relation('table_a', 'table_b')
    assert table_b.path == 'path/to/table_a'
    assert not g.has_relation('table_a', 'table_c')


@pytest.mark.parametrize(
    'condition, result, error_msg',
    [
        ('${true_var}', True, None),
        ('not ${true_var}', False, None),
        ('${unknown-var}', None, 'could not evaluate'),
    ],
)
def test_evaluate_column_conditions(condition, result, error_msg):
    extra_columns = [
        {'if': parse_sqlike(condition), 'then': parse_col_expr('table.col')},
    ]
    vs = variables.Variables({'true_var': True})

    if error_msg:
        with pytest.raises(error.ValidationError, match=error_msg):
            qb.evaluate_column_conditions(extra_columns, vs)
    else:
        cols = qb.evaluate_column_conditions(extra_columns, vs)
        assert cols[0]['if'] == result


def test_add_enabled_columns():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.set_root_table('table_a')

    extra_columns = [
        {'if': True, 'then': parse_col_expr('table.extra_col1')},
        {'if': False, 'then': parse_col_expr('table.extra_col2')},
    ]

    qb.add_enabled_columns(g, extra_columns)
    assert 'extra_col1' in g.table('table_a').projection
    assert 'extra_col2' not in g.table('table_a').projection


def test_add_columns_unconditionally():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.set_root_table('table_a')

    extra_columns = [
        {'if': True, 'then': parse_col_expr('table.extra_col1')},
        {'if': False, 'then': parse_col_expr('table.extra_col2')},
    ]

    qb.add_columns_unconditionally(g, extra_columns)
    assert 'extra_col1' in g.table('table_a').projection
    assert 'extra_col2' in g.table('table_a').projection


@pytest.mark.parametrize(
    'value, expected',
    [
        (1, ft.Constant(1)),
        ('str', ft.Constant('str')),
        (True, ft.Constant(True)),
        (None, ft.Constant(None)),
        ([1, 2], ft.List([ft.Constant(1), ft.Constant(2)])),
    ],
)
def test_constant_to_node(value, expected):
    assert qb.constant_to_node(value) == expected


def test_substitute_templates():
    clause = parse_sqlike('${{g1.val}} > ${{g2.val}}')
    vs = variables.Variables(
        {'g1': [{'val': 1}, {'val': 2}], 'g2': [{'val': 3}]},
    )
    expected = '(1 > 3) or (2 > 3)'

    result = qb.substitute_templates(clause, vs)
    assert gen_sqlike(result) == expected


def test_substitute_template_sizes():
    clause = parse_sqlike('col = ${{#g.vals}}')
    vs = variables.Variables({'g': [{'vals': [1, 2]}, {'vals': [3, 4, 5]}]})
    expected = '(col = 2) or (col = 3)'

    result = qb.substitute_templates(clause, vs)
    assert gen_sqlike(result) == expected


def test_substitute_template_sizes_type_error():
    clause = parse_sqlike('col = ${{#g.vals}}')
    vs = variables.Variables({'g': [{'val': 1}]})

    with pytest.raises(error.ValidationError, match='has no len'):
        qb.substitute_templates(clause, vs)


def test_build_query_with_templates():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.set_root_table('table_a')

    filters = {
        'filters': [
            {
                'id': 'main',
                'where': parse_sqlike('table_a.value < ${{g.val}}'),
            },
        ],
        'targets': ['main'],
        'extra_columns': [],
    }

    vs = variables.Variables({'g': [{'val': 1}, {'val': 2}]})
    _, query = qb.build_query(g, filters, vs)

    expected = """
            SELECT *
          FROM table_a
         WHERE table_a.value < 1 or table_a.value < 2
    """

    assert qformat(query) == qformat(expected)


def test_build_query_with_star_expr():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.set_root_table('table_a')
    g.join('table_a', 'table_b', 'inner', 'key')

    g.table('table_a').add_column('*')
    g.table('table_a').add_column('table_b.*')

    filters = {'filters': [], 'targets': [], 'extra_columns': []}

    tables, query = qb.build_query(g, filters)

    expected = """
            SELECT *,
               table_b.*
          FROM table_a
         INNER JOIN (
                SELECT *,
                       key AS __table_b__key
                  FROM table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
    """

    assert qformat(query) == qformat(expected)
    assert {t.name for t in tables} == {'table_a', 'table_b'}


def test_simplify_clauses():
    clauses = {
        'where': {
            'f1': parse_sqlike('true and true'),
            'f2': ft.Operator('and', [ft.noop, ft.noop]),
        },
        'having': {'f3': parse_sqlike('true or false')},
    }

    disabled_filters = set()
    qb.simplify_clauses(clauses, disabled_filters)

    assert clauses['where']['f1'] == parse_sqlike('true')
    assert clauses['where']['f2'] == ft.noop
    assert clauses['having']['f3'] == parse_sqlike('true')
    assert disabled_filters == {'f2'}


def test_join_keys():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.add_table('table_c', '//path/to/c')
    g.set_root_table('table_a')

    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_a', 'table_c', 'inner', on='table_b.col', right_on='key')
    g.table('table_b').add_keys('col')

    filters = {
        'filters': [{'id': 'main', 'where': parse_sqlike('1 = 1')}],
        'targets': ['main'],
        'extra_columns': [],
    }

    _, query = qb.build_query(g, filters)

    expected = """
            SELECT *
          FROM table_a
         INNER JOIN (
                SELECT col AS __table_b__col,
                       KEY AS __table_b__key
                  FROM table_b
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         INNER JOIN (
                SELECT KEY AS __table_c__key
                  FROM table_c
               ) AS table_c
            ON table_b.__table_b__col = table_c.__table_c__key
         WHERE TRUE
    """

    assert qformat(query) == qformat(expected)


def test_build_query_duplicate_key_names():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.add_table('table_c', '//path/to/b')
    g.set_root_table('table_a')

    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')

    filters = {
        'filters': [{'id': 'main', 'where': parse_sqlike('true')}],
        'targets': ['main'],
        'extra_columns': [],
    }

    _, query = qb.build_query(g, filters)

    expected = """
        SELECT *
          FROM table_a
         INNER JOIN (
                SELECT __table_c__key,
                       KEY AS __table_b__key
                  FROM table_b
                 INNER JOIN (
                        SELECT KEY AS __table_c__key
                          FROM table_c
                       ) AS table_c
                    ON table_b.key = table_c.__table_c__key
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
         WHERE TRUE
    """
    assert qformat(query) == qformat(expected)


def test_build_query_filter_semi_joined_table():
    g = tg.Graph()
    g.add_table('table_a', '//path/to/a')
    g.add_table('table_b', '//path/to/b')
    g.add_table('table_c', '//path/to/b')
    g.set_root_table('table_a')

    g.join('table_a', 'table_b', 'left_semi', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.isolate_subqueries()

    filters = {
        'filters': [
            {'id': 'main', 'where': parse_sqlike('table_c.key = 123')},
        ],
        'targets': ['main'],
        'extra_columns': [],
    }

    _, query = qb.build_query(g, filters)

    expected = """
        SELECT *
          FROM table_a
          LEFT SEMI JOIN (
                SELECT __table_c__key,
                       KEY AS __table_b__key
                  FROM table_b
                 INNER JOIN (
                        SELECT KEY AS __table_c__key
                          FROM table_c
                       ) AS table_c
                    ON table_b.key = table_c.__table_c__key
                 WHERE __table_c__key = 123
               ) AS table_b
            ON table_a.key = table_b.__table_b__key
    """
    assert qformat(query) == qformat(expected)
