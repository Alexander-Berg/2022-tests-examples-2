import pytest

from replication.utils import inspect_ext


class _Info:
    def __init__(self, key_a, key_b, key_c=None, key_d='d'):
        self.doc = {
            'key_a': key_a,
            'key_b': key_b,
            'key_c': key_c,
            'key_d': key_d,
        }


@pytest.mark.parametrize(
    'kwargs,error,expected',
    [
        (
            {'key_a': 1, 'key_b': 2},
            None,
            {'key_a': 1, 'key_b': 2, 'key_c': None, 'key_d': 'd'},
        ),
        (
            {'key_a': 1, 'key_b': 2, 'key_c': 'c2', 'key_d': 'd2'},
            None,
            {'key_a': 1, 'key_b': 2, 'key_c': 'c2', 'key_d': 'd2'},
        ),
        (
            {'key_a': 1, 'key_b': 2, 'key_d': 'd2'},
            None,
            {'key_a': 1, 'key_b': 2, 'key_c': None, 'key_d': 'd2'},
        ),
        ({'key_a': 1}, inspect_ext.CannotInitError, None),
        (
            {'key_a': 1, 'key_c': 'c2', 'key_d': 'd2'},
            inspect_ext.CannotInitError,
            None,
        ),
    ],
)
@pytest.mark.nofilldb()
def test_init(kwargs, error, expected):
    if error:
        with pytest.raises(error):
            inspect_ext.init('', _Info, kwargs)
    else:
        meta = inspect_ext.init('', _Info, kwargs)
        assert meta.doc == expected
