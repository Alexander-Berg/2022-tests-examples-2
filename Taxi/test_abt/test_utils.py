import pytest


from abt.utils import collections as collections_utils
from abt.utils import sphinx as sphinx_utils


@pytest.mark.parametrize(
    ['input_string', 'expected'],
    [
        pytest.param('', '', id='empty_string'),
        pytest.param('qwe', 'qwe', id='normal_string'),
        pytest.param('qwe-asd', 'qwe-asd', id='string_with_hyphen'),
        pytest.param('qwe_asd', 'qwe-asd', id='string_with_underscore'),
        pytest.param('qwe__asd', 'qwe-asd', id='string_with_seq_underscores'),
        pytest.param('qwe__asd_zxc', 'qwe-asd-zxc', id='double_and_single'),
        pytest.param('qwe__asd__zxc', 'qwe-asd-zxc', id='two_doubles'),
        pytest.param('aaa_bbb__ccc', 'aaa-bbb-ccc', id='seq_chars'),
        pytest.param('aaa_B__ccc', 'aaa-b-ccc', id='upper_case_to_lower'),
    ],
)
def test_metric_name_transform(input_string, expected):
    assert sphinx_utils.to_anchor_string(input_string) == expected


@pytest.mark.parametrize(
    ['collection', 'expected'],
    [
        pytest.param([1, 2, 3], [], id='no duplicates'),
        pytest.param(
            [1, 1, 2, 3], [1], id='one occurrence of duplicated value',
        ),
        pytest.param(
            [1, 2, 2, 2, 3], [2], id='several occurrences of duplicated value',
        ),
    ],
)
def test_find_duplicates(collection, expected):
    assert sorted(collections_utils.find_duplicates(collection)) == sorted(
        expected,
    )
