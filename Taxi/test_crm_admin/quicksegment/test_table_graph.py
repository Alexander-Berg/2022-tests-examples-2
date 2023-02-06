# pylint: disable=invalid-name

import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import filter_tree as ft
from crm_admin.quicksegment import select_expr_parser
from crm_admin.quicksegment import table_graph as tg


def test_add_table():
    g = tg.Graph()
    g.add_table('table_a', 'path_b')
    g.add_table('table_b', 'path_b')

    with pytest.raises(error.ValidationError):
        g.add_table('table_a', 'some other path')

    assert g.graph.number_of_nodes() == 2
    assert g.table('table_a').name == 'table_a'
    assert g.table('table_b').name == 'table_b'


def test_edges():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)

    g.join('table_a', 'table_b', 'inner', on='key')
    g.join('table_b', 'table_c', 'inner', on='key')

    with pytest.raises(error.ValidationError):
        g.join('table_a', 'table_b', 'left_outer', on='other-key')

    with pytest.raises(error.ValidationError):
        g.join('table_x', 'table_y', 'inner', on='key')

    assert g.graph.number_of_edges() == 2
    g.relation('table_a', 'table_b').how = 'inner'
    g.relation('table_a', 'table_b').on = [('key', 'key')]


def test_root_table():
    g = tg.Graph()
    g.add_table('table_a', None)

    with pytest.raises(error.ValidationError):
        g.set_root_table('table_b')
    g.set_root_table('table_a')

    assert g.root_table() == 'table_a'


def test_set_anchor_table():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.set_anchor_table('table_a')
    g.set_anchor_table('table_b')

    # a* <- b* <- c
    # |  <- d
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.join('table_a', 'table_d', 'inner', 'key')

    assert g.anchor_table('table_a') == 'table_a'
    assert g.anchor_table('table_b') == 'table_b'
    assert g.anchor_table('table_c') == 'table_b'
    assert g.anchor_table('table_d') == 'table_a'


def test_get_anchor_table():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.set_anchor_table('table_a')
    g.set_anchor_table('table_b')

    # a* <- b* <- d
    # |  <-  c <- |
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_d', 'inner', 'key')
    g.join('table_a', 'table_c', 'inner', 'key')
    g.join('table_c', 'table_d', 'inner', 'key')

    assert g.anchor_table('table_a') == 'table_a'
    assert g.anchor_table('table_b') == 'table_b'
    assert g.anchor_table('table_c') == 'table_a'
    with pytest.raises(AssertionError):
        g.anchor_table('table_d')
    assert g.anchor_tables('table_a') == ['table_a']
    assert set(g.anchor_tables('table_d')) == {'table_a', 'table_b'}


def test_isolate_subqueries():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.add_table('table_e', None)
    g.add_table('table_f', None)
    g.add_table('table_g', None)

    g.set_root_table('table_a')
    g.table('table_e').set_condition('col is not null')

    # a* <~ b <- c
    # |  <- d
    # |  <- e
    # |  <-* f <- g
    #
    g.join('table_a', 'table_b', 'left_semi', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.join('table_a', 'table_d', 'inner', 'key')
    g.join('table_a', 'table_e', 'inner', 'key')
    g.join('table_a', 'table_f', 'inner', 'key')
    g.join('table_f', 'table_g', 'inner', 'key')

    g.relation('table_a', 'table_f').is_optional = True

    g.isolate_subqueries()

    assert g.anchor_table('table_a') == 'table_a'
    assert g.anchor_table('table_b') == 'table_b'
    assert g.anchor_table('table_c') == 'table_b'
    assert g.anchor_table('table_d') == 'table_a'
    assert g.anchor_table('table_e') == 'table_e'
    assert g.anchor_table('table_f') == 'table_a'
    assert g.anchor_table('table_g') == 'table_a'


def test_remove_table():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.add_table('table_e', None)
    g.set_anchor_table('table_a')

    # a* <- b <--- c
    # |  <- d <--- |
    #       | <- e
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.join('table_a', 'table_d', 'inner', 'key')
    g.join('table_d', 'table_c', 'inner', 'key')
    g.join('table_d', 'table_e', 'inner', 'key')

    g.remove_table('table_d')
    assert 'table_d' not in g.graph
    assert 'table_e' not in g.graph
    assert 'table_c' in g.graph


def test_cut():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.add_table('table_e', None)
    g.set_anchor_table('table_a')

    # a* <- b <--- c
    # |  <- d <--- |
    #       | <- e
    #
    g.join('table_a', 'table_b', 'inner', 'key')
    g.join('table_b', 'table_c', 'inner', 'key')
    g.join('table_a', 'table_d', 'inner', 'key')
    g.join('table_d', 'table_c', 'inner', 'key')
    g.join('table_d', 'table_e', 'inner', 'key')

    g.cut('table_a', 'table_d')
    assert not g.has_relation('table_a', 'table_d')
    assert 'table_d' not in g.graph
    assert 'table_e' not in g.graph
    assert 'table_c' in g.graph


def test_cut_edge():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.join('table_a', 'table_b', 'inner', 'key')

    assert g.has_relation('table_a', 'table_b')
    g.cut_edge(('table_b', 'table_a'))
    assert not g.has_relation('table_a', 'table_b')


def test_has_relation():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.join('table_a', 'table_b', 'inner', on='key')
    g.set_root_table('table_a')

    assert g.has_relation('table_a', 'table_b')
    assert not g.has_relation('table_b', 'table_a')


def test_validate_ok():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.join('table_a', 'table_b', 'inner', on='key')
    g.set_root_table('table_a')

    assert tg.validate(g)


def test_validate_cycles():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.set_root_table('table_a')

    # a* <- b <- c
    # |  -> - -> |
    #
    g.join('table_a', 'table_b', 'inner', on='key')
    g.join('table_b', 'table_c', 'inner', on='key')
    g.join('table_c', 'table_a', 'inner', on='key')

    with pytest.raises(error.ValidationError, match='cycles detected'):
        tg.validate(g)


def test_validate_root_table():
    g = tg.Graph()
    g.add_table('table_a', None)

    with pytest.raises(error.ValidationError, match='no root table'):
        tg.validate(g)


def test_join_on_expression():
    g = tg.Graph()
    g.add_table('left', None)
    g.add_table('right', None)
    g.set_root_table('left')

    with pytest.raises(error.ValidationError, match='can not join'):
        g.join('left', 'right', how='inner', on='col->key')


def test_groupby_expression():
    g = tg.Graph()
    g.add_table('table', None)
    g.set_root_table('table')

    with pytest.raises(error.ValidationError, match='can not group by'):
        g.table('table').set_groupby_keys(['col->key'])


@pytest.mark.parametrize(
    'how, ok',
    [
        ('left_outer', True),
        ('inner', True),
        ('left_semi', True),
        ('left_anti', True),
        ('cross_join', False),
    ],
)
def test_validate_join_names(how, ok):
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.set_root_table('table_a')
    g.join('table_a', 'table_b', how, 'key')

    if not ok:
        with pytest.raises(error.ValidationError, match='invalid join'):
            tg.validate(g)
    else:
        assert tg.validate(g)


@pytest.mark.parametrize(
    'expr, error_msg',
    [('col', None), ('unknown_table.col', 'Unknow table'), ('*', None)],
)
def test_validate_column_expressions(expr, error_msg):
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.add_column(expr)
    g.set_root_table('table_a')

    if error_msg:
        with pytest.raises(error.ValidationError, match=error_msg):
            tg.validate(g)
    else:
        assert tg.validate(g)


@pytest.mark.parametrize(
    'dtype, error_msg',
    [
        ('string', None),
        ('array<integer>', None),
        ('map<string, boolean>', None),
        ('array<array<string>>', None),
        ('struct[name: array<string>]', None),
        ('string1', 'type is not supported'),
        ('array<string1>', 'type is not supported'),
    ],
)
def test_validate_schema_hints(dtype, error_msg):
    g = tg.Graph()
    g.add_table('table_a', None)
    g.set_root_table('table_a')

    g.table('table_a').add_schema_hint('col', dtype)
    if error_msg:
        with pytest.raises(error.ValidationError, match=error_msg):
            tg.validate(g)
    else:
        assert tg.validate(g)


def test_connected_subgraph():
    g = tg.Graph()
    g.add_table('table_a', None)
    g.add_table('table_b', None)
    g.add_table('table_c', None)
    g.add_table('table_d', None)
    g.set_root_table('table_a')

    # a* <- b
    # |  x- c <- d
    #
    g.join('table_a', 'table_b', 'left_outer', 'key')
    g.join('table_c', 'table_d', 'left_outer', 'key')

    subgraph = g.connected_subgraph()
    assert subgraph.root_table() == g.root_table()
    assert set(subgraph.graph.nodes()) == {'table_a', 'table_b'}


def test_add_column():
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.add_column('col1')
    t.add_column(select_expr_parser.parse('col2'))

    assert 'col1' in t.projection
    assert 'col2' in t.projection
    assert isinstance(t.projection['col1'], ft.ColExpr)

    with pytest.raises(error.ValidationError, match='duplicate column'):
        t.add_column('col3 as col1')


def test_set_projection():
    g = tg.Graph()
    t = g.add_table('table_a', None)

    t.add_column('col1')
    assert not t.custom_projection

    t.set_projection('col2', 'col3')
    assert t.custom_projection
    assert 'col1' not in t.projection
    assert 'col2' in t.projection
    assert 'col3' in t.projection


def test_set_condition():
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.set_condition('col is not null')
    assert isinstance(t.condition, ft.Node)


@pytest.mark.parametrize(
    'value, dtype',
    [
        (10, int),
        (None, None),
        ('varname', ft.Variable),
        ('${varname}', ft.Variable),
    ],
)
def test_set_history_depth_days(value, dtype):
    g = tg.Graph()
    t = g.add_table('table_a', None)
    t.set_history_depth_days(value)

    if value is not None:
        assert isinstance(t.history_depth_days, dtype)
    else:
        assert t.history_depth_days is None


def test_iter_subgraph():
    g = tg.Graph()
    g.add_table('a', None)
    g.add_table('b', None)
    g.add_table('c', None)
    g.add_table('d', None)
    g.add_table('e', None)
    g.add_table('f', None)
    g.add_table('g', None)
    g.set_root_table('a')

    # a* <- b
    # |  <- c
    # |  <- d <- e
    #       | <- f <- g
    #
    g.join('a', 'b', 'inner', 'key')
    g.join('a', 'c', 'inner', 'key')
    g.join('a', 'd', 'inner', 'key')
    g.join('d', 'e', 'inner', 'key')
    g.join('d', 'f', 'inner', 'key')
    g.join('f', 'g', 'inner', 'key')

    subgraph = g.iter_subgraph('d')
    assert set(subgraph) == {'d', 'e', 'f', 'g'}

    reverse_subgraph = g.iter_subgraph('d', reverse=True)
    assert set(reverse_subgraph) == {'d', 'a'}


@pytest.mark.parametrize(
    'how, is_optional',
    [
        ('left_outer', False),
        ('inner', False),
        ('left_semi', True),
        ('left_anti', True),
    ],
)
def test_default_optional_flag(how, is_optional):
    r = tg.Relation(how, 'left', 'right', 'key')
    assert r.is_optional == is_optional


def test_relation():
    g = tg.Graph()
    g.add_table('a', None)
    g.add_table('b', None)
    g.join('a', 'b', 'inner', 'key')

    rel = g.relation('a', 'b')
    assert rel.left == 'a'
    assert rel.right == 'b'

    with pytest.raises(KeyError):
        g.relation('b', 'a')


def test_edge():
    g = tg.Graph()
    g.add_table('a', None)
    g.add_table('b', None)
    g.join('a', 'b', 'inner', 'key')

    assert g.edge('a', 'b') == ('b', 'a')


def test_joined_tables():
    g = tg.Graph()
    g.add_table('a', None)
    g.add_table('b', None)
    g.add_table('c', None)

    g.join('a', 'b', 'inner', 'key')
    g.join('a', 'c', 'inner', 'key')

    assert set(g.joined_tables('a')) == {'b', 'c'}
    assert set(g.joined_tables('b')) == set()
