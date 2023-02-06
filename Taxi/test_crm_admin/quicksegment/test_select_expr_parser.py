import pytest

from crm_admin.quicksegment import filter_tree as ft
from crm_admin.quicksegment.select_expr_parser import (
    Parser,
)  # pylint: disable-all


@pytest.mark.parametrize(
    'expr, expr_type, alias',
    [
        ('fn(fn(), col + 1) as alias', ft.FuncCall, 'alias'),
        ('col', ft.Column, 'col'),
        ('table.col', ft.Column, 'col'),
        ('table.col->key as alias', ft.ObjPath, 'alias'),
        ('col as alias', ft.Column, 'alias'),
        ('col->key as alias', ft.ObjPath, 'alias'),
        ('fn(col) as alias', ft.FuncCall, 'alias'),
        ('fn(fn(col)) as alias', ft.FuncCall, 'alias'),
        ('cast(col as string) as alias', ft.Cast, 'alias'),
        ('not col as alias', ft.Operator, 'alias'),
        ('cast(not col as string) as alias', ft.Cast, 'alias'),
        ('map("key", "value")["key"] as alias', ft.GetItem, 'alias'),
        ('col[1] as alias', ft.GetItem, 'alias'),
        ('col["key"] as alias', ft.GetItem, 'alias'),
        ('col[i + 1] as alias', ft.GetItem, 'alias'),
        ('col1 + col2 as alias', ft.Operator, 'alias'),
        ('col1 in ("a", "b") as alias', ft.Operator, 'alias'),
        ('${var} as alias', ft.Variable, 'alias'),
        ('${#var} as alias', ft.VariableSize, 'alias'),
    ],
)
def test_col_expr(expr, expr_type, alias):
    parser = Parser()
    tree = parser.parse(expr)

    assert isinstance(tree, ft.ColExpr)
    assert isinstance(tree.expr, expr_type)
    if alias:
        assert tree.alias == alias
    else:
        assert tree.alias is None


@pytest.mark.parametrize('expr', ['*', 'table.*'])
def test_star_expr(expr):
    parser = Parser()
    tree = parser.parse(expr)

    assert isinstance(tree, ft.StarExpr)
    assert tree.value == expr


@pytest.mark.parametrize(
    'expr',
    [
        """
            case
                when condition1 then body1
                when condition2 then body2
                else otherwise
            end as alias
        """,
        """
            case
                when condition then body
            end as alias
        """,
    ],
)
def test_cases(expr):
    parser = Parser()
    tree = parser.parse(expr)

    cases = tree.children()[0]
    assert isinstance(cases, ft.CaseExpr)
    assert isinstance(cases.cases[0], ft.CaseExprWhen)
    if cases.otherwise is not None:
        assert isinstance(cases.otherwise, ft.CaseExprElse)


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('1 - 1 - 1 as c', '(1 - 1) - 1 as c'),
        ('1 + 1 + 1 as c', '(1 + 1) + 1 as c'),
        ('1 + 1 - 1 as c', '(1 + 1) - 1 as c'),
        ('1 - 1 + 1 as c', '(1 - 1) + 1 as c'),
        ('1 + 1 - 1 + 1 as c', '((1 + 1) - 1) + 1 as c'),
        ('1 * 1 + 1 as c', '(1 * 1) + 1 as c'),
        ('1 + 1 * 1 as c', '1 + (1 * 1) as c'),
        ('1 / 1 / 1 as c', '(1 / 1) / 1 as c'),
    ],
)
def test_arithmetics(expr, expected):
    parser = Parser()

    parsed = parser.parse(expr)
    expected_tree = parser.parse(expected)
    assert parsed == expected_tree
