# pylint: disable=protected-access,invalid-name,redefined-outer-name

import itertools

import pytest

from crm_admin.quicksegment import filter_tree as ft
from crm_admin.quicksegment import select_expr_parser as projection_parser
from crm_admin.quicksegment import simplify as simp
from crm_admin.quicksegment import sqlike_generator as generator
from crm_admin.quicksegment import sqlike_parser as parser


def build_tree_from_chain(head, tail):
    if tail:
        head.operands.append(
            build_tree_from_chain(ft.Operator(tail[0], []), tail[1:]),
        )
    return head


def parse_sqlike(query):
    return parser.parse(query)


def gen_sqlike(ir):
    return generator.generate(ir)


@pytest.mark.parametrize(
    'chain',
    [
        (['add']),
        (['add', 'add']),
        (['or', 'or']),
        (['add', 'add']),
        (['sub', 'sub']),
        (['mul', 'mul']),
        (['div', 'div']),
        (['div', 'div', 'div']),
        (['div', 'div', 'mul', 'div']),
    ],
)
def test_collapse_chains(chain):
    tree = build_tree_from_chain(ft.Operator(chain[0], []), chain[1:])
    simplified_tree = simp.remove_parentheses(tree)

    collapsed_chain = [op for op, _ in itertools.groupby(chain)]
    expected_tree = build_tree_from_chain(
        ft.Operator(collapsed_chain[0], []), collapsed_chain[1:],
    )

    assert simplified_tree == expected_tree


@pytest.mark.parametrize(
    'chain',
    [(['eq', 'eq']), (['mod', 'mod']), (['like', 'like']), (['not', 'not'])],
)
def test_never_collapse_chains(chain):
    tree = build_tree_from_chain(ft.Operator(chain[0], []), chain[1:])
    simplified_tree = simp.remove_parentheses(tree)

    expected_tree = build_tree_from_chain(ft.Operator(chain[0], []), chain[1:])
    assert simplified_tree == expected_tree


@pytest.mark.parametrize(
    'expr, result, parser',
    [
        (
            'a and (b and ((c or d) and e))',
            'a and b and (c or d) and e',
            parser,
        ),
        (
            'a[b and (c and d)] as a',
            'a[b and c and d] as a',
            projection_parser,
        ),
    ],
)
def test_collapse(expr, result, parser):
    tree = parser.parse(expr)
    simplified_tree = simp.remove_parentheses(tree)
    simplified_expr = gen_sqlike(simplified_tree)

    assert simplified_expr == result


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('false and false', 'false'),
        ('true and true', 'true'),
        ('true and col', 'col'),
        ('col and true', 'col'),
        ('col and false', 'false'),
        ('false and col', 'false'),
        ('col_a and (true and col_b)', 'col_a and col_b'),
        ('col_a and (false and col_b)', 'false'),
        ('col_a and col_b', 'col_a and col_b'),
    ],
)
def test_evaluate_and(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('false or false', 'false'),
        ('true or true', 'true'),
        ('true or col', 'true'),
        ('col or true', 'true'),
        ('col or false', 'col'),
        ('false or col', 'col'),
        ('col_a or (true or col_b)', 'true'),
        ('col_a or (false or col_b)', 'col_a or col_b'),
        ('col_a or col_b', 'col_a or col_b'),
    ],
)
def test_evaluate_or(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('not false', 'true'),
        ('not true', 'false'),
        ('not not true', 'true'),
        ('not not false', 'false'),
        ('not col', 'not col'),
    ],
)
def test_evaluate_not(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('null is null', 'true'),
        ('null is not null', 'false'),
        ('1 is null', 'false'),
        ('1 is not null', 'true'),
        ('col is null', 'col is null'),
        ('col is not null', 'col is not null'),
    ],
)
def test_evaluate_nulltest(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('1 = 1', 'true'),
        ('1 != 1', 'false'),
        ('1 = 2', 'false'),
        ('1 != 2', 'true'),
        ('"string" = "string"', 'true'),
        ('"string" != "string"', 'false'),
        ('"one" = "two"', 'false'),
        ('"one" != "two"', 'true'),
    ],
)
def test_evaluate_eq(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('1 in (1, 2)', 'true'),
        ('1 not in (1, 2)', 'false'),
        ('3 in (1, 2)', 'false'),
        ('3 not in (1, 2)', 'true'),
        ('val in (1, 2)', 'val in (1, 2)'),
        ('val not in (1, 2)', 'val not in (1, 2)'),
        ('1 in ${var}', '1 in ${var}'),
    ],
)
def test_evaluate_in(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('1 + 1', '2'),
        ('1 - 1', '0'),
        ('4 * 2', '8'),
        ('4 / 2', '2.0'),
        ('-1', '-1'),
        ('-(-1)', '1'),
        ('+1', '1'),
        ('1 + ${var}', '1 + ${var}'),
    ],
)
def test_evaluate_arithmetic_ops(expr, expected):
    ir = parse_sqlike(expr)
    simplified = simp.evaluate(ir)
    assert gen_sqlike(simplified) == expected


@pytest.mark.parametrize(
    'tree, expected',
    [
        (ft.Operator('and', [ft.noop, ft.noop]), ft.noop),
        (
            ft.Operator('and', [ft.Variable('var'), ft.noop]),
            ft.Variable('var'),
        ),
        (ft.Operator('and', [ft.Constant(True), ft.noop]), ft.Constant(True)),
        (ft.Operator('or', [ft.noop, ft.noop]), ft.noop),
        (ft.Operator('or', [ft.Variable('var'), ft.noop]), ft.Variable('var')),
        (ft.Operator('or', [ft.Constant(False), ft.noop]), ft.Constant(False)),
        (ft.Operator('add', [ft.Constant(1), ft.noop]), ft.noop),
        (ft.Operator('eq', [ft.Constant(1), ft.noop]), ft.noop),
        (ft.Operator('not', [ft.noop]), ft.noop),
        (ft.FuncCall('fn', [ft.noop]), ft.noop),
        (ft.List([ft.noop]), ft.noop),
    ],
)
def test_evaluate_noop(tree, expected):
    assert simp.evaluate(tree) == expected
