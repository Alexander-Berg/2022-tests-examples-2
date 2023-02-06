# pylint: disable=redefined-outer-name

import pytest

from crm_admin.quicksegment import filter_tree as ft
from crm_admin.quicksegment import sqlike_parser


def parse_sqlike(query):
    return sqlike_parser.parse(query)


def get_node_name(node):
    if node is None:
        return None
    try:
        return node.name
    except AttributeError:
        return node.value


@pytest.fixture
def expression():
    return parse_sqlike('col_a > 1 and (col_b < ${val_b} or col_c is null)')


@pytest.fixture
def traverse_path():
    return [
        (None, 'and'),
        ('and', 'gt'),
        ('gt', 'col_a'),
        ('gt', 1),
        ('and', 'or'),
        ('or', 'lt'),
        ('lt', 'col_b'),
        ('lt', 'val_b'),
        ('or', 'isnull'),
        ('isnull', 'col_c'),
    ]


def test_visit(expression, traverse_path):
    path = []

    def visitor(node):
        path.append(get_node_name(node))

    ft.visit(expression, visitor)

    assert path == [item[1] for item in traverse_path]


def test_visit_with_parent(expression, traverse_path):
    path = []

    def visitor(parent, node):
        path.append((get_node_name(parent), get_node_name(node)))

    ft.visit(expression, visitor)

    assert path == traverse_path


def test_visit_return_value(expression, traverse_path):
    def visitor(node):
        return ft.Constant('val')

    clause = ft.Variable('var')
    clause = ft.visit(clause, visitor)
    assert clause == ft.Constant('val')


def test_visit_gen(expression, traverse_path):
    def visitor(node):
        yield get_node_name(node)

    path = ft.visit_gen(expression, visitor)

    assert list(path) == [item[1] for item in traverse_path]


def test_visit_gen_with_parent(expression, traverse_path):
    def visitor(parent, node):
        yield get_node_name(parent), get_node_name(node)

    path = ft.visit_gen(expression, visitor)

    assert list(path) == traverse_path


def test_children(expression):
    assert expression.children()[0].name == 'gt'
    assert expression.children()[1].name == 'or'


def test_child_index(expression):
    for i, child in enumerate(expression.children()):
        assert expression.child_index(child) == i


def test_replace_child(expression):
    true = ft.Constant(True)
    false = ft.Constant(False)
    expression.replace_child(expression.children()[0], true)
    expression.replace_child(expression.children()[1], false)

    assert expression.children()[0].value is True
    assert expression.children()[1].value is False
