# pylint: disable=W0212
import pytest

from taxi.util import rst


FULL_TABLE = """
+--------+--------+--------+
| h1     | h2     | h3     |
+========+========+========+
| r11    | r12    | r13    |
+--------+--------+--------+
| r21    | r22    | r23    |
+--------+--------+--------+
"""


@pytest.mark.parametrize(
    ['items', 'symbol', 'expected'],
    [
        pytest.param([1, 2, 3], '*', '* 1\n* 2\n* 3', id='items_int'),
        pytest.param(['1', '2', '3'], '*', '* 1\n* 2\n* 3', id='items_str'),
        pytest.param(['1', 2, '3'], '*', '* 1\n* 2\n* 3', id='items_mixed'),
        pytest.param([1, 2, 3], None, '* 1\n* 2\n* 3', id='symbol_none'),
        pytest.param([1, 2, 3], '+', '+ 1\n+ 2\n+ 3', id='symbol_diff'),
        pytest.param([1, 2, 3], '+=', '+= 1\n+= 2\n+= 3', id='two_symbols'),
    ],
)
def test_create_list(items, symbol, expected):
    args = [items]
    if symbol is not None:
        args.append(symbol)
    assert rst.create_list(*args) == expected


@pytest.mark.parametrize(
    ['widths', 'symbol', 'expected'],
    [
        pytest.param([0], '*', '++\n', id='single_item_zero'),
        pytest.param([0, 0], None, '+++\n', id='multiple_items_zero'),
        pytest.param([2], '*', '+**+\n', id='single_non_zero'),
        pytest.param([1, 2, 3], '*', '+*+**+***+\n', id='multiple_non_zero'),
        pytest.param(
            [1, 2, 3], None, '+-+--+---+\n', id='multiple_symbol_diff',
        ),
        pytest.param(
            [1, 2, 3], '**', '+**+****+******+\n', id='multiple_symbols',
        ),
    ],
)
def test_create_table_line(widths, symbol, expected):
    args = [widths]
    if symbol is not None:
        args.append(symbol)
    assert rst._create_table_line(*args) == expected


@pytest.mark.parametrize(
    ['widths', 'content', 'expected'],
    [
        pytest.param(
            [0, 0],
            ['test1', 'test2'],
            '| test1 | test2 |\n',
            id='widths_lesser',
        ),
        pytest.param(
            [5, 5],
            ['test1', 'test2'],
            '| test1 | test2 |\n',
            id='widths_equals',
        ),
        pytest.param(
            [8, 8],
            ['test1', 'test2'],
            '| test1  | test2  |\n',
            id='widths_bit_more',
        ),
        pytest.param(
            [10, 10],
            ['test1', 'test2'],
            '| test1    | test2    |\n',
            id='widths_much_more',
        ),
        pytest.param(
            [1, 10],
            ['test1', 'test2'],
            '| test1 | test2    |\n',
            id='left_less_right_more',
        ),
        pytest.param(
            [10, 1],
            ['test1', 'test2'],
            '| test1    | test2 |\n',
            id='left_more_right_less',
        ),
    ],
)
def test_create_table_content_line(widths, content, expected):
    assert rst._create_table_content_line(widths, content) == expected


@pytest.mark.parametrize(
    ['headers', 'rows', 'expected'],
    [
        pytest.param(
            ['h1', 'h2', 'h3'],
            [['r11', 'r12', 'r13'], ['r21', 'r22', 'r23']],
            FULL_TABLE.lstrip('\n'),
            id='full_table_ok',
        ),
    ],
)
def test_create_table(headers, rows, expected):
    assert rst.create_table(headers, rows) == expected


@pytest.mark.parametrize(
    ['title', 'level', 'expected'],
    [
        pytest.param(
            'test', rst.HeadingLevel.ONE, '****\ntest\n****', id='heading_1',
        ),
        pytest.param(
            'test', rst.HeadingLevel.TWO, '####\ntest\n####', id='heading_2',
        ),
        pytest.param(
            'test', rst.HeadingLevel.THREE, '====\ntest\n====', id='heading_3',
        ),
        pytest.param(
            'test', rst.HeadingLevel.FOUR, '----\ntest\n----', id='heading_4',
        ),
        pytest.param(
            'test', rst.HeadingLevel.FIVE, '^^^^\ntest\n^^^^', id='heading_5',
        ),
        pytest.param(
            'test', rst.HeadingLevel.SIX, '""""\ntest\n""""', id='heading_6',
        ),
    ],
)
def test_create_heading(title, level, expected):
    assert rst.create_heading(title, level) == expected


@pytest.mark.parametrize(
    ['link', 'name', 'expected'],
    [
        pytest.param(
            'http://some_link',
            'some_name',
            '`some_name <http://some_link>`_',
            id='link_and_name',
        ),
        pytest.param(
            'http://some_link',
            None,
            '`http://some_link <http://some_link>`_',
            id='only_link',
        ),
    ],
)
def test_create_external_link(link, name, expected):
    assert rst.create_external_link(link, name) == expected
