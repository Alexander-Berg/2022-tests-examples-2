import pytest

from taxi.util import dictionary


@pytest.mark.parametrize(
    'dicts, result, error_msg',
    (
        ((None, {'a': 'b', 'c': 'd'}), {'a': 'b', 'c': 'd'}, None),
        (
            (None, {'a': 'b', 'c': 'd'}, {'x': 'y', 'z': 'A'}),
            {'a': 'b', 'c': 'd', 'x': 'y', 'z': 'A'},
            None,
        ),
        (
            (None, {'a': 'b', 'c': 'd'}, {'a': 'b', 'x': 'y'}),
            {'a': 'b', 'c': 'd', 'x': 'y'},
            None,
        ),
        (
            (None, {'a': 'b', 'c': 'd'}, {'a': 'e'}),
            None,
            'merge conflict on key: \'a\'',
        ),
    ),
)
def test_shallow_merge(dicts, result, error_msg):
    if error_msg:
        with pytest.raises(ValueError) as exc_info:
            dictionary.shallow_merge(dicts)

        assert exc_info.value.args == (error_msg,)
    else:
        assert result == dictionary.shallow_merge(dicts)
