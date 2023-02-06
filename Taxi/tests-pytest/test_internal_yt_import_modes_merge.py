import pytest

from taxi.internal.yt_import.modes import merge


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('prev_mapped_row,mapped_row,expected', [
    (None, {'_id': 'foo', 'field': 'bar'}, True),
    ({'_id': 'foo', 'field': 'baz'}, {'_id': 'bar', 'field': 'quux'}, True),
    ({'_id': 'foo', 'field': 'baz'}, {'_id': 'foo', 'field': 'baz'}, False),
    ({'_id': 'foo', 'field': 'baz'}, {'_id': 'foo', 'field': 'quux'}, False),
])
def test_check_yt_duplicates(prev_mapped_row, mapped_row, expected):
    result = merge._check_yt_duplicates(prev_mapped_row, mapped_row)
    assert result == expected
