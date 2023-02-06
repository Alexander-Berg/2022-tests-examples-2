import pytest

from crm_admin.quicksegment import select_expr_parser
from crm_admin.quicksegment import sqlike_generator
from crm_admin.quicksegment import sqlike_parser


def parse_sqlike(query):
    return sqlike_parser.parse(query)


def parse_col_expr(query):
    return select_expr_parser.parse(query)


@pytest.mark.parametrize(
    'expr',
    [
        '1',
        '-1',
        '1.5',
        '-1.5',
        'true',
        'false',
        'none',
        '"string"',
        'col',
        'table.col',
        '${var}',
        '${#var}',
        '${group.var}',
        '${#group.var}',
        '${{group.var}}',
        '${{#group.var}}',
        '%{filter_id}',
        'fn()',
        'fn(arg)',
        'fn(arg1, arg2)',
        'col[1]',
        'col is null',
        'col is not null',
        '-col',
        'col + col',
        'col and col',
        'not col',
        'col in ${var}',
        'col in ()',
        'col in (1)',
        'col in (1, 2)',
        'col not in ${var}',
        'col not in ()',
        'col not in (1)',
        'col not in (1, 2)',
        'col like ${var}',
        'col not like ${var}',
        '1 - (1 + 1)',
        '(1 - 1) + 1',
        '1 + (-1)',
        '1 * (-1)',
    ],
)
def test_generator(expr):
    tree = parse_sqlike(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr, expected', [('"string"', '"string"'), ('\'string\'', '"string"')],
)
def test_string_const_generator(expr, expected):
    tree = parse_sqlike(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expected


@pytest.mark.parametrize(
    'expr', ['cast("123" as int)', 'cast(fn(col) as bool)'],
)
def test_cast_generator(expr):
    tree = parse_sqlike(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr',
    [
        'col',
        'col as alias',
        'fn(col) as alias',
        'cast(col as string) as alias',
        'table.col as col',
        '*',
        'table.*',
    ],
)
def test_col_expr_generator(expr):
    tree = parse_col_expr(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr',
    ['col[0]', '${var}[1]', 'col["key"]', 'map("key", "value")["key"]'],
)
def test_getitem(expr):
    tree = parse_sqlike(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr', ['fn()', 'fn(col)', 'fn(col, ${var})', 'fn1(fn2())'],
)
def test_func_call(expr):
    tree = parse_sqlike(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr',
    [
        (
            'case when condition1 then body1 when condition2 then body2 '
            'else otherwise end as alias'
        ),
        'case when condition then body end as alias',
    ],
)
def test_cases(expr):
    tree = parse_col_expr(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expr


@pytest.mark.parametrize(
    'expr, parser, expected',
    [
        ('col->key', parse_sqlike, 'col.key'),
        ('table.col->key', parse_sqlike, 'table.col.key'),
        ('table.col->key->subkey', parse_sqlike, 'table.col.key.subkey'),
        ('col->key as key', parse_col_expr, 'col.key as key'),
        ('table.col->key as key', parse_col_expr, 'table.col.key as key'),
    ],
)
def test_obj_path(expr, parser, expected):
    tree = parser(expr)
    generated = sqlike_generator.generate(tree)
    assert generated == expected
