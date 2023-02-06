# pylint: disable=invalid-name

import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import filter_tree as ft
from crm_admin.quicksegment import sqlike_parser


@pytest.mark.parametrize(
    'expr, value',
    [
        ('\'string\'', 'string'),
        ('"string"', 'string'),
        ('1', 1),
        ('-1', -1),
        ('1.1', 1.1),
        ('-1.1', -1.1),
        ('true', True),
        ('false', False),
        ('null', None),
    ],
)
def test_consts(expr, value):
    tree = sqlike_parser.parse(expr)
    assert tree == ft.Constant(value)


@pytest.mark.parametrize(
    'expr, func_name, nargs',
    [
        ('func()', 'func', 0),
        ('func(arg)', 'func', 1),
        ('func(arg1, arg2)', 'func', 2),
        ('func(arg1 + arg2)', 'func', 1),
    ],
)
def test_func_call(expr, func_name, nargs):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.FuncCall)
    assert tree.name == func_name
    assert len(tree.arglist) == nargs


@pytest.mark.parametrize(
    'expr, index',
    [('table.col[1]', 1), ('fn()[1]', 1), ('col["key"]', 'key')],
)
def test_getitem(expr, index):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.GetItem)
    assert isinstance(tree.obj, ft.Node)
    assert isinstance(tree.index, ft.Node)


@pytest.mark.parametrize(
    'expr, name, node_type',
    [
        ('${var}', 'var', ft.Variable),
        ('${a.b.c}', 'a.b.c', ft.Variable),
        ('${#a.b.c}', 'a.b.c', ft.VariableSize),
        ('${{a.b.c}}', 'a.b.c', ft.TemplateVariable),
        ('${{#a.b.c}}', 'a.b.c', ft.TemplateVariableSize),
    ],
)
def test_variables(expr, name, node_type):
    tree = sqlike_parser.parse(expr)
    assert tree == node_type(name)


@pytest.mark.parametrize(
    'expr, name', [('col', 'col'), ('table.col', 'table.col')],
)
def test_column(expr, name):
    tree = sqlike_parser.parse(expr)
    assert tree == ft.Column(name)


@pytest.mark.parametrize(
    'expr, node_type',
    [
        ('col->a', ft.ObjPath),
        ('col[0]->a', ft.ObjPath),
        ('col->a->b', ft.ObjPath),
        ('table.col->a->b', ft.ObjPath),
        ('-col->a', ft.Operator),
        ('col->a + col->b', ft.Operator),
    ],
)
def test_obj_path(expr, node_type):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, node_type)


@pytest.mark.parametrize('expr, name', [('%{filter-id}', 'filter-id')])
def test_filter_id(expr, name):
    tree = sqlike_parser.parse(expr)
    assert tree == ft.FilterId(name)


@pytest.mark.parametrize(
    'expr, name',
    [
        ('- table.col', 'minus'),
        ('- fn()', 'minus'),
        ('+ table.col', 'plus'),
        ('+ fn()', 'plus'),
    ],
)
def test_unary_ops(expr, name):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.Operator)
    assert tree.name == name
    assert len(tree.operands) == 1


@pytest.mark.parametrize(
    'expr, name',
    [
        ('col1 / col2', 'div'),
        ('col1 * col2', 'mul'),
        ('col1 % col2', 'mod'),
        ('col1 + col2', 'add'),
        ('col1 - col2', 'sub'),
        ('col1 = col2', 'eq'),
        ('col1 != col2', 'ne'),
        ('col1 < col2', 'lt'),
        ('col1 <= col2', 'le'),
        ('col1 > col2', 'gt'),
        ('col1 >= col2', 'ge'),
        ('col1 like col2', 'like'),
        ('col1 not like col2', 'notlike'),
        ('col1 in col2', 'in'),
        ('col1 not in col2', 'notin'),
        ('col1 and col2', 'and'),
        ('col1 or col2', 'or'),
    ],
)
def test_binary_ops(expr, name):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.Operator)
    assert tree.name == name
    assert len(tree.operands) == 2


@pytest.mark.parametrize(
    'expr, name', [('col is null', 'isnull'), ('col is not null', 'notnull')],
)
def test_nul(expr, name):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.Operator)
    assert tree.name == name
    assert len(tree.operands) == 1


@pytest.mark.parametrize('expr, name', [('not col', 'not')])
def test_not(expr, name):
    tree = sqlike_parser.parse(expr)
    assert isinstance(tree, ft.Operator)
    assert tree.name == name
    assert len(tree.operands) == 1


@pytest.mark.parametrize(
    'expr, root',
    [
        ('- a * b', 'mul'),
        ('a * b + c', 'add'),
        ('a + b is null ', 'isnull'),
        ('a is null in b ', 'in'),
        ('a = b in c ', 'eq'),
        ('not a = b', 'not'),
        ('not a and b', 'and'),
        ('a and b or c', 'or'),
    ],
)
def test_operator_precedence(expr, root):
    tree = sqlike_parser.parse(expr)
    assert tree.name == root


@pytest.mark.parametrize(
    'expr, is_valid',
    [
        ('', False),
        ('()', False),
        ('a', True),
        ('(a)', True),
        ('1 + 1 - 1', True),
        ('1 * 1 / 1', True),
    ],
)
def test_expr(expr, is_valid):
    if not is_valid:
        with pytest.raises(error.ParseError):
            sqlike_parser.parse(expr)
    else:
        sqlike_parser.parse(expr)


def test_cast():
    tree = sqlike_parser.parse('cast(col as int)')
    assert isinstance(tree, ft.Cast)
    assert isinstance(tree.args[0], ft.Column)
    assert isinstance(tree.args[1], ft.Typename)


@pytest.mark.parametrize(
    'query, op',
    [
        ('col in (1, 2, 3)', 'in'),
        ('col in ${var}', 'in'),
        ('col not in (1, 2, 3)', 'notin'),
        ('col not in ${var}', 'notin'),
    ],
)
def test_isin(query, op):
    ir = sqlike_parser.parse(query)

    assert isinstance(ir, ft.Operator)
    assert ir.name == op
    assert len(ir.operands) == 2


@pytest.mark.parametrize(
    'query, items',
    [
        ('col in (1, 2, 3)', [1, 2, 3]),
        ('col in ()', []),
        ('col not in (1, 2, 3)', [1, 2, 3]),
        ('col not in ()', []),
    ],
)
def test_list(query, items):
    ir = sqlike_parser.parse(query)
    assert isinstance(ir.operands[1], ft.List)
    assert len(ir.operands[1].items) == len(items)
    for item, expected in zip(ir.operands[1].items, items):
        assert isinstance(item, ft.Constant)
        assert item.value == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('1 - 1 - 1', '(1 - 1) - 1'),
        ('1 + 1 + 1', '(1 + 1) + 1'),
        ('1 + 1 - 1', '(1 + 1) - 1'),
        ('1 - 1 + 1', '(1 - 1) + 1'),
        ('1 + 1 - 1 + 1', '((1 + 1) - 1) + 1'),
        ('1 * 1 + 1', '(1 * 1) + 1'),
        ('1 + 1 * 1', '1 + (1 * 1)'),
        ('1 / 1 / 1', '(1 / 1) / 1'),
    ],
)
def test_arithmetics(expr, expected):
    parsed = sqlike_parser.parse(expr)
    expected_tree = sqlike_parser.parse(expected)
    assert parsed == expected_tree
