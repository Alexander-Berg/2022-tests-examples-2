import pytest
from core.deserialize_utils import split_escaping_items, array, smart_strip_escaping


@pytest.mark.parametrize('sep, value, expected', [
    (',', [], []),
    (',', ['1, 2,",","{""1"",""2""}",NULL,""""""'], ['1', ' 2', '","', '"{""1"",""2""}"', 'NULL', '""""""']),
    ('\n', ['1, 2,",","{""1"",""2""}",NULL,""""""\n'], ['1, 2,",","{""1"",""2""}",NULL,""""""']),
    ('\n', ['1\n', '2\n3', '\n4\n'], ['1', '2', '3', '4']),
    ('\n', ['1\t2\n', '11\t"2\n2', '"\n', '\t"33\n"\n'], ['1\t2', '11\t"2\n2"', '\t"33\n"'])
])
def test_split_escaping_items(sep, value, expected):
    assert list(split_escaping_items(value, sep=sep)) == expected


@pytest.mark.parametrize('func, val, expected', [
    [int, '{1,2,NULL}', [1, 2, None]],
    [None, '{,"1,2","2,2","""",NULL}', ['', '1,2', '2,2', '"', None]],
    [None, '{ "1", 2}', [' "1"', ' 2']],  # неожиданное поведение при наличие пробелов
])
def test_array(func, val, expected):
    assert list(array(func)(val)) == expected


@pytest.mark.parametrize('val, expected', [
    [['1', '"2,3"', '""', '"4 "" 5"'], ['1', '2,3', '', '4 " 5']],
    [['" \"\"\" "'],  [' "" ']],
]
)
def test_smart_strip_escaping(val, expected):
    assert list(smart_strip_escaping(val)) == expected
